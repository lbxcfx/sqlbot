# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SQLBot is an intelligent text-to-SQL system based on Large Language Models (LLM) and Retrieval-Augmented Generation (RAG). It enables natural language querying of databases with built-in workspace isolation and fine-grained data permissions.

**Architecture**: Full-stack application with:
- **Backend**: FastAPI (Python) - Main app on port 8000, MCP server on port 8001
- **Frontend**: Vue 3 + TypeScript + Element Plus + Vite
- **Database**: PostgreSQL (primary) with support for multiple datasource types
- **Chart Rendering**: Node.js G2-SSR service for server-side chart generation
- **Embedding**: text2vec-base-chinese for semantic search and RAG

## Development Commands

### Backend (FastAPI)

**Running the application**:
```bash
# From backend/ directory
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run MCP server (separate process)
uvicorn main:mcp_app --host 0.0.0.0 --port 8001
```

**Database migrations** (Alembic):
```bash
# From backend/ directory
alembic upgrade head              # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic downgrade -1              # Rollback one migration
```

**Key environment variables** (see docker-compose.yaml for full list):
- `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `SECRET_KEY` - JWT token signing
- `DEFAULT_PWD` - Default admin password (SQLBot@123456)
- `SERVER_IMAGE_HOST` - MCP server image hosting URL
- `EMBEDDING_ENABLED` - Enable/disable RAG embeddings
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

### Frontend (Vue 3)

```bash
# From frontend/ directory
npm install                # Install dependencies
npm run dev                # Development server (with type checking)
npm run build              # Production build
npm run lint               # ESLint with auto-fix
```

### G2-SSR (Chart Server)

```bash
# From g2-ssr/ directory
npm install
node app.js                # Runs on port 3000
```

### Docker

```bash
# Single container deployment (includes PostgreSQL, backend, frontend, G2-SSR)
docker run -d --name sqlbot -p 8000:8000 -p 8001:8001 dataease/sqlbot

# Docker Compose
docker-compose up -d
docker-compose logs -f sqlbot
```

Default credentials: `admin` / `SQLBot@123456`

## Code Architecture

### Backend Structure (`backend/`)

**Main application** (`main.py`):
- Two FastAPI apps: `app` (main API) and `mcp_app` (MCP server for AI agent integration)
- Startup lifecycle: runs migrations → initializes cache → loads dynamic CORS → fills embeddings
- Uses `fastapi-mcp` for exposing specific operations as MCP tools
- Middleware stack: CORS → Token auth → Response formatting

**Core modules** (`common/core/`):
- `config.py` - Pydantic settings with environment variable loading
- `db.py` - SQLAlchemy async session management
- `security.py` - JWT token generation and password hashing
- `deps.py` - FastAPI dependencies (CurrentUser, CurrentAssistant, session injection)
- `sqlbot_cache.py` - Pluggable cache (Redis or in-memory)
- `models.py` - Base SQLModel classes
- `pagination.py` - Pagination utilities

**App structure** (`apps/`):
Each app follows the pattern: `models/` → `crud/` → `api/` → `task/`
- **system**: User, workspace, AI model, assistant management
- **datasource**: Database connections, table/field metadata, SQL execution
- **chat**: Q&A sessions, streaming LLM responses, chart generation
- **terminology**: Business term definitions for RAG context
- **data_training**: Training data for improving text-to-SQL accuracy
- **dashboard**: Dashboard creation and management
- **mcp**: MCP protocol endpoints for external integrations

**LLM integration** (`apps/ai_model/`):
- `model_factory.py` - Factory for creating LLM clients (OpenAI, Claude, etc.)
- `llm.py` - Unified LLM interface with streaming support
- `embedding.py` - Embedding model management for RAG

**Database engine** (`apps/db/`):
- `engine.py` - SQLAlchemy engine creation for various database types
- `db.py` - Database metadata extraction (tables, columns, constraints)
- `db_sql.py` - SQL generation and execution
- `es_engine.py` - Elasticsearch integration (if enabled)

**Chat flow** (`apps/chat/task/llm.py`):
The LLMService class orchestrates the full text-to-SQL pipeline:
1. Load datasource metadata and permissions
2. Retrieve relevant terminology via embedding search
3. Retrieve similar training examples via embedding search
4. Construct prompt with context
5. Stream LLM response with SQL generation
6. Execute SQL and return results
7. Optionally generate charts

### Frontend Structure (`frontend/src/`)

**Main views**:
- `views/chat/` - Chat interface with streaming responses, SQL display, charts
- `views/ds/` - Datasource management (connection, table selection, field configuration)
- `views/system/` - Admin panels (users, workspaces, AI models, embeddings, permissions)
- `views/dashboard/` - Dashboard editor and preview
- `views/embedded/` - Assistant embedding for third-party integration

**State management** (Pinia stores in `src/store/` - inferred):
- User authentication state
- Workspace context
- Chat session state

**API client** (Axios wrapper in `src/api/` - inferred):
- Centralized HTTP client with token injection
- Request/response interceptors

**Router** (`src/router/index.ts`):
- Vue Router with authentication guards
- Lazy-loaded route components

### Database Schema

**Key tables** (see `backend/alembic/versions/`):
- `user` - User accounts
- `workspace` - Multi-tenancy workspaces
- `user_ws` - User-workspace associations
- `core_datasource` - Database connections
- `core_table`, `core_field` - Datasource metadata
- `core_permission` - Row/column-level permissions
- `chat`, `chat_record` - Q&A sessions and history
- `terminology` - Business terms with embeddings
- `data_training` - Training examples with embeddings
- `ai_model` - LLM and embedding model configurations
- `assistant` - Embedded assistant configurations

**Migrations**:
- All migrations are in `backend/alembic/versions/`
- Naming convention: `{number}_{description}.py`
- Run automatically on app startup via `run_migrations()` in main.py

## Important Implementation Details

**RAG/Embedding System**:
- Embeddings are computed asynchronously via `common/utils/embedding_threads.py`
- Two types: terminology embeddings and data training embeddings
- Configurable similarity thresholds and top-K counts in settings
- Used to retrieve relevant context before LLM prompt construction

**Security**:
- JWT tokens with configurable expiration (default 8 days)
- Password hashing with bcrypt
- Row-level and column-level permissions enforced in SQL generation
- Workspace isolation for multi-tenancy
- Sensitive data (API keys, passwords) encrypted via `common/utils/crypto.py`

**MCP Integration**:
FastAPI-MCP exposes these operations for AI agent platforms (n8n, Dify, Coze):
- `mcp_start` - Authenticate and create chat session
- `get_datasource_list` - List available datasources
- `get_model_list` - List configured LLMs
- `mcp_question` - Submit question and get streaming response
- `mcp_assistant` - Assistant-specific endpoints

**Chart Generation**:
- G2-SSR (Node.js) renders charts server-side as base64 images
- Chart types: line, bar, column, pie (in `g2-ssr/charts/`)
- Images saved to `MCP_IMAGE_PATH` and served via MCP server

**SQL Execution Safety**:
- Read-only queries enforced for non-admin users
- Query timeout configured per datasource
- Permission filters automatically injected into WHERE clauses

## Testing

No test framework is currently configured. When adding tests:
- Backend: Use pytest with async support
- Frontend: Use Vitest (Vite's native test runner)

## Common Gotchas

- The backend expects to be run from the `backend/` directory due to relative paths in config
- Alembic migrations run automatically on startup, but you need to generate them manually
- The frontend build is embedded in the Docker image, not served separately in production
- G2-SSR must be running for chart features to work
- Embedding model downloads on first startup (can be slow without pre-cached models)
- Database connection strings are sensitive - PostgreSQL passwords must be URL-encoded