# Spec: search-discovery

## ADDED Requirements

### Requirement: Busca geo + full-text de profissionais
O sistema SHALL permitir busca de profissionais por localização, categoria e texto livre.

#### Scenario: Busca por localização e categoria
- **WHEN** usuário envia GET /search/professionals?lat=-23.5&lng=-46.6&category=encanamento&radius_km=20
- **THEN** sistema retorna profissionais verificados dentro do raio, ordenados por relevância (Typesense + reputation_score)

#### Scenario: Busca sem resultado
- **WHEN** nenhum profissional atende os filtros de busca
- **THEN** sistema retorna lista vazia e sugestão de ampliar raio ou categoria

---

### Requirement: Busca full-text em PT-BR
O sistema SHALL indexar nome, bio e especialidades dos profissionais no Typesense.

#### Scenario: Busca por texto livre
- **WHEN** usuário envia GET /search/professionals?q=hidráulica
- **THEN** Typesense retorna profissionais com "hidráulica" (ou variações) no nome, bio ou categorias, com highlight nos termos encontrados

---

### Requirement: Mapa interativo de profissionais
O sistema SHALL exibir profissionais em mapa com clustering de pontos.

#### Scenario: Carregamento do mapa
- **WHEN** usuário acessa a página de busca com mapa
- **THEN** sistema exibe mapa com pins de profissionais disponíveis na área visível

---

### Requirement: Indexação em tempo real (Typesense)
O sistema SHALL atualizar o índice do Typesense quando profissional atualiza perfil ou é verificado.

#### Scenario: Profissional aprovado indexado
- **WHEN** admin aprova profissional (is_verified=true)
- **THEN** worker indexa profissional no Typesense com localização, categorias e scores

#### Scenario: Profissional atualiza perfil
- **WHEN** profissional atualiza bio, localização ou categorias
- **THEN** worker atualiza documento no Typesense em até 5s
