// Generated by the gRPC C++ plugin.
// If you make any local change, they will be lost.
// source: task.proto
#ifndef GRPC_task_2eproto__INCLUDED
#define GRPC_task_2eproto__INCLUDED

#include "task.pb.h"

#include <functional>
#include <grpcpp/impl/codegen/async_generic_service.h>
#include <grpcpp/impl/codegen/async_stream.h>
#include <grpcpp/impl/codegen/async_unary_call.h>
#include <grpcpp/impl/codegen/client_callback.h>
#include <grpcpp/impl/codegen/client_context.h>
#include <grpcpp/impl/codegen/completion_queue.h>
#include <grpcpp/impl/codegen/message_allocator.h>
#include <grpcpp/impl/codegen/method_handler.h>
#include <grpcpp/impl/codegen/proto_utils.h>
#include <grpcpp/impl/codegen/rpc_method.h>
#include <grpcpp/impl/codegen/server_callback.h>
#include <grpcpp/impl/codegen/server_callback_handlers.h>
#include <grpcpp/impl/codegen/server_context.h>
#include <grpcpp/impl/codegen/service_type.h>
#include <grpcpp/impl/codegen/status.h>
#include <grpcpp/impl/codegen/stub_options.h>
#include <grpcpp/impl/codegen/sync_stream.h>

namespace parser {

class Coordinator final {
 public:
  static constexpr char const* service_full_name() {
    return "parser.Coordinator";
  }
  class StubInterface {
   public:
    virtual ~StubInterface() {}
    virtual ::grpc::Status GetTask(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::parser::TaskResponse* response) = 0;
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::TaskResponse>> AsyncGetTask(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::TaskResponse>>(AsyncGetTaskRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::TaskResponse>> PrepareAsyncGetTask(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::TaskResponse>>(PrepareAsyncGetTaskRaw(context, request, cq));
    }
    virtual ::grpc::Status ReportResult(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::parser::ResultAck* response) = 0;
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::ResultAck>> AsyncReportResult(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::ResultAck>>(AsyncReportResultRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::ResultAck>> PrepareAsyncReportResult(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::ResultAck>>(PrepareAsyncReportResultRaw(context, request, cq));
    }
    virtual ::grpc::Status SubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::parser::SubmitTaskResponse* response) = 0;
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::SubmitTaskResponse>> AsyncSubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::SubmitTaskResponse>>(AsyncSubmitTaskRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::SubmitTaskResponse>> PrepareAsyncSubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReaderInterface< ::parser::SubmitTaskResponse>>(PrepareAsyncSubmitTaskRaw(context, request, cq));
    }
    // Новый метод для отправки URL-адреса
    class async_interface {
     public:
      virtual ~async_interface() {}
      virtual void GetTask(::grpc::ClientContext* context, const ::parser::TaskRequest* request, ::parser::TaskResponse* response, std::function<void(::grpc::Status)>) = 0;
      virtual void GetTask(::grpc::ClientContext* context, const ::parser::TaskRequest* request, ::parser::TaskResponse* response, ::grpc::ClientUnaryReactor* reactor) = 0;
      virtual void ReportResult(::grpc::ClientContext* context, const ::parser::TaskResult* request, ::parser::ResultAck* response, std::function<void(::grpc::Status)>) = 0;
      virtual void ReportResult(::grpc::ClientContext* context, const ::parser::TaskResult* request, ::parser::ResultAck* response, ::grpc::ClientUnaryReactor* reactor) = 0;
      virtual void SubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest* request, ::parser::SubmitTaskResponse* response, std::function<void(::grpc::Status)>) = 0;
      virtual void SubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest* request, ::parser::SubmitTaskResponse* response, ::grpc::ClientUnaryReactor* reactor) = 0;
      // Новый метод для отправки URL-адреса
    };
    typedef class async_interface experimental_async_interface;
    virtual class async_interface* async() { return nullptr; }
    class async_interface* experimental_async() { return async(); }
   private:
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::parser::TaskResponse>* AsyncGetTaskRaw(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::grpc::CompletionQueue* cq) = 0;
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::parser::TaskResponse>* PrepareAsyncGetTaskRaw(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::grpc::CompletionQueue* cq) = 0;
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::parser::ResultAck>* AsyncReportResultRaw(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::grpc::CompletionQueue* cq) = 0;
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::parser::ResultAck>* PrepareAsyncReportResultRaw(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::grpc::CompletionQueue* cq) = 0;
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::parser::SubmitTaskResponse>* AsyncSubmitTaskRaw(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::grpc::CompletionQueue* cq) = 0;
    virtual ::grpc::ClientAsyncResponseReaderInterface< ::parser::SubmitTaskResponse>* PrepareAsyncSubmitTaskRaw(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::grpc::CompletionQueue* cq) = 0;
  };
  class Stub final : public StubInterface {
   public:
    Stub(const std::shared_ptr< ::grpc::ChannelInterface>& channel, const ::grpc::StubOptions& options = ::grpc::StubOptions());
    ::grpc::Status GetTask(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::parser::TaskResponse* response) override;
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::TaskResponse>> AsyncGetTask(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::TaskResponse>>(AsyncGetTaskRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::TaskResponse>> PrepareAsyncGetTask(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::TaskResponse>>(PrepareAsyncGetTaskRaw(context, request, cq));
    }
    ::grpc::Status ReportResult(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::parser::ResultAck* response) override;
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::ResultAck>> AsyncReportResult(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::ResultAck>>(AsyncReportResultRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::ResultAck>> PrepareAsyncReportResult(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::ResultAck>>(PrepareAsyncReportResultRaw(context, request, cq));
    }
    ::grpc::Status SubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::parser::SubmitTaskResponse* response) override;
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::SubmitTaskResponse>> AsyncSubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::SubmitTaskResponse>>(AsyncSubmitTaskRaw(context, request, cq));
    }
    std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::SubmitTaskResponse>> PrepareAsyncSubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::grpc::CompletionQueue* cq) {
      return std::unique_ptr< ::grpc::ClientAsyncResponseReader< ::parser::SubmitTaskResponse>>(PrepareAsyncSubmitTaskRaw(context, request, cq));
    }
    class async final :
      public StubInterface::async_interface {
     public:
      void GetTask(::grpc::ClientContext* context, const ::parser::TaskRequest* request, ::parser::TaskResponse* response, std::function<void(::grpc::Status)>) override;
      void GetTask(::grpc::ClientContext* context, const ::parser::TaskRequest* request, ::parser::TaskResponse* response, ::grpc::ClientUnaryReactor* reactor) override;
      void ReportResult(::grpc::ClientContext* context, const ::parser::TaskResult* request, ::parser::ResultAck* response, std::function<void(::grpc::Status)>) override;
      void ReportResult(::grpc::ClientContext* context, const ::parser::TaskResult* request, ::parser::ResultAck* response, ::grpc::ClientUnaryReactor* reactor) override;
      void SubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest* request, ::parser::SubmitTaskResponse* response, std::function<void(::grpc::Status)>) override;
      void SubmitTask(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest* request, ::parser::SubmitTaskResponse* response, ::grpc::ClientUnaryReactor* reactor) override;
     private:
      friend class Stub;
      explicit async(Stub* stub): stub_(stub) { }
      Stub* stub() { return stub_; }
      Stub* stub_;
    };
    class async* async() override { return &async_stub_; }

   private:
    std::shared_ptr< ::grpc::ChannelInterface> channel_;
    class async async_stub_{this};
    ::grpc::ClientAsyncResponseReader< ::parser::TaskResponse>* AsyncGetTaskRaw(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::grpc::CompletionQueue* cq) override;
    ::grpc::ClientAsyncResponseReader< ::parser::TaskResponse>* PrepareAsyncGetTaskRaw(::grpc::ClientContext* context, const ::parser::TaskRequest& request, ::grpc::CompletionQueue* cq) override;
    ::grpc::ClientAsyncResponseReader< ::parser::ResultAck>* AsyncReportResultRaw(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::grpc::CompletionQueue* cq) override;
    ::grpc::ClientAsyncResponseReader< ::parser::ResultAck>* PrepareAsyncReportResultRaw(::grpc::ClientContext* context, const ::parser::TaskResult& request, ::grpc::CompletionQueue* cq) override;
    ::grpc::ClientAsyncResponseReader< ::parser::SubmitTaskResponse>* AsyncSubmitTaskRaw(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::grpc::CompletionQueue* cq) override;
    ::grpc::ClientAsyncResponseReader< ::parser::SubmitTaskResponse>* PrepareAsyncSubmitTaskRaw(::grpc::ClientContext* context, const ::parser::SubmitTaskRequest& request, ::grpc::CompletionQueue* cq) override;
    const ::grpc::internal::RpcMethod rpcmethod_GetTask_;
    const ::grpc::internal::RpcMethod rpcmethod_ReportResult_;
    const ::grpc::internal::RpcMethod rpcmethod_SubmitTask_;
  };
  static std::unique_ptr<Stub> NewStub(const std::shared_ptr< ::grpc::ChannelInterface>& channel, const ::grpc::StubOptions& options = ::grpc::StubOptions());

  class Service : public ::grpc::Service {
   public:
    Service();
    virtual ~Service();
    virtual ::grpc::Status GetTask(::grpc::ServerContext* context, const ::parser::TaskRequest* request, ::parser::TaskResponse* response);
    virtual ::grpc::Status ReportResult(::grpc::ServerContext* context, const ::parser::TaskResult* request, ::parser::ResultAck* response);
    virtual ::grpc::Status SubmitTask(::grpc::ServerContext* context, const ::parser::SubmitTaskRequest* request, ::parser::SubmitTaskResponse* response);
    // Новый метод для отправки URL-адреса
  };
  template <class BaseClass>
  class WithAsyncMethod_GetTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithAsyncMethod_GetTask() {
      ::grpc::Service::MarkMethodAsync(0);
    }
    ~WithAsyncMethod_GetTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status GetTask(::grpc::ServerContext* /*context*/, const ::parser::TaskRequest* /*request*/, ::parser::TaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestGetTask(::grpc::ServerContext* context, ::parser::TaskRequest* request, ::grpc::ServerAsyncResponseWriter< ::parser::TaskResponse>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(0, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  template <class BaseClass>
  class WithAsyncMethod_ReportResult : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithAsyncMethod_ReportResult() {
      ::grpc::Service::MarkMethodAsync(1);
    }
    ~WithAsyncMethod_ReportResult() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status ReportResult(::grpc::ServerContext* /*context*/, const ::parser::TaskResult* /*request*/, ::parser::ResultAck* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestReportResult(::grpc::ServerContext* context, ::parser::TaskResult* request, ::grpc::ServerAsyncResponseWriter< ::parser::ResultAck>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(1, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  template <class BaseClass>
  class WithAsyncMethod_SubmitTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithAsyncMethod_SubmitTask() {
      ::grpc::Service::MarkMethodAsync(2);
    }
    ~WithAsyncMethod_SubmitTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status SubmitTask(::grpc::ServerContext* /*context*/, const ::parser::SubmitTaskRequest* /*request*/, ::parser::SubmitTaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestSubmitTask(::grpc::ServerContext* context, ::parser::SubmitTaskRequest* request, ::grpc::ServerAsyncResponseWriter< ::parser::SubmitTaskResponse>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(2, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  typedef WithAsyncMethod_GetTask<WithAsyncMethod_ReportResult<WithAsyncMethod_SubmitTask<Service > > > AsyncService;
  template <class BaseClass>
  class WithCallbackMethod_GetTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithCallbackMethod_GetTask() {
      ::grpc::Service::MarkMethodCallback(0,
          new ::grpc::internal::CallbackUnaryHandler< ::parser::TaskRequest, ::parser::TaskResponse>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::parser::TaskRequest* request, ::parser::TaskResponse* response) { return this->GetTask(context, request, response); }));}
    void SetMessageAllocatorFor_GetTask(
        ::grpc::MessageAllocator< ::parser::TaskRequest, ::parser::TaskResponse>* allocator) {
      ::grpc::internal::MethodHandler* const handler = ::grpc::Service::GetHandler(0);
      static_cast<::grpc::internal::CallbackUnaryHandler< ::parser::TaskRequest, ::parser::TaskResponse>*>(handler)
              ->SetMessageAllocator(allocator);
    }
    ~WithCallbackMethod_GetTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status GetTask(::grpc::ServerContext* /*context*/, const ::parser::TaskRequest* /*request*/, ::parser::TaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* GetTask(
      ::grpc::CallbackServerContext* /*context*/, const ::parser::TaskRequest* /*request*/, ::parser::TaskResponse* /*response*/)  { return nullptr; }
  };
  template <class BaseClass>
  class WithCallbackMethod_ReportResult : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithCallbackMethod_ReportResult() {
      ::grpc::Service::MarkMethodCallback(1,
          new ::grpc::internal::CallbackUnaryHandler< ::parser::TaskResult, ::parser::ResultAck>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::parser::TaskResult* request, ::parser::ResultAck* response) { return this->ReportResult(context, request, response); }));}
    void SetMessageAllocatorFor_ReportResult(
        ::grpc::MessageAllocator< ::parser::TaskResult, ::parser::ResultAck>* allocator) {
      ::grpc::internal::MethodHandler* const handler = ::grpc::Service::GetHandler(1);
      static_cast<::grpc::internal::CallbackUnaryHandler< ::parser::TaskResult, ::parser::ResultAck>*>(handler)
              ->SetMessageAllocator(allocator);
    }
    ~WithCallbackMethod_ReportResult() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status ReportResult(::grpc::ServerContext* /*context*/, const ::parser::TaskResult* /*request*/, ::parser::ResultAck* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* ReportResult(
      ::grpc::CallbackServerContext* /*context*/, const ::parser::TaskResult* /*request*/, ::parser::ResultAck* /*response*/)  { return nullptr; }
  };
  template <class BaseClass>
  class WithCallbackMethod_SubmitTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithCallbackMethod_SubmitTask() {
      ::grpc::Service::MarkMethodCallback(2,
          new ::grpc::internal::CallbackUnaryHandler< ::parser::SubmitTaskRequest, ::parser::SubmitTaskResponse>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::parser::SubmitTaskRequest* request, ::parser::SubmitTaskResponse* response) { return this->SubmitTask(context, request, response); }));}
    void SetMessageAllocatorFor_SubmitTask(
        ::grpc::MessageAllocator< ::parser::SubmitTaskRequest, ::parser::SubmitTaskResponse>* allocator) {
      ::grpc::internal::MethodHandler* const handler = ::grpc::Service::GetHandler(2);
      static_cast<::grpc::internal::CallbackUnaryHandler< ::parser::SubmitTaskRequest, ::parser::SubmitTaskResponse>*>(handler)
              ->SetMessageAllocator(allocator);
    }
    ~WithCallbackMethod_SubmitTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status SubmitTask(::grpc::ServerContext* /*context*/, const ::parser::SubmitTaskRequest* /*request*/, ::parser::SubmitTaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* SubmitTask(
      ::grpc::CallbackServerContext* /*context*/, const ::parser::SubmitTaskRequest* /*request*/, ::parser::SubmitTaskResponse* /*response*/)  { return nullptr; }
  };
  typedef WithCallbackMethod_GetTask<WithCallbackMethod_ReportResult<WithCallbackMethod_SubmitTask<Service > > > CallbackService;
  typedef CallbackService ExperimentalCallbackService;
  template <class BaseClass>
  class WithGenericMethod_GetTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithGenericMethod_GetTask() {
      ::grpc::Service::MarkMethodGeneric(0);
    }
    ~WithGenericMethod_GetTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status GetTask(::grpc::ServerContext* /*context*/, const ::parser::TaskRequest* /*request*/, ::parser::TaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
  };
  template <class BaseClass>
  class WithGenericMethod_ReportResult : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithGenericMethod_ReportResult() {
      ::grpc::Service::MarkMethodGeneric(1);
    }
    ~WithGenericMethod_ReportResult() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status ReportResult(::grpc::ServerContext* /*context*/, const ::parser::TaskResult* /*request*/, ::parser::ResultAck* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
  };
  template <class BaseClass>
  class WithGenericMethod_SubmitTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithGenericMethod_SubmitTask() {
      ::grpc::Service::MarkMethodGeneric(2);
    }
    ~WithGenericMethod_SubmitTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status SubmitTask(::grpc::ServerContext* /*context*/, const ::parser::SubmitTaskRequest* /*request*/, ::parser::SubmitTaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
  };
  template <class BaseClass>
  class WithRawMethod_GetTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawMethod_GetTask() {
      ::grpc::Service::MarkMethodRaw(0);
    }
    ~WithRawMethod_GetTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status GetTask(::grpc::ServerContext* /*context*/, const ::parser::TaskRequest* /*request*/, ::parser::TaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestGetTask(::grpc::ServerContext* context, ::grpc::ByteBuffer* request, ::grpc::ServerAsyncResponseWriter< ::grpc::ByteBuffer>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(0, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  template <class BaseClass>
  class WithRawMethod_ReportResult : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawMethod_ReportResult() {
      ::grpc::Service::MarkMethodRaw(1);
    }
    ~WithRawMethod_ReportResult() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status ReportResult(::grpc::ServerContext* /*context*/, const ::parser::TaskResult* /*request*/, ::parser::ResultAck* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestReportResult(::grpc::ServerContext* context, ::grpc::ByteBuffer* request, ::grpc::ServerAsyncResponseWriter< ::grpc::ByteBuffer>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(1, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  template <class BaseClass>
  class WithRawMethod_SubmitTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawMethod_SubmitTask() {
      ::grpc::Service::MarkMethodRaw(2);
    }
    ~WithRawMethod_SubmitTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status SubmitTask(::grpc::ServerContext* /*context*/, const ::parser::SubmitTaskRequest* /*request*/, ::parser::SubmitTaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    void RequestSubmitTask(::grpc::ServerContext* context, ::grpc::ByteBuffer* request, ::grpc::ServerAsyncResponseWriter< ::grpc::ByteBuffer>* response, ::grpc::CompletionQueue* new_call_cq, ::grpc::ServerCompletionQueue* notification_cq, void *tag) {
      ::grpc::Service::RequestAsyncUnary(2, context, request, response, new_call_cq, notification_cq, tag);
    }
  };
  template <class BaseClass>
  class WithRawCallbackMethod_GetTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawCallbackMethod_GetTask() {
      ::grpc::Service::MarkMethodRawCallback(0,
          new ::grpc::internal::CallbackUnaryHandler< ::grpc::ByteBuffer, ::grpc::ByteBuffer>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::grpc::ByteBuffer* request, ::grpc::ByteBuffer* response) { return this->GetTask(context, request, response); }));
    }
    ~WithRawCallbackMethod_GetTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status GetTask(::grpc::ServerContext* /*context*/, const ::parser::TaskRequest* /*request*/, ::parser::TaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* GetTask(
      ::grpc::CallbackServerContext* /*context*/, const ::grpc::ByteBuffer* /*request*/, ::grpc::ByteBuffer* /*response*/)  { return nullptr; }
  };
  template <class BaseClass>
  class WithRawCallbackMethod_ReportResult : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawCallbackMethod_ReportResult() {
      ::grpc::Service::MarkMethodRawCallback(1,
          new ::grpc::internal::CallbackUnaryHandler< ::grpc::ByteBuffer, ::grpc::ByteBuffer>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::grpc::ByteBuffer* request, ::grpc::ByteBuffer* response) { return this->ReportResult(context, request, response); }));
    }
    ~WithRawCallbackMethod_ReportResult() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status ReportResult(::grpc::ServerContext* /*context*/, const ::parser::TaskResult* /*request*/, ::parser::ResultAck* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* ReportResult(
      ::grpc::CallbackServerContext* /*context*/, const ::grpc::ByteBuffer* /*request*/, ::grpc::ByteBuffer* /*response*/)  { return nullptr; }
  };
  template <class BaseClass>
  class WithRawCallbackMethod_SubmitTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithRawCallbackMethod_SubmitTask() {
      ::grpc::Service::MarkMethodRawCallback(2,
          new ::grpc::internal::CallbackUnaryHandler< ::grpc::ByteBuffer, ::grpc::ByteBuffer>(
            [this](
                   ::grpc::CallbackServerContext* context, const ::grpc::ByteBuffer* request, ::grpc::ByteBuffer* response) { return this->SubmitTask(context, request, response); }));
    }
    ~WithRawCallbackMethod_SubmitTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable synchronous version of this method
    ::grpc::Status SubmitTask(::grpc::ServerContext* /*context*/, const ::parser::SubmitTaskRequest* /*request*/, ::parser::SubmitTaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    virtual ::grpc::ServerUnaryReactor* SubmitTask(
      ::grpc::CallbackServerContext* /*context*/, const ::grpc::ByteBuffer* /*request*/, ::grpc::ByteBuffer* /*response*/)  { return nullptr; }
  };
  template <class BaseClass>
  class WithStreamedUnaryMethod_GetTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithStreamedUnaryMethod_GetTask() {
      ::grpc::Service::MarkMethodStreamed(0,
        new ::grpc::internal::StreamedUnaryHandler<
          ::parser::TaskRequest, ::parser::TaskResponse>(
            [this](::grpc::ServerContext* context,
                   ::grpc::ServerUnaryStreamer<
                     ::parser::TaskRequest, ::parser::TaskResponse>* streamer) {
                       return this->StreamedGetTask(context,
                         streamer);
                  }));
    }
    ~WithStreamedUnaryMethod_GetTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable regular version of this method
    ::grpc::Status GetTask(::grpc::ServerContext* /*context*/, const ::parser::TaskRequest* /*request*/, ::parser::TaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    // replace default version of method with streamed unary
    virtual ::grpc::Status StreamedGetTask(::grpc::ServerContext* context, ::grpc::ServerUnaryStreamer< ::parser::TaskRequest,::parser::TaskResponse>* server_unary_streamer) = 0;
  };
  template <class BaseClass>
  class WithStreamedUnaryMethod_ReportResult : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithStreamedUnaryMethod_ReportResult() {
      ::grpc::Service::MarkMethodStreamed(1,
        new ::grpc::internal::StreamedUnaryHandler<
          ::parser::TaskResult, ::parser::ResultAck>(
            [this](::grpc::ServerContext* context,
                   ::grpc::ServerUnaryStreamer<
                     ::parser::TaskResult, ::parser::ResultAck>* streamer) {
                       return this->StreamedReportResult(context,
                         streamer);
                  }));
    }
    ~WithStreamedUnaryMethod_ReportResult() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable regular version of this method
    ::grpc::Status ReportResult(::grpc::ServerContext* /*context*/, const ::parser::TaskResult* /*request*/, ::parser::ResultAck* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    // replace default version of method with streamed unary
    virtual ::grpc::Status StreamedReportResult(::grpc::ServerContext* context, ::grpc::ServerUnaryStreamer< ::parser::TaskResult,::parser::ResultAck>* server_unary_streamer) = 0;
  };
  template <class BaseClass>
  class WithStreamedUnaryMethod_SubmitTask : public BaseClass {
   private:
    void BaseClassMustBeDerivedFromService(const Service* /*service*/) {}
   public:
    WithStreamedUnaryMethod_SubmitTask() {
      ::grpc::Service::MarkMethodStreamed(2,
        new ::grpc::internal::StreamedUnaryHandler<
          ::parser::SubmitTaskRequest, ::parser::SubmitTaskResponse>(
            [this](::grpc::ServerContext* context,
                   ::grpc::ServerUnaryStreamer<
                     ::parser::SubmitTaskRequest, ::parser::SubmitTaskResponse>* streamer) {
                       return this->StreamedSubmitTask(context,
                         streamer);
                  }));
    }
    ~WithStreamedUnaryMethod_SubmitTask() override {
      BaseClassMustBeDerivedFromService(this);
    }
    // disable regular version of this method
    ::grpc::Status SubmitTask(::grpc::ServerContext* /*context*/, const ::parser::SubmitTaskRequest* /*request*/, ::parser::SubmitTaskResponse* /*response*/) override {
      abort();
      return ::grpc::Status(::grpc::StatusCode::UNIMPLEMENTED, "");
    }
    // replace default version of method with streamed unary
    virtual ::grpc::Status StreamedSubmitTask(::grpc::ServerContext* context, ::grpc::ServerUnaryStreamer< ::parser::SubmitTaskRequest,::parser::SubmitTaskResponse>* server_unary_streamer) = 0;
  };
  typedef WithStreamedUnaryMethod_GetTask<WithStreamedUnaryMethod_ReportResult<WithStreamedUnaryMethod_SubmitTask<Service > > > StreamedUnaryService;
  typedef Service SplitStreamedService;
  typedef WithStreamedUnaryMethod_GetTask<WithStreamedUnaryMethod_ReportResult<WithStreamedUnaryMethod_SubmitTask<Service > > > StreamedService;
};

}  // namespace parser


#endif  // GRPC_task_2eproto__INCLUDED
