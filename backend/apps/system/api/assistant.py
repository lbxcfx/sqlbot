from datetime import timedelta
import json
import os
from typing import List, Optional
from fastapi import APIRouter, Form, HTTPException, Query, Request, Response, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import select
from apps.system.crud.assistant import get_assistant_info
from apps.system.crud.assistant_manage import dynamic_upgrade_cors, save
from apps.system.models.system_model import AssistantModel
from apps.system.schemas.auth import CacheName, CacheNamespace
from apps.system.schemas.system_schema import AssistantBase, AssistantDTO, AssistantUiSchema, AssistantValidator
from common.core.deps import SessionDep, Trans
from common.core.security import create_access_token
from common.core.sqlbot_cache import clear_cache
from common.utils.time import get_timestamp

from common.core.config import settings
from common.utils.utils import get_origin_from_referer

# 开源版本：实现简单的文件工具类
try:
    from sqlbot_xpack.file_utils import SQLBotFileUtils
    XPACK_AVAILABLE = True
except ImportError:
    XPACK_AVAILABLE = False
    import uuid
    import os
    import shutil
    from fastapi import UploadFile
    from pathlib import Path

    class SQLBotFileUtils:
        """开源版本的文件工具类"""
        # 文件存储目录
        UPLOAD_DIR = Path(settings.MCP_IMAGE_PATH) / "uploads"

        @classmethod
        def _ensure_upload_dir(cls):
            """确保上传目录存在"""
            cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        @classmethod
        def get_file_path(cls, file_id: str) -> str:
            """获取文件路径"""
            cls._ensure_upload_dir()
            return str(cls.UPLOAD_DIR / file_id)

        @classmethod
        def split_filename_and_flag(cls, filename: str) -> tuple:
            """分割文件名和标志
            例如: logo_myfile.png -> (myfile.png, logo)
            """
            if '_' in filename:
                parts = filename.split('_', 1)
                return parts[1], parts[0]
            return filename, None

        @classmethod
        def check_file(cls, file: UploadFile, file_types: list, limit_file_size: int):
            """检查文件类型和大小"""
            # 检查文件类型
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_types and file_ext not in file_types:
                raise ValueError(f"File type {file_ext} not allowed. Allowed types: {file_types}")

            # 检查文件大小
            file.file.seek(0, 2)  # 移动到文件末尾
            file_size = file.file.tell()
            file.file.seek(0)  # 重置到文件开头

            if file_size > limit_file_size:
                raise ValueError(f"File size {file_size} exceeds limit {limit_file_size}")

        @classmethod
        async def upload(cls, file: UploadFile) -> str:
            """上传文件并返回文件 ID"""
            cls._ensure_upload_dir()

            # 生成唯一文件 ID
            file_ext = os.path.splitext(file.filename)[1]
            file_id = f"{uuid.uuid4()}{file_ext}"
            file_path = cls.UPLOAD_DIR / file_id

            # 保存文件
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)

            return file_id

        @classmethod
        def detete_file(cls, file_id: str):
            """删除文件"""
            if not file_id:
                return

            file_path = cls.UPLOAD_DIR / file_id
            if file_path.exists():
                try:
                    os.remove(file_path)
                except Exception:
                    pass  # 忽略删除失败

router = APIRouter(tags=["system/assistant"], prefix="/system/assistant")

@router.get("/info/{id}") 
async def info(request: Request, response: Response, session: SessionDep, trans: Trans, id: int) -> AssistantModel:
    if not id:
        raise Exception('miss assistant id')
    db_model = await get_assistant_info(session=session, assistant_id=id)
    if not db_model:
        raise RuntimeError(f"assistant application not exist")
    db_model = AssistantModel.model_validate(db_model)
    response.headers["Access-Control-Allow-Origin"] = db_model.domain
    origin = request.headers.get("origin") or get_origin_from_referer(request)
    if not origin:
        raise RuntimeError(trans('i18n_embedded.invalid_origin', origin = origin or ''))
    origin = origin.rstrip('/')
    if origin != db_model.domain:
        raise RuntimeError(trans('i18n_embedded.invalid_origin', origin = origin or ''))
    return db_model

@router.get("/app/{appId}") 
async def getApp(request: Request, response: Response, session: SessionDep, trans: Trans, appId: str) -> AssistantModel:
    if not appId:
        raise Exception('miss assistant appId')
    db_model = session.exec(select(AssistantModel).where(AssistantModel.app_id == appId)).first()
    if not db_model:
        raise RuntimeError(f"assistant application not exist")
    db_model = AssistantModel.model_validate(db_model)
    response.headers["Access-Control-Allow-Origin"] = db_model.domain
    origin = request.headers.get("origin") or get_origin_from_referer(request)
    if not origin:
        raise RuntimeError(trans('i18n_embedded.invalid_origin', origin = origin or ''))
    origin = origin.rstrip('/')
    if origin != db_model.domain:
        raise RuntimeError(trans('i18n_embedded.invalid_origin', origin = origin or ''))
    return db_model

@router.get("/validator", response_model=AssistantValidator) 
async def validator(session: SessionDep, id: int, virtual: Optional[int] = Query(None)):
    if not id:
        raise Exception('miss assistant id')
    
    db_model = await get_assistant_info(session=session, assistant_id=id)
    if not db_model:
        return AssistantValidator()
    db_model = AssistantModel.model_validate(db_model)
    assistant_oid = 1
    if(db_model.type == 0):
        configuration = db_model.configuration
        config_obj = json.loads(configuration) if configuration else {}
        assistant_oid = config_obj.get('oid', 1)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    assistantDict = {
        "id": virtual, "account": 'sqlbot-inner-assistant', "oid": assistant_oid, "assistant_id": id
    }
    access_token = create_access_token(
        assistantDict, expires_delta=access_token_expires
    )
    return AssistantValidator(True, True, True, access_token)
        
@router.get('/picture/{file_id}')
async def picture(file_id: str):
    file_path = SQLBotFileUtils.get_file_path(file_id=file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_id.lower().endswith(".svg"):
        media_type = "image/svg+xml"
    else:
        media_type = "image/jpeg"
    
    def iterfile():
        with open(file_path, mode="rb") as f:
            yield from f
    
    return StreamingResponse(iterfile(), media_type=media_type)

@router.patch('/ui')
async def ui(session: SessionDep, data: str = Form(), files: List[UploadFile] = []):
    json_data = json.loads(data)
    uiSchema = AssistantUiSchema(**json_data)
    id = uiSchema.id
    db_model = session.get(AssistantModel, id)
    if not db_model:
        raise ValueError(f"AssistantModel with id {id} not found")
    configuration = db_model.configuration
    config_obj = json.loads(configuration) if configuration else {}
    
    ui_schema_dict = uiSchema.model_dump(exclude_none=True, exclude_unset=True)
    if files:
        for file in files:
            origin_file_name = file.filename
            file_name, flag_name = SQLBotFileUtils.split_filename_and_flag(origin_file_name)
            file.filename = file_name
            if flag_name == 'logo' or flag_name == 'float_icon':
                SQLBotFileUtils.check_file(file=file, file_types=[".jpg", ".jpeg", ".png", ".svg"], limit_file_size=(10 * 1024 * 1024))
                if config_obj.get(flag_name):
                    SQLBotFileUtils.detete_file(config_obj.get(flag_name))
                file_id = await SQLBotFileUtils.upload(file)
                ui_schema_dict[flag_name] = file_id
            else:
                raise ValueError(f"Unsupported file flag: {flag_name}")
            
    for flag_name in ['logo', 'float_icon']:
        file_val = config_obj.get(flag_name)
        if file_val and not ui_schema_dict.get(flag_name):
            config_obj[flag_name] = None
            SQLBotFileUtils.detete_file(file_val)
            
    for attr, value in ui_schema_dict.items():
        if attr != 'id' and not attr.startswith("__"):
            config_obj[attr] = value
    
    db_model.configuration = json.dumps(config_obj, ensure_ascii=False)
    session.add(db_model)
    session.commit()
    await clear_ui_cache(db_model.id)

@clear_cache(namespace=CacheNamespace.EMBEDDED_INFO, cacheName=CacheName.ASSISTANT_INFO, keyExpression="id")  
async def clear_ui_cache(id: int):
    pass

@router.get("", response_model=list[AssistantModel])
async def query(session: SessionDep):
    list_result = session.exec(select(AssistantModel).where(AssistantModel.type != 4).order_by(AssistantModel.name, AssistantModel.create_time)).all()
    return list_result

@router.post("")
async def add(request: Request, session: SessionDep, creator: AssistantBase):
    await save(request, session, creator)

    
@router.put("")
@clear_cache(namespace=CacheNamespace.EMBEDDED_INFO, cacheName=CacheName.ASSISTANT_INFO, keyExpression="editor.id")  
async def update(request: Request, session: SessionDep, editor: AssistantDTO):
    id = editor.id
    db_model = session.get(AssistantModel, id)
    if not db_model:
        raise ValueError(f"AssistantModel with id {id} not found")
    update_data = AssistantModel.model_validate(editor)
    db_model.sqlmodel_update(update_data)
    session.add(db_model)
    session.commit()
    dynamic_upgrade_cors(request=request, session=session)

@router.get("/{id}", response_model=AssistantModel)    
async def get_one(session: SessionDep, id: int):
    db_model = await get_assistant_info(session=session, assistant_id=id)
    if not db_model:
        raise ValueError(f"AssistantModel with id {id} not found")
    db_model = AssistantModel.model_validate(db_model)
    return db_model

@router.delete("/{id}")
@clear_cache(namespace=CacheNamespace.EMBEDDED_INFO, cacheName=CacheName.ASSISTANT_INFO, keyExpression="id")  
async def delete(request: Request, session: SessionDep, id: int):
    db_model = session.get(AssistantModel, id)
    if not db_model:
        raise ValueError(f"AssistantModel with id {id} not found")
    session.delete(db_model)
    session.commit()
    dynamic_upgrade_cors(request=request, session=session)




        

    
