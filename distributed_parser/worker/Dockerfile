FROM prestart:latest

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    cmake \
    git \
    libssl-dev \
    libuv1-dev \
    zlib1g-dev \
    curl \
    libcurl4-openssl-dev \
    libxml2-dev \
    protobuf-compiler \
    libprotobuf-dev

# Клонирование и установка DataStax C/C++ Driver
RUN git clone https://github.com/datastax/cpp-driver.git /tmp/cpp-driver && \
    mkdir -p /tmp/cpp-driver/build && \
    cd /tmp/cpp-driver/build && \
    cmake .. && \
    make && \
    make install && \
    ldconfig

# Копирование исходного кода
WORKDIR /app
COPY . .

# Сборка проекта
RUN mkdir -p build && \
    cd build && \
    cmake .. && \
    make -j$(nproc)

# Открытие порта
EXPOSE 50051

# Команда запуска
CMD ["./build/worker"]
