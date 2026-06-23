#!/bin/sh

# Inicia o worker arq em segundo plano
arq app.core.worker.WorkerSettings &

# Inicia o servidor uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT

