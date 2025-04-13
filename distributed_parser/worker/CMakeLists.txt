# Установка минимальной версии CMake
cmake_minimum_required(VERSION 3.15)

# Название проекта
project(Worker LANGUAGES CXX)

# Установка стандарта C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Установка типа сборки
set(CMAKE_BUILD_TYPE Release)

# Пути для поиска заголовочных файлов
include_directories(
    ${CMAKE_SOURCE_DIR}
    /usr/include
    /usr/local/include
)

# Поиск зависимостей
find_package(Protobuf REQUIRED)
find_package(gRPC CONFIG REQUIRED)
find_package(CURL REQUIRED)
find_package(LibXml2 REQUIRED)

# Добавление пути к установленным библиотекам
link_directories(/usr/local/lib)

# Источники проекта
set(SOURCES
    main.cpp
    worker.cpp
    page_fetcher.cpp
    html_parser.cpp
    /app/generated/task.pb.cc
    /app/generated/task.grpc.pb.cc
)

# Создание исполняемого файла
add_executable(worker ${SOURCES})

# Линковка с библиотеками
target_link_libraries(worker
    gRPC::grpc++
    protobuf::libprotobuf
    ${CURL_LIBRARIES}
    ${LIBXML2_LIBRARIES}
    cassandra
    pthread
)

# Установка директорий с заголовочными файлами
target_include_directories(worker PRIVATE
    ${CURL_INCLUDE_DIRS}
    ${LIBXML2_INCLUDE_DIRS}
    ${Protobuf_INCLUDE_DIRS}
    /usr/local/include
)
