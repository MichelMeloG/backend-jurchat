#!/bin/bash

# Script de setup para desenvolvimento local
set -e

echo "🚀 Configurando JurChat Backend para desenvolvimento..."

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cat > .env << EOF
# Development Environment Settings

# Django
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=jurchat
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/1

# OpenAI (opcional - deixe vazio para usar mock)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=2000

# Storage (MinIO local)
USE_S3=True
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin123
AWS_STORAGE_BUCKET_NAME=jurchat-documents
AWS_S3_ENDPOINT_URL=http://minio:9000

# Security
ENCRYPTION_KEY=dev-encryption-key-32-chars-long

# FastAPI
FASTAPI_SERVICE_URL=http://fastapi_app:8001
EOF
    echo "✅ Arquivo .env criado com configurações de desenvolvimento"
else
    echo "📁 Arquivo .env já existe"
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e iniciar serviços
echo "🔨 Construindo e iniciando serviços..."
docker-compose up -d --build

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Executar migrações
echo "📊 Executando migrações do banco de dados..."
docker-compose exec -T django_app python manage.py makemigrations
docker-compose exec -T django_app python manage.py migrate

# Criar bucket no MinIO
echo "🗄️ Configurando storage MinIO..."
docker-compose exec -T minio mc alias set local http://localhost:9000 minioadmin minioadmin123 || true
docker-compose exec -T minio mc mb local/jurchat-documents || true
docker-compose exec -T minio mc policy set public local/jurchat-documents || true

# Criar superusuário (opcional)
echo "👤 Você gostaria de criar um superusuário Django agora? (y/N)"
read -r create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    echo "Criando superusuário..."
    docker-compose exec django_app python manage.py createsuperuser
fi

echo ""
echo "🎉 Setup concluído com sucesso!"
echo ""
echo "📋 URLs dos serviços:"
echo "   🌐 Django API: http://localhost:8000"
echo "   👨‍💼 Django Admin: http://localhost:8000/admin"
echo "   🤖 FastAPI Docs: http://localhost:8001/docs"
echo "   🗄️ MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)"
echo ""
echo "📝 Próximos passos:"
echo "   1. Acesse http://localhost:8000/admin para verificar se tudo está funcionando"
echo "   2. Teste o upload de documentos via API"
echo "   3. Configure sua chave OpenAI no arquivo .env se quiser usar IA real"
echo ""
echo "🔧 Comandos úteis:"
echo "   docker-compose logs -f             # Ver logs de todos os serviços"
echo "   docker-compose logs django_app     # Ver logs do Django"
echo "   docker-compose exec django_app python manage.py shell  # Shell Django"
echo "   docker-compose down                # Parar todos os serviços"
echo ""
