import json
from typing import List, Union

from fastapi.responses import StreamingResponse
from apps.ai_model.model_factory import LLMConfig, LLMFactory
from apps.system.schemas.ai_model_schema import AiModelConfigItem, AiModelCreator, AiModelEditor, AiModelGridItem
from fastapi import APIRouter, Query
from sqlmodel import func, select, update

from apps.system.models.system_model import AiModelDetail
from common.core.deps import SessionDep, Trans
from common.utils.crypto import sqlbot_decrypt
from common.utils.time import get_timestamp
from common.utils.utils import SQLBotLogUtil, prepare_model_arg

router = APIRouter(tags=["system/aimodel"], prefix="/system/aimodel")

@router.post("/status")
async def check_llm(info: AiModelCreator, trans: Trans):
    async def generate():
        try:
            additional_params = {item.key: prepare_model_arg(item.val) for item in info.config_list if item.key and item.val}
            config = LLMConfig(
                model_type="openai" if info.protocol == 1 else "vllm",
                model_name=info.base_model,
                api_key=info.api_key,
                api_base_url=info.api_domain,
                additional_params=additional_params,
            )
            llm_instance = LLMFactory.create_llm(config)
            async for chunk in llm_instance.llm.astream("1+1=?"):
                SQLBotLogUtil.info(chunk)
                if chunk and isinstance(chunk, str):
                    yield json.dumps({"content": chunk}) + "\n"
                if chunk and isinstance(chunk, dict) and chunk.content:
                    yield json.dumps({"content": chunk.content}) + "\n"
        
        except Exception as e:
            SQLBotLogUtil.error(f"Error checking LLM: {e}")
            error_msg = trans('i18n_llm.validate_error', msg=str(e))
            yield json.dumps({"error": error_msg}) + "\n"
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")

@router.get("/default")
async def check_default(session: SessionDep, trans: Trans):
    db_model = session.exec(
        select(AiModelDetail).where(AiModelDetail.default_model == True)
    ).first()
    if not db_model:
        raise Exception(trans('i18n_llm.miss_default'))
    
@router.put("/default/{id}")
async def set_default(session: SessionDep, id: int):
    db_model = session.get(AiModelDetail, id)
    if not db_model:
        raise ValueError(f"AiModelDetail with id {id} not found")
    if db_model.default_model:
        return

    try:
        session.exec(
            update(AiModelDetail).values(default_model=False)
        )
        db_model.default_model = True
        session.add(db_model)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

@router.get("", response_model=list[AiModelGridItem])
async def query(
        session: SessionDep,
        keyword: Union[str, None] = Query(default=None, max_length=255)
):
    statement = select(AiModelDetail.id, 
                       AiModelDetail.name, 
                       AiModelDetail.model_type, 
                       AiModelDetail.base_model, 
                       AiModelDetail.supplier,
                       AiModelDetail.protocol, 
                       AiModelDetail.default_model)
    if keyword is not None:
        statement = statement.where(AiModelDetail.name.like(f"%{keyword}%"))
    statement = statement.order_by(AiModelDetail.default_model.desc(), AiModelDetail.name, AiModelDetail.create_time)
    items = session.exec(statement).all()
    return items

@router.get("/{id}", response_model=AiModelEditor)
async def get_model_by_id(
        session: SessionDep,
        id: int
):
    db_model = session.get(AiModelDetail, id)
    if not db_model:
        raise ValueError(f"AiModelDetail with id {id} not found")

    config_list: List[AiModelConfigItem] = []
    if db_model.config:
        try:
            raw = json.loads(db_model.config)
            config_list = [AiModelConfigItem(**item) for item in raw]
        except Exception:
            pass
    if db_model.api_key:
        db_model.api_key = await sqlbot_decrypt(db_model.api_key)
    if db_model.api_domain:
        db_model.api_domain = await sqlbot_decrypt(db_model.api_domain)
    data = AiModelDetail.model_validate(db_model).model_dump(exclude_unset=True)
    data.pop("config", None)
    data["config_list"] = config_list
    return AiModelEditor(**data)

@router.post("")
async def add_model(
        session: SessionDep,
        creator: AiModelCreator
):
    data = creator.model_dump(exclude_unset=True)
    data["config"] = json.dumps([item.model_dump(exclude_unset=True) for item in creator.config_list])
    data.pop("config_list", None)
    detail = AiModelDetail.model_validate(data)
    detail.create_time = get_timestamp()
    count = session.exec(select(func.count(AiModelDetail.id))).one()
    if count == 0:
        detail.default_model = True
    session.add(detail)
    session.commit()

@router.put("")
async def update_model(
        session: SessionDep,
        editor: AiModelEditor
):
    id = int(editor.id)
    data = editor.model_dump(exclude_unset=True)
    data["config"] = json.dumps([item.model_dump(exclude_unset=True) for item in editor.config_list])
    data.pop("config_list", None)
    db_model = session.get(AiModelDetail, id)
    #update_data = AiModelDetail.model_validate(data)
    db_model.sqlmodel_update(data)
    session.add(db_model)
    session.commit()

@router.delete("/{id}")
async def delete_model(
        session: SessionDep,
        trans: Trans,
        id: int
):
    item = session.get(AiModelDetail, id)
    if item.default_model:
        raise Exception(trans('i18n_llm.delete_default_error', key = item.name))
    session.delete(item)
    session.commit()
    

    