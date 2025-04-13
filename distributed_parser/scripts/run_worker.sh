#!/bin/bash

# Переменные среды
export $(grep -v '^#' ../.env | xargs)

# Определяем путь к воркеру
WORKER_PATH="../build/worker"

# Проверяем, существует ли исполняемый файл воркера
if [ ! -f "$WORKER_PATH" ]; then
    echo "Error: Worker executable not found. Please run build_all.sh first."
    exit 1
fi

# Запуск воркера
echo "Starting Worker on port ${WORKER_PORT}..."
$WORKER_PATH
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Worker"
    exit 1
fi
