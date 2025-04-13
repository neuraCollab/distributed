#!/bin/bash
PROTO_DIR=../proto_files
OUT_DIR=../generated

protoc -I=$PROTO_DIR --cpp_out=$OUT_DIR --grpc_out=$OUT_DIR --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` $PROTO_DIR/task.proto
