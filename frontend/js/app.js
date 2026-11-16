const API_URL = "/api";

// ==========================================
// 1. LISTAR ESTOQUE (DESKTOP + MOBILE CARDS)
// ==========================================
async function carregarEstoque() {
    const tabela = document.getElementById('tabela-estoque');
    const cardsMobile = document.getElementById('cards-estoque-mobile');
    
    if (!tabela && !cardsMobile) return; 

    try {
        const response = await fetch(`${API_URL}/estoque`);
        if (!response.ok) throw new Error(`Erro HTTP: ${response.status}`);

        const itens = await response.json();
        
        if (tabela) tabela.innerHTML = '';
        if (cardsMobile) cardsMobile.innerHTML = '';

        if (itens.length === 0) {
            const msgVazio = 'Nenhum item cadastrado ainda.';
            if (tabela) tabela.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-3">${msgVazio}</td></tr>`;
            if (cardsMobile) cardsMobile.innerHTML = `<div class="card p-3 text-center text-muted">${msgVazio}</div>`;
            return;
        }

        itens.forEach(item => {
            const isEstoqueBaixo = item.quantidade_atual <= item.estoque_minimo;
            const badgeHTML = isEstoqueBaixo 
                ? '<span class="badge bg-danger">Estoque Baixo</span>' 
                : '<span class="badge bg-success">Regular</span>';
            const qtdClass = isEstoqueBaixo ? 'fw-bold text-danger' : 'fw-bold text-dark';

            // 1. Preenche a linha da tabela (Desktop)
            if (tabela) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${item.id}</td>
                    <td>${item.codigo_patrimonio}</td>
                    <td>${item.nome}</td>
                    <td class="${qtdClass}">${item.quantidade_atual}</td>
                    <td>${item.estoque_minimo}</td>
                    <td>${badgeHTML}</td>
                `;
                tabela.appendChild(tr);
            }

            // 2. Preenche o Card (Celular)
            if (cardsMobile) {
                const card = document.createElement('div');
                card.className = `card shadow-sm border-start border-4 ${isEstoqueBaixo ? 'border-danger' : 'border-success'}`;
                card.innerHTML = `
                    <div class="card-body py-2 px-3">
                        <div class="d-flex justify-content-between align-items-start mb-1">
                            <div>
                                <span class="badge bg-secondary me-1">ID: ${item.id}</span>
                                <small class="text-muted fw-semibold">${item.codigo_patrimonio}</small>
                            </div>
                            ${badgeHTML}
                        </div>
                        <h6 class="card-title mb-2 fw-bold">${item.nome}</h6>
                        <div class="d-flex justify-content-between align-items-center bg-light rounded px-2 py-1">
                            <span class="small text-muted">Qtd. Atual: <strong class="fs-6 ${qtdClass}">${item.quantidade_atual}</strong></span>
                            <span class="small text-muted">Mínimo: <strong>${item.estoque_minimo}</strong></span>
                        </div>
                    </div>
                `;
                cardsMobile.appendChild(card);
            }
        });
    } catch (error) {
        const msgErro = `Erro ao carregar dados: ${error.message}`;
        if (tabela) tabela.innerHTML = `<tr><td colspan="6" class="text-center text-danger">${msgErro}</td></tr>`;
        if (cardsMobile) cardsMobile.innerHTML = `<div class="alert alert-danger">${msgErro}</div>`;
    }
}

// ==========================================
// 2. CADASTRAR NOVO ITEM
// ==========================================
const formCadastro = document.getElementById('form-cadastro');

if (formCadastro) {
    formCadastro.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            codigo_patrimonio: document.getElementById('codigo').value,
            nome: document.getElementById('nome').value,
            categoria: document.getElementById('categoria').value,
            quantidade_atual: parseInt(document.getElementById('qtd_inicial').value),
            estoque_minimo: parseInt(document.getElementById('estoque_minimo').value)
        };

        try {
            const response = await fetch(`${API_URL}/itens`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert("Item cadastrado com sucesso!");
                window.location.href = "/app/dashboard.html";
            } else {
                const errorData = await response.json();
                alert(`Erro ao salvar: ${errorData.detail}`);
            }
        } catch (error) {
            alert(`Falha de comunicação: ${error.message}`);
        }
    });
}

// ==========================================
// 3. REGISTRAR SAÍDA DE ESTOQUE
// ==========================================
const formMov = document.getElementById('form-movimentacao');

if (formMov) {
    formMov.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            item_id: parseInt(document.getElementById('item_id').value),
            quantidade: parseInt(document.getElementById('quantidade').value),
            tipo: "SAIDA",
            setor: document.getElementById('setor').value
        };

        try {
            const response = await fetch(`${API_URL}/movimentacoes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert("Movimentação registrada com sucesso!");
                window.location.href = "/app/dashboard.html";
            } else {
                const errorData = await response.json();
                alert(`Erro: ${errorData.detail}`);
            }
        } catch (error) {
            alert(`Falha de comunicação: ${error.message}`);
        }
    });
}

document.addEventListener('DOMContentLoaded', carregarEstoque);