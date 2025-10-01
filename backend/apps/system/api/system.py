from fastapi import APIRouter
from fastapi.responses import JSONResponse
from common.core.deps import SessionDep, Trans

router = APIRouter(tags=["system"], prefix="/system")

@router.get("/appearance/ui")
async def get_appearance_ui(session: SessionDep, trans: Trans):
    """获取外观UI配置 - 开源版本返回默认配置"""
    return {
        "theme": "light",
        "header_font_color": "#000000",
        "logo": "",
        "float_icon": "",
        "float_icon_drag": False,
        "x_type": "right",
        "x_val": 0,
        "y_type": "bottom", 
        "y_val": 33,
        "name": "SQLBot",
        "welcome": "欢迎使用SQLBot",
        "welcome_desc": "智能SQL助手，让数据库查询更简单"
    }

@router.patch("/appearance/ui")
async def update_appearance_ui(session: SessionDep, trans: Trans, data: dict):
    """更新外观UI配置 - 开源版本仅返回成功"""
    return {"success": True, "message": "开源版本不支持外观配置"}

@router.get("/license")
async def get_license(session: SessionDep, trans: Trans):
    """获取许可证信息 - 开源版本返回默认信息"""
    return {
        "status": "valid",
        "corporation": "开源版本",
        "expired": "2099-12-31",
        "count": 999999,
        "version": "1.1.4",
        "edition": "开源版",
        "serialNo": "",
        "remark": "SQLBot开源版本",
        "isv": "SQLBot开源社区"
    }

@router.get("/license/version")
async def get_license_version(session: SessionDep, trans: Trans):
    """获取许可证版本 - 开源版本返回版本号"""
    return "1.1.4"

@router.post("/license")
async def update_license(session: SessionDep, trans: Trans, data: dict):
    """更新许可证 - 开源版本不支持"""
    return {"success": False, "message": "开源版本不支持许可证更新"}
