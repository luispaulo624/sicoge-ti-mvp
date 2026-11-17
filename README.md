# SICOGE-TI (MVP)

**Sistema de Controle e Gestão de Insumos e Periféricos de TI** — desenvolvido para o Departamento de Processamento de Dados da Prefeitura Municipal de Piracanjuba - GO, com alinhamento ao **ODS 12 (Meta 12.7 — Compras Públicas Sustentáveis)**.

---

## Sobre o Projeto
O **SICOGE-TI** substitui planilhas manuais e contagens físicas por um painel web centralizado para consulta de saldos em tempo real, registro de baixas vinculadas aos setores municipais solicitantes e sinalização automática de itens em nível crítico de reposição.

## Arquitetura e Tecnologias
- **Back-end:** Python 3 com FastAPI, validação de dados via Pydantic e persistência relacional com SQLAlchemy.
- **Banco de Dados:** SQLite (`sicoge.db`).
- **Front-end:** HTML5, CSS3, JavaScript e Bootstrap 5 (layout responsivo *mobile-first* validado a partir de 360px).

## Requisitos, Segurança e Acessibilidade
- **Funcionalidades Principais:** Autenticação institucional, cadastro de insumos com estoque mínimo, consulta de saldo atual, registro de movimentações vinculadas ao setor de destino e alertas de estoque baixo.
- **Segurança:** Autenticação baseada em tokens JWT, senhas protegidas com hash `bcrypt`, bloqueio atômico contra saldos negativos no servidor e renderização segura contra XSS.
- **Acessibilidade (WCAG 2.1 AA):** Rótulos fixos associados aos campos, alto contraste, navegação integral por teclado com foco visível, áreas de toque adequadas para uso móvel e alertas multimodais.

---

## Como rodar o projeto localmente

1. Abra o terminal na pasta `backend`.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
Execute o servidor:

Bash
uvicorn main:app --reload
A API estará rodando em http://localhost:8000.

Para acessar o Frontend, basta dar um duplo clique no arquivo frontend/index.html no seu navegador.

Projeto validado com layout responsivo mobile-first.
