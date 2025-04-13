# Используем базовый образ
FROM prestart:latest

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем исходный код проекта в контейнер
COPY . .  

# Сборка проекта
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make -j$(nproc)

# Открываем порт для приложения
EXPOSE 50051

# Устанавливаем точку входа, чтобы контейнер не завершал выполнение
# CMD ["/bin/bash"]
CMD [ "./build/coordinator" ]
