#ifndef WORKER_H
#define WORKER_H

#include <grpcpp/grpcpp.h>
#include "/app/generated/task.grpc.pb.h"
#include "/app/generated/task.pb.h"

class WorkerClient {
public:
    WorkerClient(std::shared_ptr<grpc::Channel> channel);

    std::string GetTask();
    void ReportResult(const std::string& url, const std::string& result);

private:
    std::unique_ptr<parser::Coordinator::Stub> stub_;
};

void processTask(WorkerClient& worker, const std::string& taskUrl);
#endif // WORKER_H
