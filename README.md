# 🏛️ JurChat Backend

**Sistema de Chat com IA para Análise de Documentos Jurídicos**

Um MVP completo de backend que permite upload, processamento e conversação inteligente com documentos jurídicos usando OpenAI GPT.

## ✨ Características Principais

### 🔐 **Autenticação Completa**
- Sistema JWT para registro, login e autorização
- Modelo de usuário customizado com planos (Free/Premium)
- Controle de limites por plano
- Admin interface para gerenciamento

### 📄 **Gestão de Documentos**
- Upload suportando PDF, DOC, DOCX e TXT
- Criptografia de documentos sensíveis
- Processamento assíncrono via IA
- Histórico completo de uploads

### 🤖 **IA Avançada**
- Extração inteligente de texto de documentos
- Resumos automáticos em linguagem simples
- Chat contextual sobre conteúdo dos documentos
- Integração com OpenAI GPT-3.5/4

### 💬 **Sistema de Chat**
- Sessões de chat por documento
- Histórico de conversações
- Respostas contextualizadas baseadas no documento
- Interface REST para integração frontend

### 🏗️ **Arquitetura Microserviços**
- **Django REST API** - Core do sistema (autenticação, CRUD)
- **FastAPI** - Microserviço especializado em IA
- **PostgreSQL/SQLite** - Banco de dados flexível
- **Redis** - Cache para performance (opcional)

## 🔧 Tecnologias Utilizadas

### Backend Core
- **Django 4.2.7** - Framework web robusto
- **Django REST Framework** - API REST completa
- **JWT Authentication** - Autenticação segura
- **PostgreSQL** - Banco principal (SQLite para dev)
- **Redis** - Cache e sessões (opcional)

### Microserviço IA
- **FastAPI** - API moderna e rápida
- **OpenAI API** - Processamento de linguagem natural
- **PyPDF2 + python-docx** - Extração de texto
- **Uvicorn** - Servidor ASGI performático

### DevOps & Deploy
- **Docker & Docker Compose** - Containerização
- **Nginx** - Proxy reverso (produção)
- **Gunicorn** - Servidor WSGI (produção)
- **AWS S3** - Storage de arquivos (opcional)

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND CLIENT                         │
│                 (React/Vue/Angular)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 NGINX REVERSE PROXY                        │
│                    (Produção)                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
            ┌─────────┴──────────┐
            ▼                    ▼
┌───────────────────────┐ ┌─────────────────────────┐
│   DJANGO REST API     │ │    FASTAPI AI SERVICE  │
│     (Port 8000)       │ │      (Port 8001)        │
├───────────────────────┤ ├─────────────────────────┤
│ • JWT Authentication  │ │ • Document Processing   │
│ • User Management     │ │ • Text Extraction       │
│ • Document CRUD       │ │ • AI Summarization      │
│ • Chat Sessions       │ │ • Contextual Chat       │
│ • Plan Controls       │ │ • OpenAI Integration    │
│ • Admin Interface     │ │ • Async Processing      │
└───────────┬───────────┘ └─────────────────────────┘
            │                          │
            ▼                          ▼
┌───────────────────────┐ ┌─────────────────────────┐
│   PostgreSQL/SQLite   │ │      OpenAI API         │
│                       │ │                         │
│ • Users & Auth        │ │ • GPT-3.5/4 Models      │
│ • Documents           │ │ • Text Processing       │
│ • Chat History        │ │ • Intelligent Responses │
│ • Plans & Limits      │ │                         │
└───────────────────────┘ └─────────────────────────┘
            │
            ▼
┌───────────────────────┐
│    Redis Cache        │
│     (Opcional)        │
│                       │
│ • Session Storage     │
│ • API Caching         │
│ • Background Tasks    │
└───────────────────────┘
```

### 🔄 **Fluxo de Dados**

1. **Upload de Documento**: Cliente → Django → Validação → Storage
2. **Processamento IA**: Django → FastAPI → OpenAI → Extração + Resumo
3. **Chat**: Cliente → Django → FastAPI (contexto) → OpenAI → Resposta
4. **Autenticação**: Cliente → Django → JWT → Validação

## 📋 Pré-requisitos

### 🚀 **Execução Rápida (Docker)**
- Docker & Docker Compose
- Chave da API OpenAI (opcional)

### 🛠️ **Desenvolvimento Local**
- Python 3.8+ (recomendado 3.11+)
- pip (gerenciador de pacotes Python)
- Git
- Chave da API OpenAI (opcional)

### 📊 **Opcionais para Produção**
- PostgreSQL 12+
- Redis 6+
- Nginx
- AWS S3 (para storage de arquivos)

## � Guia de Instalação

### 🎯 **Método 1: Instalação Rápida com Docker**

#### 1. Clone o Repositório
```bash
git clone https://github.com/MichelMeloG/backend-jurchat.git
cd backend-jurchat
```

#### 2. Configure Variáveis de Ambiente
```bash
# Copie os arquivos de exemplo
cp backend/django_app/.env.example backend/django_app/.env
cp backend/fastapi_app/.env.example backend/fastapi_app/.env

# Edite os arquivos .env com suas configurações
# Principalmente adicione sua chave OpenAI (opcional)
```

#### 3. Execute com Docker
```bash
# Inicie todos os serviços
docker-compose up -d

# Aguarde a inicialização (pode levar alguns minutos)
docker-compose logs -f django_app

# Execute migrações (primeira vez)
docker-compose exec django_app python manage.py migrate

# Crie superusuário
docker-compose exec django_app python manage.py createsuperuser
```

### 🛠️ **Método 2: Instalação Local (Desenvolvimento)**

#### 1. Prepare o Ambiente
```bash
# Clone e entre no diretório
git clone https://github.com/MichelMeloG/backend-jurchat.git
cd backend-jurchat

# Crie ambiente virtual
python -m venv venv

# Ative o ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale todas as dependências
pip install -r requirements.txt
```

#### 2. Configure e Execute Django
```bash
cd backend/django_app

# Configure variáveis de ambiente
cp .env.example .env
# ✏️ Edite .env com suas configurações

# Execute migrações do banco
python manage.py migrate

# Crie usuário administrador
python manage.py createsuperuser

# Inicie o servidor Django (Terminal 1)
python manage.py runserver 8000
```

#### 3. Configure e Execute FastAPI
```bash
# Abra um novo terminal no diretório raiz
cd backend/fastapi_app

# Configure variáveis de ambiente
cp .env.example .env
# ✏️ Edite .env com sua chave OpenAI (opcional)

# Inicie FastAPI (terminal 2)
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

### 4. Acesse os Serviços

- **API Django**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **FastAPI Docs**: http://localhost:8001/docs
- **MinIO Console**: http://localhost:9001

## � API Endpoints

### 🔐 **Autenticação**

```http
# Registrar novo usuário
POST /api/auth/register/
Content-Type: application/json
{
  "username": "usuario",
  "email": "user@example.com", 
  "password": "senha123",
  "plan": "free"
}

# Fazer login
POST /api/auth/login/
Content-Type: application/json
{
  "username": "usuario",
  "password": "senha123"
}

# Obter perfil do usuário
GET /api/user/profile/
Authorization: Bearer <token>

# Verificar plano atual
GET /api/user/plan/
Authorization: Bearer <token>
```

### 📄 **Documentos**

```http
# Upload de documento
POST /api/documents/upload/
Authorization: Bearer <token>
Content-Type: multipart/form-data
file: arquivo.pdf

# Listar documentos do usuário
GET /api/documents/
Authorization: Bearer <token>

# Obter detalhes de um documento
GET /api/documents/{id}/
Authorization: Bearer <token>

# Reprocessar documento com IA
POST /api/documents/{id}/reprocess/
Authorization: Bearer <token>
```

### 💬 **Chat**

```http
# Criar sessão de chat
POST /api/chat/sessions/
Authorization: Bearer <token>
Content-Type: application/json
{
  "document_id": 123,
  "title": "Análise do Contrato"
}

# Listar sessões do usuário
GET /api/chat/sessions/
Authorization: Bearer <token>

# Enviar mensagem no chat
POST /api/chat/{session_id}/send/
Authorization: Bearer <token>
Content-Type: application/json
{
  "message": "Quais são os pontos principais deste contrato?"
}
```

### 🤖 **IA (FastAPI - Port 8001)**

```http
# Processar e resumir documento
POST http://localhost:8001/ai/summarize
Content-Type: multipart/form-data
file: documento.pdf
document_id: 123
user_id: 1

# Chat com contexto de documento
POST http://localhost:8001/ai/chat
Content-Type: application/json
{
  "message": "Explique as cláusulas principais",
  "document_id": "123",
  "document_content": "texto do documento...",
  "document_summary": "resumo...",
  "conversation_history": []
}
```

## 💾 Estrutura do Banco de Dados

### 👤 **User (Usuários)**
```python
- id: UUID (Primary Key)
- username: String (Unique)
- email: EmailField (Unique)
- plan: Choice ['free', 'premium']
- documents_limit: Integer
- chat_sessions_limit: Integer
- created_at: DateTime
- is_active: Boolean
```

### 📄 **Document (Documentos)**
```python
- id: UUID (Primary Key)
- user: ForeignKey(User)
- title: String
- original_filename: String
- file_path: String (Encrypted)
- file_size: Integer
- content_type: String
- extracted_text: Text (Encrypted)
- ai_summary: Text
- processing_status: Choice ['pending', 'processing', 'completed', 'failed']
- uploaded_at: DateTime
```

### 💬 **ChatSession (Sessões de Chat)**
```python
- id: UUID (Primary Key)
- user: ForeignKey(User)
- document: ForeignKey(Document)
- title: String
- created_at: DateTime
- updated_at: DateTime
```

### 📝 **ChatMessage (Mensagens)**
```python
- id: UUID (Primary Key)
- session: ForeignKey(ChatSession)
- role: Choice ['user', 'assistant']
- content: Text
- tokens_used: Integer
- created_at: DateTime
```

### 📊 **UserPlanHistory (Histórico de Planos)**
```python
- id: UUID (Primary Key)
- user: ForeignKey(User)
- old_plan: String
- new_plan: String
- changed_at: DateTime
- reason: String
```

## 🔒 Segurança & Compliance

### 🛡️ **Medidas de Segurança**
- **JWT Authentication** - Tokens seguros com expiração
- **Password Hashing** - bcrypt para senhas
- **Data Encryption** - AES-256 para dados sensíveis
- **File Validation** - Verificação de tipos de arquivo
- **Rate Limiting** - Proteção contra abuso de API
- **CORS Configuration** - Controle de acesso cross-origin
- **Input Sanitization** - Prevenção de ataques de injeção

### 🔐 **Proteção de Dados**
- Documentos criptografados no storage
- Logs de acesso e auditoria
- Exclusão segura de dados sensíveis
- Controle de acesso baseado em planos

## 📊 Limites de Plano

| Recurso | Plano Free | Plano Premium |
|---------|------------|---------------|
| **Documentos/mês** | 10 | ♾️ Ilimitado |
| **Tokens IA/mês** | 10.000 | ♾️ Ilimitado |
| **Mensagens/documento** | 20 | ♾️ Ilimitado |
| **Tamanho máximo do arquivo** | 10MB | 50MB |
| **Suporte técnico** | ❌ | ✅ |
| **Análises avançadas** | ❌ | ✅ |

## 📁 Estrutura do Projeto

```
backend-jurchat/
├── 📄 README.md
├── 📄 requirements.txt              # Dependências completas
├── 📄 requirements-dev.txt          # Dependências de desenvolvimento
├── 📄 docker-compose.yml            # Configuração Docker
├── 📄 .env.example                  # Exemplo de variáveis de ambiente
│
├── 📂 backend/
│   ├── 📂 django_app/               # 🌐 API Principal Django
│   │   ├── 📂 core/                 # Configurações do projeto
│   │   │   ├── settings.py          # Configurações Django
│   │   │   ├── urls.py              # URLs principais
│   │   │   └── wsgi.py              # WSGI para produção
│   │   │
│   │   ├── 📂 users/                # 👤 App de usuários
│   │   │   ├── models.py            # Modelo User customizado
│   │   │   ├── serializers.py       # Serializers DRF
│   │   │   ├── views.py             # Views da API
│   │   │   └── urls.py              # URLs de autenticação
│   │   │
│   │   ├── 📂 documents/            # 📄 App de documentos
│   │   │   ├── models.py            # Modelos Document
│   │   │   ├── serializers.py       # Serializers para uploads
│   │   │   ├── views.py             # Views CRUD documentos
│   │   │   └── services.py          # Lógica de negócio
│   │   │
│   │   ├── 📂 chat/                 # 💬 App de chat
│   │   │   ├── models.py            # ChatSession, ChatMessage
│   │   │   ├── serializers.py       # Serializers de chat
│   │   │   ├── views.py             # Views de chat
│   │   │   └── consumers.py         # WebSocket (futuro)
│   │   │
│   │   ├── 📄 manage.py             # Django CLI
│   │   ├── � requirements.txt      # Deps específicas Django
│   │   └── 📄 .env.example          # Config Django
│   │
│   └── 📂 fastapi_app/              # 🤖 Microserviço de IA
│       ├── 📄 main.py               # App principal FastAPI
│       ├── 📄 config.py             # Configurações
│       │
│       ├── 📂 services/             # 🔧 Serviços especializados
│       │   ├── ai.py                # Integração OpenAI
│       │   └── parser.py            # Extração de texto
│       │
│       ├── 📄 requirements.txt      # Deps específicas FastAPI
│       └── 📄 .env.example          # Config FastAPI
│
└── 📂 docs/                         # 📚 Documentação adicional
    └── api.md                       # Docs detalhadas da API
```

## 🛠️ Desenvolvimento

### **Configuração do Ambiente de Dev**

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Configurar hooks pre-commit (opcional)
pre-commit install

# Configurar IDE com Python paths
export PYTHONPATH="${PYTHONPATH}:backend/django_app:backend/fastapi_app"
```

### **Comandos Úteis**

```bash
# Django
python manage.py shell              # Console Django
python manage.py makemigrations     # Criar migrações
python manage.py migrate            # Aplicar migrações
python manage.py collectstatic      # Coletar arquivos estáticos
python manage.py createsuperuser    # Criar admin

# FastAPI
uvicorn main:app --reload           # Servidor dev com reload
python -c "from main import app; print(app.openapi())"  # Schema OpenAPI

# Qualidade de código
black .                             # Formatar código
flake8 .                           # Verificar estilo
isort .                            # Organizar imports
mypy .                             # Verificar tipos
```

## 🧪 Testes & QA

### **Executar Testes**

```bash
# Testes Django
cd backend/django_app
python manage.py test

# Testes FastAPI
cd backend/fastapi_app  
python -m pytest

# Com Docker
docker-compose exec django_app python manage.py test
docker-compose exec fastapi_app python -m pytest

# Cobertura de código
pytest --cov=. --cov-report=html
```

### **Qualidade de Código**

```bash
# Formatação automática
black backend/

# Verificação de estilo
flake8 backend/

# Organização de imports
isort backend/

# Verificação de tipos
mypy backend/
```

## 📈 Monitoramento

- **Logs** centralizados via Docker
- **Health checks** no Nginx
- **Métricas** de uso por usuário

## 🚢 Deploy em Produção

### 1. Configuração

- Configure SSL/TLS no Nginx
- Use PostgreSQL gerenciado (AWS RDS, etc.)
- Configure S3 real (não MinIO)
- Use Redis gerenciado
- Configure CORS adequadamente

### 2. Variáveis de Ambiente

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

### 3. Comandos de Deploy

```bash
# Build para produção
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Migrações
docker-compose exec django_app python manage.py migrate
docker-compose exec django_app python manage.py collectstatic
```

## 🔧 Desenvolvimento

### Estrutura do Código

```
backend/
├── django_app/
│   ├── core/           # Configurações Django
│   ├── users/          # Autenticação e planos
│   ├── documents/      # Gestão de documentos
│   └── chat/           # Sistema de chat
├── fastapi_app/
│   ├── main.py         # App principal FastAPI
│   └── services/
│       ├── parser.py   # Extração de texto
│       └── ai.py       # Integração com IA
└── docker-compose.yml
```

## 📈 Monitoramento & Observabilidade

### **Health Checks**
```bash
# Django
curl http://localhost:8000/api/
curl http://localhost:8000/admin/

# FastAPI
curl http://localhost:8001/
curl http://localhost:8001/docs
curl http://localhost:8001/openapi.json
```

### **Logs & Debugging**
```bash
# Logs em tempo real
docker-compose logs -f django_app
docker-compose logs -f fastapi_app

# Logs específicos
docker-compose logs --tail=100 django_app

# Entrar no container para debug
docker-compose exec django_app bash
docker-compose exec fastapi_app bash
```

### **Métricas de Uso**
- Número de uploads por usuário
- Tokens de IA consumidos
- Sessões de chat ativas
- Tempo de resposta da API

## 🚀 Deploy em Produção

### **1. Preparação do Ambiente**
```bash
# Servidor com Docker
sudo apt update && sudo apt install docker docker-compose

# Configurar firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# SSL com Let's Encrypt (recomendado)
sudo apt install certbot python3-certbot-nginx
```

### **2. Configuração de Produção**
```env
# .env.production
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:pass@db:5432/jurchat
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-production-secret-key-very-long-and-random
ENCRYPTION_KEY=your-32-char-encryption-key

# OpenAI
OPENAI_API_KEY=sk-your-production-openai-key

# AWS S3 (opcional)
USE_S3=True
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=jurchat-prod
```

### **3. Deploy Steps**
```bash
# Clone no servidor
git clone https://github.com/MichelMeloG/backend-jurchat.git
cd backend-jurchat

# Configurar ambiente
cp .env.example .env.production
# Editar .env.production com valores reais

# Build e deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Configurar banco
docker-compose exec django_app python manage.py migrate
docker-compose exec django_app python manage.py collectstatic --noinput
docker-compose exec django_app python manage.py createsuperuser

# Verificar status
docker-compose ps
curl https://yourdomain.com/api/
```

### **4. Backup & Manutenção**
```bash
# Backup do banco
docker-compose exec postgres pg_dump -U postgres jurchat > backup.sql

# Backup de arquivos
tar -czf media_backup.tar.gz media/

# Atualização
git pull origin main
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contribuição

### **Como Contribuir**

1. **Fork** o repositório
2. **Clone** seu fork: `git clone https://github.com/seu-usuario/backend-jurchat.git`
3. **Crie uma branch**: `git checkout -b feature/nova-funcionalidade`
4. **Implemente** suas mudanças
5. **Teste** completamente
6. **Commit**: `git commit -m "Add: nova funcionalidade"`
7. **Push**: `git push origin feature/nova-funcionalidade`
8. **Abra um Pull Request**

### **Padrões de Código**

- **Python**: Seguir PEP 8
- **Django**: Boas práticas Django
- **FastAPI**: Async/await quando possível
- **Commits**: Conventional Commits
- **Testes**: Cobertura mínima 80%

### **Configuração para Desenvolvimento**

```bash
# Setup completo
git clone https://github.com/MichelMeloG/backend-jurchat.git
cd backend-jurchat
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Testes antes do commit
python -m pytest
python manage.py test
black .
flake8 .
```

### **Adicionando Novas Features**

1. **Modelos**: Adicione em `models.py` do app correspondente
2. **Serializers**: Configure em `serializers.py`
3. **Views**: Implemente em `views.py`
4. **URLs**: Registre em `urls.py`
5. **Migrations**: Execute `python manage.py makemigrations`

## 📞 Suporte & Contato

### **Links Úteis**
- 📚 **Documentação**: [Wiki do Projeto](https://github.com/MichelMeloG/backend-jurchat/wiki)
- 🐛 **Issues**: [GitHub Issues](https://github.com/MichelMeloG/backend-jurchat/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/MichelMeloG/backend-jurchat/discussions)

### **Contato**
- 👨‍💻 **Desenvolvedor**: [MichelMeloG](https://github.com/MichelMeloG)
- 📧 **Email**: seu-email@exemplo.com
- 💼 **LinkedIn**: [Seu LinkedIn](https://linkedin.com/in/seu-perfil)

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🏆 Status do Projeto

**✅ MVP Completo e Funcional**

- ✅ Autenticação JWT implementada
- ✅ Upload e processamento de documentos
- ✅ IA para extração e resumo de texto
- ✅ Sistema de chat contextual
- ✅ Controle de planos Free/Premium
- ✅ API REST documentada
- ✅ Microserviços Django + FastAPI
- ✅ Banco de dados modelado
- ✅ Segurança e criptografia
- ✅ Docker para deploy
- ✅ Documentação completa

**🚀 Pronto para produção e expansão!**

---

<div align="center">

**Feito com ❤️ para democratizar o acesso à análise de documentos jurídicos**

⭐ **Se este projeto foi útil, considere dar uma estrela!** ⭐

</div>