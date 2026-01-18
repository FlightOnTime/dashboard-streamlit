## 🚀 Visão geral

Projeto: dashboard em Streamlit para visualização e previsão de atrasos de voos.

Principais componentes:
- Interface principal: `src/app.py`
- Páginas do Streamlit: `src/pages/Nova_Previsão.py`, `src/pages/Dashboard.py`, `src/pages/Storytelling.py`
- Exemplo de dados / mock: `src/pages/MOCK_DATA.sql`

**Linguagem / libs principais:** Python, Streamlit, Pandas, Plotly, psycopg2 / SQLAlchemy (opcional), python-dotenv.

## 🔧 Requisitos

- Python 3.12+
- Dependências listadas em `requirements.txt` e `pyproject.toml`.

## 📥 Instalação (rápida)

1. Clone o repositório e entre na pasta:

```bash
git clone <repo-url>
cd dash
```

2. Crie e ative um ambiente virtual (recomendado):

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

> Observação: o projeto também tem `pyproject.toml` com dependências (para Poetry/modern packaging).

## ⚙️ Variáveis de ambiente

O projeto usa variáveis para conectar ao banco de dados PostgreSQL. Há um arquivo de exemplo `.env.exemple` no repositório — copie e preencha com suas credenciais:

```bash
cp .env.exemple .env
# editar .env e inserir valores:
# DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
```

Nota: `.env` está no `.gitignore` por segurança — não comite credenciais.

## ▶️ Executando a aplicação

```bash
streamlit run src/app.py
```

Por padrão o Streamlit abre em `http://localhost:8501`.

## 🧭 Páginas e funcionalidades

- **Nova Previsão (`src/pages/Nova_Previsão.py`)**
    - Formulário para previsão individual (envia JSON para uma API de predição).
    - Upload em lote (CSV) para enviar vários voos ao endpoint `/api/v1/predict/batch`.
    - Endpoints padrão no código: `http://localhost:8080/api/v1/predict` e `/api/v1/predict/batch` — ajuste se necessário.

- **Dashboard (`src/pages/Dashboard.py`)**
    - Carrega histórico de previsões de `prediction_history` (banco PostgreSQL) e mostra painéis, mapas e gráficos.
    - Aguarda variáveis de conexão no `.env` (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD).
    - Observação: dependendo da forma como a conexão está implementada, o pandas pode emitir um aviso indicando que é preferível usar um engine SQLAlchemy (aceitável e recomendado).

- **Storytelling (`src/pages/Storytelling.py`)**
    - Página informativa sobre fonte de dados, pipeline e boas práticas; conteúdo estático e explicativo.

## 🗄️ Banco de dados / MOCK

- Existe `src/pages/MOCK_DATA.sql` com exemplo de esquema e inserts. Para testar localmente sem Postgres você pode:
    - Carregar o SQL em um SQLite temporário ou executar diretamente em um container/Postgres local.

## 🔁 Integração com backend de predição

- `src/pages/Nova_Previsão.py` comunica-se com um serviço HTTP (API) para obter previsões. Se você não tem essa API rodando, os envios falharão.
- Para testes locais, você pode simular a API com um servidor simples (Flask/FastAPI) que exponha os endpoints mencionados.

## 🐛 Problemas comuns e como resolver

- `pandas only supports SQLAlchemy connectable...` — solução:
    - Instale `SQLAlchemy` e use uma URI compatível (ex.: `postgresql+psycopg2://user:pass@host:port/dbname`) ao chamar `pd.read_sql_query()`; ou passe um engine SQLAlchemy em vez de uma conexão psycopg2 crua.

- `.env` não está sendo lido: verifique se `python-dotenv` está instalado e que seu código chama `load_dotenv()` (ou exporte variáveis manualmente no shell):

```bash
export DB_HOST=localhost
export DB_PORT=5432
# etc
```

- Erros de conexão com o Postgres: confirme credenciais, firewall/ports e se o serviço está em execução.

## 💡 Dicas de desenvolvimento

- Recomendo usar `poetry` ou `venv` para isolar o ambiente.
- Para evitar warnings do pandas, utilize SQLAlchemy engine (veja `sqlalchemy.create_engine`).
- Mantenha `.env` fora do repositório (já incluído em `.gitignore`).

## ✅ Boas práticas aplicadas

- Arquivo de exemplo `.env.exemple` para compartilhar variáveis sem expor segredos.
- `.gitignore` atualizado para não versionar ambientes locais e arquivos sensíveis.

## 👥 Contribuição

1. Crie um branch: `git checkout -b feat/minha-melhoria`
2. Faça commits pequenos e claros.
3. Abra um Pull Request descrevendo a mudança.

## 📫 Suporte

Abra uma issue no repositório ou entre em contato com o mantenedor listado no `pyproject.toml`.

---
