#!/bin/bash

# Переменные среды
export $(grep -v '^#' ../.env | xargs)

# Переключаемся в папку coordinator и собираем координатор
echo "Building Coordinator..."
cd ../coordinator
make clean && make
if [ $? -ne 0 ]; then
    echo "Error: Failed to build Coordinator"
    exit 1
fi
echo "Coordinator built successfully!"

# Переключаемся в папку worker и собираем воркера
echo "Building Worker..."
cd ../worker
make clean && make
if [ $? -ne 0 ]; then
    echo "Error: Failed to build Worker"
    exit 1
fi
echo "Worker built successfully!"

# Переключаемся обратно
cd ..

echo "All components have been built successfully!"
