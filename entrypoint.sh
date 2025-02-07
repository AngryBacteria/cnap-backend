#!/bin/bash

if [ "$RUN_TYPE" = "task" ]; then
    echo "Running Periodic Updates"
    /home/dockeruser/workspace/venv/bin/python tasks/MainTask.py
else
    echo "Starting FastAPI Backend"
    /home/dockeruser/workspace/venv/bin/fastapi run api/main.py
fi