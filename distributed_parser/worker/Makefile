CXX = g++
CXXFLAGS = -std=c++17 -I../include -I/usr/local/include
LDFLAGS = -L/usr/local/lib -lgrpc++ -lprotobuf -lxml2 -lcurl -pthread

SRCS = worker.cpp html_parser.cpp page_fetcher.cpp main.cpp ../generated/task.pb.cc ../generated/task.grpc.pb.cc
OBJS = $(SRCS:.cpp=.o)

TARGET = worker

all: $(TARGET)

$(TARGET): $(OBJS)
    $(CXX) -o $@ $(OBJS) $(LDFLAGS)

clean:
    rm -f $(OBJS) $(TARGET)
