#include "worker.h"
#include <thread>
#include <chrono>
#include <iostream>

int main(int argc, char** argv) {
    WorkerClient worker(grpc::CreateChannel("coordinator:50051", grpc::InsecureChannelCredentials()));

    while (true) {
        // Получение задания от координатора
        std::string taskUrl = worker.GetTask();
        if (!taskUrl.empty()) {
            // Обработка задания
            processTask(worker, taskUrl);
        } else {
            // Если нет задания, ждем немного перед следующим запросом
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
    }

    return 0;
}
