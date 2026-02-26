#!/bin/bash

PID_FILE="/tmp/rabbitmq-pf.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    echo "[INFO] Stopping RabbitMQ port-forward (PID: $PID)..."
    
    kill "$PID" 2>/dev/null
    rm "$PID_FILE"
    
    echo "[SUCCESS] Port-forward stopped."
else
    echo "[WARNING] No PID file found. Checking for lingering processes..."
    
    PIDS=$(pgrep -f "kubectl port-forward.*5673:5672")
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill
        echo "[SUCCESS] Stopped lingering processes: $PIDS"
    else
        echo "[INFO] No running port-forward processes found."
    fi
fi