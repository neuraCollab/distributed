CXX = g++
CXXFLAGS = -std=c++17 -I. -I../generated -I/usr/local/include -I/usr/include -Wall
LDFLAGS = -L/usr/local/include/absl/base -labsl -L/usr/local/bin/grpc/lib -lgrpc++ -lprotobuf -lpthread -lcurl -lxml2 

# Файлы проекта
SRCS = coordinator.cpp main.cpp
GRPC_SRCS = ../generated/task.pb.cc ../generated/task.grpc.pb.cc
OBJS = $(SRCS:.cpp=.o) $(GRPC_SRCS:.cc=.o)

TARGET = coordinator

# Правило для сборки всего проекта
all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) -o $@ $(OBJS) $(LDFLAGS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

%.o: %.cc
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Правило для очистки скомпилированных файлов
clean:
	rm -f $(OBJS) $(TARGET)
