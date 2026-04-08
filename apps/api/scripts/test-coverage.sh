#!/bin/bash
set -e

# Executa os testes com cobertura
# --cov=app: indica o diretório de código a ser medido
# --cov-report=term-missing: mostra as linhas não cobertas no terminal
# --cov-fail-under=50: falha se a cobertura for inferior a 50%
pytest --cov=app --cov-report=term-missing --cov-fail-under=50 tests/
