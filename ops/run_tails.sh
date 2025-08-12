#!/usr/bin/env bash
# run_tails.sh - run in Tails persistent environment
export TEST_MODE=0
export INGEST_HOST=127.0.0.1
export INGEST_PORT=8000
# start ingest
uvicorn ingest.app:app --reload --host 127.0.0.1 --port 8000 &
sleep 2
# start worker
python3 processor/worker.py &
sleep 2
# start tor crawler
python3 crawler/tor_crawler_tails.py

