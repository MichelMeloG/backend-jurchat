# Guia de Setup Local (Sem Docker)

## Pré-requisitos
- Python 3.11+
- PostgreSQL 15+
- Redis
- Node.js (opcional, para ferramentas de desenvolvimento)

## 1. Configurar PostgreSQL

### Instalar PostgreSQL:
```bash
# Via winget
winget install PostgreSQL.PostgreSQL

# Ou baixe de: https://www.postgresql.org/download/windows/
```

### Criar banco de dados:
```sql
-- Conecte ao PostgreSQL como superusuário
createdb jurchat
```

## 2. Configurar Redis

### Instalar Redis:
```bash
# Via chocolatey (instale chocolatey primeiro)
choco install redis-64

# Ou use Redis no WSL
wsl --install
wsl
sudo apt update && sudo apt install redis-server
```

## 3. Configurar Django App

### No diretório django_app:
```bash
cd django_app

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
copy ..\.env.example .env
# Edite o .env com suas configurações locais

# Executar migrações
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar servidor
python manage.py runserver 0.0.0.0:8000
```

## 4. Configurar FastAPI App

### Em outro terminal, no diretório fastapi_app:
```bash
cd fastapi_app

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar servidor
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## 5. Variáveis de Ambiente (.env)

```env
# Database (PostgreSQL local)
DB_NAME=jurchat
DB_USER=postgres
DB_PASSWORD=sua_senha_postgres
DB_HOST=localhost
DB_PORT=5432

# Redis (local)
REDIS_URL=redis://localhost:6379/1

# Outros
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
USE_S3=False
FASTAPI_SERVICE_URL=http://localhost:8001
```

## 6. Testar Setup

1. Django: http://localhost:8000/admin
2. FastAPI: http://localhost:8001/docs
3. API Django: http://localhost:8000/auth/

## Notas Importantes

- **PostgreSQL**: Configure a senha e crie o banco 'jurchat'
- **Redis**: Deve estar rodando na porta 6379
- **Python**: Use ambientes virtuais separados para Django e FastAPI
- **Dependências**: Instale exatamente como nos requirements.txt
