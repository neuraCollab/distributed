cmake_minimum_required(VERSION 3.15)

# Название проекта
project(Coordinator LANGUAGES CXX)

# Установка версии стандарта C++
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -D_GLIBCXX_USE_CXX11_ABI=0")

# Параметры для сборки
set(CMAKE_BUILD_TYPE Release)

# Пути для поиска сторонних библиотек
include_directories(
    .
    /app/generated
    /usr/local/include
    /usr/include
)

# Найти зависимости
find_package(CURL REQUIRED)
find_package(LibXml2 REQUIRED)
find_package(Protobuf CONFIG REQUIRED)
find_package(gRPC CONFIG REQUIRED)

if(NOT Protobuf_FOUND)
    message(FATAL_ERROR "Failed to find Protobuf!")
else()
    message(STATUS "Using Protobuf ${Protobuf_VERSION}")
endif()

if(NOT gRPC_FOUND)
    message(FATAL_ERROR "Failed to find gRPC!")
else()
    message(STATUS "Using gRPC ${gRPC_VERSION}")
endif()

# Источники проекта
set(SOURCES
    main.cpp
    coordinator.cpp
    /app/generated/task.pb.cc
    /app/generated/task.grpc.pb.cc
)

# Создание исполняемого файла
add_executable(coordinator ${SOURCES})

# Линковка библиотек
target_link_libraries(coordinator
    gRPC::grpc++
    gRPC::grpc++_reflection
    protobuf::libprotobuf
    absl::strings  # Если используется gRPC 1.44+ и требуется Abseil
    ${CURL_LIBRARIES}
    ${LIBXML2_LIBRARIES}
    pthread
)

# Указание include-директорий
target_include_directories(coordinator PRIVATE
    ${CURL_INCLUDE_DIRS}
    ${LIBXML2_INCLUDE_DIRS}
    ${Protobuf_INCLUDE_DIRS}
    ${gRPC_INCLUDE_DIRS}
)
