# Spec: search-discovery

> **Convenção de linguagem**: Este documento segue o padrão RFC 2119.  
> **MUST / SHALL** = obrigatório | **SHOULD** = recomendado | **MAY** = opcional.

---

## Requirement: Busca geo + full-text de profissionais

O sistema **SHALL** permitir busca de profissionais por localização geográfica, categoria e texto livre, retornando apenas profissionais verificados.

### Scenario 1 — Busca por localização e categoria retorna resultados

- **GIVEN** que profissionais verificados existem dentro do raio e da categoria informada
- **WHEN** o usuário envia `GET /search/professionals?lat=-23.5&lng=-46.6&category=encanamento&radius_km=20`
- **THEN** o sistema **MUST** retornar lista de profissionais com `is_verified=true` dentro do raio, ordenados por relevância (Typesense score + `reputation_score`); resposta **MUST** incluir `distance_km` por profissional

### Scenario 2 — Busca sem resultados

- **GIVEN** que nenhum profissional atende os filtros informados
- **WHEN** a busca é executada
- **THEN** o sistema **MUST** retornar lista vazia `[]`; **SHOULD** incluir mensagem sugerindo ampliar `radius_km` ou alterar categoria

### Scenario 3 — Parâmetros de coordenadas inválidos

- **GIVEN** que `lat` ou `lng` estão fora dos intervalos válidos (`lat ∈ [-90, 90]`, `lng ∈ [-180, 180]`)
- **WHEN** a requisição chega ao FastAPI
- **THEN** o sistema **MUST** retornar `422 Unprocessable Entity` com detalhe nos campos inválidos

### Scenario 4 — Typesense indisponível

- **GIVEN** que o serviço Typesense não responde
- **WHEN** a busca é encaminhada ao Typesense
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`; **MAY** fazer fallback para query PostgreSQL com PostGIS como degradação graceful, logando o evento

### Scenario 5 — PostgreSQL indisponível (sem fallback disponível)

- **GIVEN** que tanto o Typesense quanto o PostgreSQL estão inacessíveis
- **WHEN** a busca é executada
- **THEN** o sistema **MUST** retornar `503 Service Unavailable`

---

## Requirement: Busca full-text em PT-BR

O sistema **SHALL** indexar `name`, `bio` e `specialties` dos profissionais verificados no Typesense com suporte a variações morfológicas em português.

### Scenario 1 — Busca por texto livre com resultado

- **GIVEN** que profissionais indexados possuem o termo (ou variação) em seus campos
- **WHEN** o usuário envia `GET /search/professionals?q=hidráulica`
- **THEN** o Typesense **MUST** retornar profissionais com correspondência no `name`, `bio` ou `categories`, com highlight nos termos encontrados; profissionais com `is_verified=false` **MUST NOT** aparecer nos resultados

### Scenario 2 — Busca com termo sem correspondência

- **GIVEN** que nenhum profissional indexado possui o termo pesquisado
- **WHEN** a busca é executada
- **THEN** o sistema **MUST** retornar lista vazia; **SHOULD** sugerir termos relacionados se disponíveis via Typesense

---

## Requirement: Mapa interativo de profissionais

O sistema **SHALL** exibir profissionais disponíveis em mapa com clustering, consumindo dados da mesma API de busca geo.

### Scenario 1 — Carregamento do mapa com profissionais

- **GIVEN** que o usuário está na página de busca e a geolocalização do browser foi concedida (ou coords manuais fornecidas)
- **WHEN** o front-end carrega a view de mapa
- **THEN** o sistema **MUST** exibir pins de profissionais disponíveis na área visível; pins **MUST** usar clustering para densidades altas; cada pin **MUST** exibir nome, foto e `reputation_score` ao ser clicado

### Scenario 2 — Acesso sem permissão de geolocalização

- **GIVEN** que o usuário nega permissão de geolocalização no browser
- **WHEN** o mapa tenta obter coordenadas
- **THEN** a UI **MUST** exibir campo de busca por endereço manual como alternativa; **MUST NOT** travar nem mostrar erro genérico

---

## Requirement: Indexação em tempo real (Typesense)

O sistema **SHALL** atualizar o índice do Typesense sempre que um profissional for aprovado ou atualizar seu perfil.

### Scenario 1 — Profissional aprovado pelo admin

- **GIVEN** que o admin aprova profissional com `is_verified=false`
- **WHEN** o status é atualizado para `is_verified=true` no PostgreSQL
- **THEN** o sistema **MUST** enfileirar job de indexação; o worker **MUST** indexar o profissional no Typesense com localização, categorias e `reputation_score` em até 5 s

### Scenario 2 — Profissional atualiza bio, localização ou categorias

- **GIVEN** que o profissional autenticado envia `PATCH /professionals/me` com dados atualizados
- **WHEN** a atualização é persistida no PostgreSQL
- **THEN** o worker **MUST** atualizar o documento no Typesense em até 5 s

### Scenario 3 — Typesense indisponível durante indexação

- **GIVEN** que o Typesense não responde ao request de indexação
- **WHEN** o worker tenta indexar
- **THEN** o worker **MUST** retentar até 3× com backoff exponencial; após falhas, **MUST** logar o evento para reprocessamento; a atualização no PostgreSQL **MUST** ter sido persistida independentemente da falha de indexação

### Scenario 4 — Profissional desativado ou rejeitado após indexação

- **GIVEN** que um profissional previamente indexado é desativado ou rejeitado pelo admin
- **WHEN** o status é atualizado no PostgreSQL
- **THEN** o sistema **MUST** remover o documento do Typesense em até 5 s; o profissional **MUST NOT** aparecer em resultados de busca após remoção
