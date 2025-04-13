#!/bin/bash

# Переменные среды
export $(grep -v '^#' ../.env | xargs)

# Определяем путь к координатору
COORDINATOR_PATH="../build/coordinator"

# Проверяем, существует ли исполняемый файл координатора
if [ ! -f "$COORDINATOR_PATH" ]; then
    echo "Error: Coordinator executable not found. Please run build_all.sh first."
    exit 1
fi

# Запуск координатора
echo "Starting Coordinator on port ${COORDINATOR_PORT}..."
$COORDINATOR_PATH
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Coordinator"
    exit 1
fi
