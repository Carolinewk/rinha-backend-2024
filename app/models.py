from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from pydantic import BaseModel
from .database import Base
from sqlalchemy.sql.expression import text
from datetime import datetime

class Client(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    limite = Column(Integer, nullable=False)
    saldo = Column(Integer, nullable=False)

class Transaction(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clientes.id"))
    valor = Column(Integer)
    tipo = Column(String(1))
    descricao = Column(String)
    created_at = Column(DateTime, default=datetime.now())
