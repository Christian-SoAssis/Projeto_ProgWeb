# Proposal: Cobertura de Testes e Execução em Container

## Motivação
Desenvolvedores precisam garantir que o código novo seja testado antes do merge. Cobertura de testes é uma métrica fundamental para saúde do projeto.

## Impacto
- **Qualidade**: Garantia de que pelo menos 50% do código seja coberto por testes.
- **Ambiente**: Otimização do pipeline de testes rodando em container.

## Solução
Implementação de `pytest-cov` e criação de script de automatização de testes com falha automática para cobertura baixa.
