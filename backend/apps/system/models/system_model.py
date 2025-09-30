   
from typing import Optional
from sqlmodel import BigInteger, Field, Text, SQLModel
from common.core.models import SnowflakeBase
from common.core.schemas import BaseCreatorDTO


class AiModelBase:
    supplier: int = Field(nullable=False)
    name: str = Field(max_length=255, nullable=False)
    model_type: int = Field(nullable=False)
    base_model: str = Field(max_length = 255, nullable=False)
    default_model: bool = Field(default=False, nullable=False)

class AiModelDetail(SnowflakeBase, AiModelBase, table=True):
   __tablename__ = "ai_model"
   api_key: str | None = Field(nullable=True)
   api_domain: str = Field(nullable=False)
   protocol: int = Field(nullable=False, default = 1)
   config: str = Field(sa_type = Text())
   status: int = Field(nullable=False, default = 1)
   create_time: int = Field(default=0, sa_type=BigInteger())
   



class WorkspaceBase(SQLModel):
    name: str = Field(max_length=255, nullable=False)

class WorkspaceEditor(WorkspaceBase, BaseCreatorDTO):
    pass
    
class WorkspaceModel(SnowflakeBase, WorkspaceBase, table=True):
    __tablename__ = "sys_workspace"
    create_time: int = Field(default=0, sa_type=BigInteger())
    
class UserWsBaseModel(SQLModel):
    uid: int = Field(nullable=False, sa_type=BigInteger())
    oid: int = Field(nullable=False, sa_type=BigInteger())
    weight: int =  Field(default=0, nullable=False)
    
class UserWsModel(SnowflakeBase, UserWsBaseModel, table=True):
    __tablename__ = "sys_user_ws"
    

class AssistantBaseModel(SQLModel):
    name: str = Field(max_length=255, nullable=False)
    type: int = Field(nullable=False, default=0)
    domain: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(sa_type = Text(), nullable=True)
    configuration: Optional[str] = Field(sa_type = Text(), nullable=True)
    create_time: int = Field(default=0, sa_type=BigInteger())
    app_id: Optional[str] = Field(default=None, max_length=255,  nullable=True)
    app_secret: Optional[str] = Field(default=None, max_length=255, nullable=True)

class AssistantModel(SnowflakeBase, AssistantBaseModel, table=True):
    __tablename__ = "sys_assistant"
    