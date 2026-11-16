import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="SICOGE-TI API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MovimentacaoCreate(BaseModel):
    item_id: int
    quantidade: int
    tipo: str
    setor: str = "Padrão"

class ItemCreate(BaseModel):
    codigo_patrimonio: str
    nome: str
    categoria: str
    quantidade_atual: int
    estoque_minimo: int

@app.get("/api/estoque")
def listar_estoque(db: Session = Depends(database.get_db)):
    return db.query(models.ItemEstoque).all()

@app.post("/api/itens", status_code=201)
def cadastrar_item(item: ItemCreate, db: Session = Depends(database.get_db)):
    db_item = db.query(models.ItemEstoque).filter(models.ItemEstoque.codigo_patrimonio == item.codigo_patrimonio).first()
    if db_item:
        raise HTTPException(status_code=400, detail="Código de patrimônio já cadastrado.")
    
    novo_item = models.ItemEstoque(
        codigo_patrimonio=item.codigo_patrimonio,
        nome=item.nome,
        categoria=item.categoria,
        quantidade_atual=item.quantidade_atual,
        estoque_minimo=item.estoque_minimo
    )
    
    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)
    return novo_item

@app.post("/api/movimentacoes", status_code=201)
def registrar_movimentacao(mov: MovimentacaoCreate, db: Session = Depends(database.get_db)):
    item = db.query(models.ItemEstoque).filter(models.ItemEstoque.id == mov.item_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado. Verifique o ID.")
    
    if mov.tipo == "SAIDA":
        if item.quantidade_atual < mov.quantidade:
            raise HTTPException(status_code=400, detail="Estoque insuficiente para esta saída.")
        item.quantidade_atual -= mov.quantidade
    elif mov.tipo == "ENTRADA":
        item.quantidade_atual += mov.quantidade
    
    nova_mov = models.Movimentacao(
        item_id=item.id, 
        tipo=mov.tipo, 
        quantidade=mov.quantidade, 
        destino_setor=mov.setor
    )
    
    db.add(nova_mov)
    db.commit()
    db.refresh(item)
    
    return {"mensagem": "Sucesso", "quantidade_restante": item.quantidade_atual}

# Serve o Frontend na mesma porta (8000)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

@app.get("/")
def raiz():
    return RedirectResponse(url="/app/index.html")

app.mount("/app", StaticFiles(directory=FRONTEND_DIR), name="frontend")