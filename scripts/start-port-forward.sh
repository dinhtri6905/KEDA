#!/bin/bash

RABBITMQ_SVC="svc/rabbitmq"
NAMESPACE="messaging"
LOCAL_PORT="5673"
REMOTE_PORT="5672"
PID_FILE="/tmp/rabbitmq-pf.pid"

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "[INFO] Port-forward is already running with PID: $OLD_PID"
        exit 0
    else
        rm "$PID_FILE"
    fi
fi

echo "[INFO] Starting port-forward for RabbitMQ ($LOCAL_PORT:$REMOTE_PORT)..."

nohup kubectl port-forward -n "$NAMESPACE" "$RABBITMQ_SVC" "$LOCAL_PORT:$REMOTE_PORT" > /dev/null 2>&1 &
NEW_PID=$!

sleep 2

if ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "$NEW_PID" > "$PID_FILE"
    echo "[SUCCESS] Connected! RabbitMQ available at localhost:$LOCAL_PORT (PID: $NEW_PID)"
else
    echo "[ERROR] Failed to start port-forward. Please check kubectl connectivity."
    exit 1
fi