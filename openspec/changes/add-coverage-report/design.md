# Design: Cobertura de Testes e Execução em Container

## Arquitetura
O sistema de testes utilizará `pytest` com o plugin `pytest-cov`.
A execução será orquestrada via Docker Compose.

## Componentes
- **pytest-cov**: Plugin para coleta de dados de cobertura.
- **Docker Compose**: Para execução isolada e reprodutível.
- **Shell Script**: Para abstrair a complexidade do comando e tratar os resultados.

## Fluxo
1. Carregar container `api`.
2. Rodar `pytest` com flags de cobertura.
3. Verificar se a cobertura final atende ao limite de 50%.
4. Reportar resultados no console.
