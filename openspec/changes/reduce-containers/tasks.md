# Tasks: Redução de Topologia de Containers

Esta mudança consolida a infraestrutura removendo containers redundantes e mergeando o microserviço de matching no backend principal.

## Tarefa 1: Refatoração de Backend (API + Matching)
- [ ] Mover código de `./apps/matching` para `./apps/api/app/matching`
- [ ] Criar módulo `engine.py` no backend para chamadas de função direta
- [ ] Atualizar `requirements.txt` da API com `lightgbm` e `libgomp1`
- [ ] Implementar abstração `IStorage` com provedor de filesystem local (`aiofiles`)
- [ ] Configurar FastAPI `StaticFiles` para servir a pasta `./uploads` em dev

## Tarefa 2: Consolidação de Banco de Dados (PostgreSQL)
- [ ] Criar script de migração para adicionar `tsvector` à tabela `professionals`
- [ ] Implementar trigger para atualização automática do `tsvector` no banco
- [ ] Criar índices `pg_trgm` para fuzzy search
- [ ] Atualizar queries de busca no `search_service.py` para usar PostGIS + FTS nativo

## Tarefa 3: Orquestração Docker & Cleanup
- [ ] Atualizar `docker-compose.yml` (remover `typesense`, `minio`, `matching`, `otel-collector`)
- [ ] Remover rede `backend` do compose
- [ ] Adicionar volumes bind mount para `./uploads` e `./models` no serviço `api`
- [ ] Limpar variáveis de ambiente obsoletas do `.env.example`

## Tarefa 4: Verificação & Testes
- [ ] Validar matching via chamada de função (unit tokens)
- [ ] Validar busca com PostGIS + FTS (integração)
- [ ] Validar upload de imagens para filesystem local
- [ ] Testar startup completo com `docker compose up` reduzido
