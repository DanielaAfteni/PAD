import grpc
import log_pb2
import log_pb2_grpc
import google.protobuf.timestamp_pb2


# Create a gRPC channel to connect to the server
channel = grpc.insecure_channel('localhost:5297')  # Replace with the actual server address

# Create a gRPC stub
stub = log_pb2_grpc.NotificationStub(channel)

# Create a LogRequest message
log_request = log_pb2.LogRequest(
    serviceName="nulla consequat irure",
    serviceMessage="amet aliqua mollit ex",
    time=google.protobuf.timestamp_pb2.Timestamp(nanos=0, seconds=80460018092)  # Use the full module path
)

# Send the LogRequest to the server
response = stub.SaveLogToRabbit(log_request)

# Handle the response
if response.isSuccess:
    print("Request was successful.")
else:
    print("Request failed.")
