#include "coordinator.h"
#include <iostream>
#include <mutex>

// Конструктор класса CoordinatorServiceImpl
CoordinatorServiceImpl::CoordinatorServiceImpl() {
    // Изначально список заданий пуст, задания будут добавляться через SubmitTask
}

// Метод для получения задания воркером
grpc::Status CoordinatorServiceImpl::GetTask(grpc::ServerContext* context, const parser::TaskRequest* request, parser::TaskResponse* response) {
    std::lock_guard<std::mutex> lock(mu_);
    if (tasks.empty()) {
        response->set_has_task(false);
    } else {
        response->set_url(tasks.back());
        response->set_has_task(true);
        tasks.pop_back();
    }
    return grpc::Status::OK;
}

// Метод для получения результатов от воркеров
grpc::Status CoordinatorServiceImpl::ReportResult(grpc::ServerContext* context, const parser::TaskResult* result, parser::ResultAck* ack) {
    std::lock_guard<std::mutex> lock(mu_);
    std::cout << "Worker " << result->worker_id() << " completed task for URL " << result->url() 
              << " with result: " << result->result() << std::endl;
    ack->set_success(true);
    return grpc::Status::OK;
}

// Метод для добавления нового задания в очередь (получение URL-адреса от клиента)
grpc::Status CoordinatorServiceImpl::SubmitTask(grpc::ServerContext* context, const parser::SubmitTaskRequest* request, parser::SubmitTaskResponse* response) {
    std::lock_guard<std::mutex> lock(mu_);
    tasks.push_back(request->url());
    std::cout << "Received new task: " << request->url() << std::endl;
    response->set_success(true);
    return grpc::Status::OK;
}

// Реализация метода тестирования
// Реализация метода тестирования
void CoordinatorServiceImpl::testSubmitTask() {
    parser::SubmitTaskRequest request;
    parser::SubmitTaskResponse response;

    // Установите тестовый URL
    std::string test_url = "http://example.com/test-task";
    request.set_url(test_url);

    // Лог начальных данных
    std::cout << "[Debug] Test URL set: " << test_url << std::endl;

    // Создайте фиктивный контекст
    grpc::ServerContext context;

    // Лог начала вызова SubmitTask
    std::cout << "[Debug] Calling SubmitTask..." << std::endl;

    // Вызовите SubmitTask
    grpc::Status status = SubmitTask(&context, &request, &response);

    // Лог результата вызова SubmitTask
    if (status.ok()) {
        std::cout << "[Debug] SubmitTask completed successfully." << std::endl;
    } else {
        std::cout << "[Debug] SubmitTask failed. Error: " << status.error_message() << std::endl;
    }

    // Лог ответа от SubmitTask
    // std::cout << "[Debug] Response success flag: " << response.success() << std::endl;

    // // Проверка статуса выполнения SubmitTask
    if (status.ok() && response.success()) {
        std::cout << "[Test] Task submitted successfully: " << test_url << std::endl;

        // Дополнительно: Проверьте, что задача добавлена в очередь
        {
            std::lock_guard<std::mutex> lock(mu_);
            std::cout << "[Debug] Checking task queue..." << std::endl;

            if (!tasks.empty()) {
                std::cout << "[Debug] Task queue is not empty. Back task: " << tasks.back() << std::endl;
            } else {
                std::cout << "[Debug] Task queue is empty." << std::endl;
            }

            if (!tasks.empty() && tasks.back() == test_url) {
                std::cout << "[Test] Task successfully added to the queue." << std::endl;
            } else {
                std::cout << "[Test] Task was not added to the queue as expected." << std::endl;
            }
        }
    } else {
        std::cout << "[Test] Task submission failed!" << std::endl;
        std::cout << "[Test] gRPC Status: " << status.error_message() << std::endl;
    }
}

