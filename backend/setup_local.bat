@echo off
REM Script para configurar ambiente local sem Docker
setlocal enabledelayedexpansion

echo 🚀 Configurando JurChat Backend (Local - Sem Docker)
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.11+ primeiro.
    echo    Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python encontrado

REM Verificar PostgreSQL
pg_config --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PostgreSQL não encontrado
    echo    Install: winget install PostgreSQL.PostgreSQL
    echo    Ou: https://www.postgresql.org/download/windows/
) else (
    echo ✅ PostgreSQL encontrado
)

REM Verificar Redis
redis-server --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Redis não encontrado
    echo    Install: choco install redis-64
    echo    Ou use WSL: wsl e então apt install redis-server
) else (
    echo ✅ Redis encontrado
)

echo.
echo 📝 Configurando Django App...

REM Configurar Django
cd django_app

REM Criar ambiente virtual
if not exist venv (
    echo Criando ambiente virtual Python...
    python -m venv venv
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Atualizar pip
python -m pip install --upgrade pip

REM Instalar dependências
echo Instalando dependências Django...
pip install -r requirements.txt

REM Criar arquivo .env se não existir
if not exist .env (
    echo Criando arquivo .env...
    (
        echo # Local Development Settings
        echo DEBUG=True
        echo SECRET_KEY=local-dev-secret-key-change-me
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo.
        echo # Database (Configure com suas credenciais PostgreSQL^)
        echo DB_NAME=jurchat
        echo DB_USER=postgres
        echo DB_PASSWORD=postgres
        echo DB_HOST=localhost
        echo DB_PORT=5432
        echo.
        echo # Redis
        echo REDIS_URL=redis://localhost:6379/1
        echo.
        echo # Storage (local^)
        echo USE_S3=False
        echo.
        echo # OpenAI (opcional^)
        echo OPENAI_API_KEY=
        echo.
        echo # FastAPI
        echo FASTAPI_SERVICE_URL=http://localhost:8001
        echo.
        echo # Security
        echo ENCRYPTION_KEY=local-dev-encryption-key-32chars
    ) > .env
)

echo.
echo 📊 Executando migrações...
python manage.py makemigrations
python manage.py migrate

echo.
echo 👤 Criar superusuário? (y/N):
set /p create_super="Resposta: "
if /i "!create_super!"=="y" (
    python manage.py createsuperuser
)

echo.
echo 🎉 Django configurado!
echo.
echo 📋 Próximos passos:
echo.
echo 1. Configure PostgreSQL e Redis se ainda não fez
echo 2. Edite o arquivo django_app\.env com suas credenciais
echo 3. Execute os serviços:
echo.
echo    Para Django:
echo    cd django_app
echo    venv\Scripts\activate
echo    python manage.py runserver 8000
echo.
echo    Para FastAPI (em outro terminal^):
echo    cd fastapi_app
echo    python -m venv venv
echo    venv\Scripts\activate
echo    pip install -r requirements.txt
echo    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
echo.
echo 🌐 URLs após iniciar:
echo    Django: http://localhost:8000
echo    Django Admin: http://localhost:8000/admin
echo    FastAPI: http://localhost:8001/docs
echo.

pause
