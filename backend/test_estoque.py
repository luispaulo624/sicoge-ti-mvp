"""Suíte de testes automatizados (unitários e de integração) do SICOGE-TI."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app
from models import ItemEstoque, Movimentacao

# Banco SQLite em memória isolado: evita criação de arquivos residuais no repositório
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(name="db_session")
def fixture_db_session():
    """Cria um schema limpo antes de cada teste e o destrói ao finalizar."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(name="client")
def fixture_client(db_session):
    """Fornece um TestClient da API com a dependência de banco sobrescrita."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(name="item_padrao")
def fixture_item_padrao(db_session):
    """Insere um insumo padrão no banco de testes para reutilização nos cenários."""
    item = ItemEstoque(
        codigo_patrimonio="TI-001",
        nome="Toner TN-3472",
        categoria="Suprimentos",
        quantidade_atual=10,
        estoque_minimo=5,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


def test_listar_estoque_vazio(client):
    """Garante que a listagem retorna lista vazia quando não há itens cadastrados."""
    response = client.get("/api/estoque")

    assert response.status_code == 200
    assert response.json() == []


def test_listar_estoque_com_itens(client, item_padrao):
    """Garante que os itens cadastrados são retornados corretamente pela API."""
    response = client.get("/api/estoque")
    dados = response.json()

    assert response.status_code == 200
    assert len(dados) == 1
    assert dados[0]["codigo_patrimonio"] == item_padrao.codigo_patrimonio
    assert dados[0]["quantidade_atual"] == 10


def test_registrar_entrada_estoque(client, db_session, item_padrao):
    """Valida o incremento de saldo e o registro de auditoria na entrada de itens."""
    payload = {
        "item_id": item_padrao.id,
        "quantidade": 5,
        "tipo": "ENTRADA",
        "setor": "Almoxarifado Central",
    }

    response = client.post("/api/movimentacoes", json=payload)

    assert response.status_code == 201
    assert response.json()["quantidade_restante"] == 15

    # Verifica a persistência do log de movimentação (rastreabilidade ODS 16)
    registro = db_session.query(Movimentacao).first()
    assert registro is not None
    assert registro.tipo == "ENTRADA"
    assert registro.quantidade == 5


def test_registrar_saida_valida(client, db_session, item_padrao):
    """Valida o abatimento de saldo e a gravação do setor de destino na saída."""
    payload = {
        "item_id": item_padrao.id,
        "quantidade": 3,
        "tipo": "SAIDA",
        "setor": "Departamento de Processamento de Dados",
    }

    response = client.post("/api/movimentacoes", json=payload)

    assert response.status_code == 201
    assert response.json()["quantidade_restante"] == 7

    registro = db_session.query(Movimentacao).first()
    assert registro is not None
    assert registro.tipo == "SAIDA"
    assert registro.destino_setor == "Departamento de Processamento de Dados"


def test_registrar_saida_estoque_insuficiente(client, db_session, item_padrao):
    """Impede saída maior que o saldo disponível e preserva a integridade do estoque."""
    payload = {
        "item_id": item_padrao.id,
        "quantidade": 25,  # Saldo atual é 10
        "tipo": "SAIDA",
        "setor": "Secretaria",
    }

    response = client.post("/api/movimentacoes", json=payload)

    assert response.status_code == 400
    assert "insuficiente" in response.json()["detail"].lower()

    # Garante que o saldo não foi alterado e nenhuma movimentação inválida foi salva
    db_session.refresh(item_padrao)
    assert item_padrao.quantidade_atual == 10
    assert db_session.query(Movimentacao).count() == 0


def test_registrar_movimentacao_item_inexistente(client):
    """Garante retorno HTTP 404 ao tentar movimentar um ID não cadastrado."""
    payload = {
        "item_id": 9999,
        "quantidade": 1,
        "tipo": "SAIDA",
        "setor": "Recepção",
    }

    response = client.post("/api/movimentacoes", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Item não encontrado"
