from sqlalchemy import Column, Integer, String, DateTime
from database import Base
import datetime

class ItemEstoque(Base):
    __tablename__ = "itens_estoque"

    id = Column(Integer, primary_key=True, index=True)
    codigo_patrimonio = Column(String, unique=True, index=True)
    nome = Column(String, index=True)
    categoria = Column(String)
    quantidade_atual = Column(Integer, default=0)
    estoque_minimo = Column(Integer, default=5)

class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer)
    tipo = Column(String)
    quantidade = Column(Integer)
    destino_setor = Column(String, nullable=True)
    data_hora = Column(DateTime, default=datetime.datetime.utcnow)