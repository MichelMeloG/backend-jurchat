@echo off
REM Script de setup para desenvolvimento local no Windows
setlocal enabledelayedexpansion

echo 🚀 Configurando JurChat Backend para desenvolvimento...

REM Verificar se Docker está rodando
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está rodando. Por favor, inicie o Docker primeiro.
    pause
    exit /b 1
)

REM Criar arquivo .env se não existir
if not exist .env (
    echo 📝 Criando arquivo .env...
    (
        echo # Development Environment Settings
        echo.
        echo # Django
        echo DEBUG=True
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo.
        echo # Database
        echo DB_NAME=jurchat
        echo DB_USER=postgres
        echo DB_PASSWORD=postgres123
        echo DB_HOST=postgres
        echo DB_PORT=5432
        echo.
        echo # Redis
        echo REDIS_URL=redis://redis:6379/1
        echo.
        echo # OpenAI (opcional - deixe vazio para usar mock^)
        echo OPENAI_API_KEY=
        echo OPENAI_MODEL=gpt-3.5-turbo
        echo MAX_TOKENS=2000
        echo.
        echo # Storage (MinIO local^)
        echo USE_S3=True
        echo AWS_ACCESS_KEY_ID=minioadmin
        echo AWS_SECRET_ACCESS_KEY=minioadmin123
        echo AWS_STORAGE_BUCKET_NAME=jurchat-documents
        echo AWS_S3_ENDPOINT_URL=http://minio:9000
        echo.
        echo # Security
        echo ENCRYPTION_KEY=dev-encryption-key-32-chars-long
        echo.
        echo # FastAPI
        echo FASTAPI_SERVICE_URL=http://fastapi_app:8001
    ) > .env
    echo ✅ Arquivo .env criado com configurações de desenvolvimento
) else (
    echo 📁 Arquivo .env já existe
)

REM Parar containers existentes
echo 🛑 Parando containers existentes...
docker-compose down

REM Construir e iniciar serviços
echo 🔨 Construindo e iniciando serviços...
docker-compose up -d --build

REM Aguardar serviços ficarem prontos
echo ⏳ Aguardando serviços ficarem prontos...
timeout /t 30 /nobreak >nul

REM Executar migrações
echo 📊 Executando migrações do banco de dados...
docker-compose exec -T django_app python manage.py makemigrations
docker-compose exec -T django_app python manage.py migrate

REM Configurar MinIO
echo 🗄️ Configurando storage MinIO...
docker-compose exec -T minio mc alias set local http://localhost:9000 minioadmin minioadmin123 2>nul
docker-compose exec -T minio mc mb local/jurchat-documents 2>nul
docker-compose exec -T minio mc policy set public local/jurchat-documents 2>nul

REM Criar superusuário (opcional)
echo.
set /p create_superuser="👤 Você gostaria de criar um superusuário Django agora? (y/N): "
if /i "!create_superuser!"=="y" (
    echo Criando superusuário...
    docker-compose exec django_app python manage.py createsuperuser
)

echo.
echo 🎉 Setup concluído com sucesso!
echo.
echo 📋 URLs dos serviços:
echo    🌐 Django API: http://localhost:8000
echo    👨‍💼 Django Admin: http://localhost:8000/admin
echo    🤖 FastAPI Docs: http://localhost:8001/docs
echo    🗄️ MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)
echo.
echo 📝 Próximos passos:
echo    1. Acesse http://localhost:8000/admin para verificar se tudo está funcionando
echo    2. Teste o upload de documentos via API
echo    3. Configure sua chave OpenAI no arquivo .env se quiser usar IA real
echo.
echo 🔧 Comandos úteis:
echo    docker-compose logs -f             # Ver logs de todos os serviços
echo    docker-compose logs django_app     # Ver logs do Django
echo    docker-compose exec django_app python manage.py shell  # Shell Django
echo    docker-compose down                # Parar todos os serviços
echo.
pause
