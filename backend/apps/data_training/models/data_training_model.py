from datetime import datetime
from typing import List, Optional

from pgvector.sqlalchemy import VECTOR
from pydantic import BaseModel
from sqlalchemy import Column, Text, BigInteger, DateTime, Identity
from sqlmodel import SQLModel, Field


class DataTraining(SQLModel, table=True):
    __tablename__ = "data_training"
    id: Optional[int] = Field(sa_column=Column(BigInteger, Identity(always=True), primary_key=True))
    oid: Optional[int] = Field(sa_column=Column(BigInteger, nullable=True, default=1))
    datasource: Optional[int] = Field(sa_column=Column(BigInteger, nullable=True))
    create_time: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=False), nullable=True))
    question: Optional[str] = Field(max_length=255)
    description: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    embedding: Optional[List[float]] = Field(sa_column=Column(VECTOR(), nullable=True))


class DataTrainingInfo(BaseModel):
    id: Optional[int] = None
    oid: Optional[int] = None
    datasource: Optional[int] = None
    datasource_name: Optional[str] = None
    create_time: Optional[datetime] = None
    question: Optional[str] = None
    description: Optional[str] = None
