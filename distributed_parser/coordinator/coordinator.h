#ifndef COORDINATOR_H
#define COORDINATOR_H

#include <grpcpp/grpcpp.h>
#include "/app/generated/task.pb.h" 
#include "/app/generated/task.grpc.pb.h"
#include <vector>
#include <string>
#include <mutex>

class CoordinatorServiceImpl final : public parser::Coordinator::Service {
public:
    CoordinatorServiceImpl();

    grpc::Status GetTask(grpc::ServerContext* context, const parser::TaskRequest* request, parser::TaskResponse* response) override;
    grpc::Status ReportResult(grpc::ServerContext* context, const parser::TaskResult* result, parser::ResultAck* ack) override;
    grpc::Status SubmitTask(grpc::ServerContext* context, const parser::SubmitTaskRequest* request, parser::SubmitTaskResponse* response) override;

    // Метод для тестирования SubmitTask
    void testSubmitTask();

private:
    std::vector<std::string> tasks;  // Очередь заданий
    std::mutex mu_;  // Мьютекс для синхронизации доступа к очереди заданий
};

#endif // COORDINATOR_H
