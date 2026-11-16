from fastapi.testclient import TestClient
from main import app
import models, database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configura um banco de dados em memória exclusivo para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[database.get_db] = override_get_db
client = TestClient(app)

def test_registrar_saida_valida():
    db = TestingSessionLocal()
    # Limpa e injeta um item de teste
    db.query(models.ItemEstoque).delete()
    item = models.ItemEstoque(codigo_patrimonio="TI-001", nome="Toner Preto", quantidade_atual=10, estoque_minimo=2)
    db.add(item)
    db.commit()
    db.refresh(item)

    # Executa a requisição simulando o Frontend
    response = client.post(
        "/api/movimentacoes", 
        json={"item_id": item.id, "quantidade": 3, "tipo": "SAIDA", "setor": "Recepção"}
    )
    
    assert response.status_code == 201
    assert response.json()["quantidade_restante"] == 7