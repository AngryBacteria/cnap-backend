#!/bin/bash

if [ "$RUN_TYPE" = "task" ]; then
    echo "Running Periodic Updates"
    python tasks/MainTask.py
else
    echo "Starting FastAPI Backend"
    fastapi run api/main.py
fi