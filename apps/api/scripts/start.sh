#!/bin/sh

# Instala shapely especificamente se necessário (como solicitado pelo usuário)
# Ou melhor, garante que tudo do requirements.txt esteja instalado
pip install shapely==2.1.2

# Inicia o servidor uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
