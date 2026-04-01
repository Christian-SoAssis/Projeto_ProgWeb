# Tasks: Redução de Topologia de Containers

Esta mudança consolida a infraestrutura removendo containers redundantes e mergeando o microserviço de matching no backend principal.

## Tarefa 1: Refatoração de Backend (API + Matching)
- [x] Mover código de `./apps/matching` para `./apps/api/app/matching`
- [x] Criar módulo `engine.py` no backend para chamadas de função direta
- [x] Atualizar `requirements.txt` da API com `lightgbm` e `libgomp1`
- [x] Implementar abstração `IStorage` com provedor de filesystem local (`aiofiles`)
- [x] Configurar FastAPI `StaticFiles` para servir a pasta `./uploads` em dev

## Tarefa 2: Consolidação de Banco de Dados (PostgreSQL)
- [x] Criar script de migração para adicionar `tsvector` à tabela `professionals`
- [x] Implementar trigger para atualização automática do `tsvector` no banco
- [x] Criar índices `pg_trgm` para fuzzy search
- [x] Atualizar queries de busca no `search_service.py` para usar PostGIS + FTS nativo

## Tarefa 3: Orquestração Docker & Cleanup
- [x] Atualizar `docker-compose.yml` (remover `typesense`, `minio`, `matching`, `otel-collector`)
- [x] Remover rede `backend` do compose
- [x] Adicionar volumes bind mount para `./uploads` e `./models` no serviço `api`
- [x] Limpar variáveis de ambiente obsoletas do `.env.example`

## Tarefa 4: Verificação & Testes
- [x] Validar matching via chamada de função (unit tokens)
- [x] Validar busca com PostGIS + FTS (integração)
- [x] Validar upload de imagens para filesystem local
- [x] Testar startup completo com `docker compose up` reduzido
