create:
	python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. --pyi_out=. proto/log.proto

clean-generated-files:
	del -f log_pb2.py log_pb2.pyi log_pb2_grpc.py # windows
	#rm -f log_pb2.py log_pb2.pyi log_pb2_grpc.py #linux

.PHONY: all clean-generated-files

delete: clean-generated-files