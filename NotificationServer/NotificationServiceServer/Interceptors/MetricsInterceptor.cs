using Grpc.Core.Interceptors;
using Grpc.Core;
using Prometheus;
using System.Diagnostics;

namespace NotificationServiceServer.Interceptors
{
    public class MetricsInterceptor : Interceptor
    {
        private readonly Counter grpcRequestsReceived = Metrics.CreateCounter("grpc_requests_received_total", "Number of gRPC requests received");
        private readonly Counter grpcMethodDurations = Metrics.CreateCounter("grpc_method_duration_seconds_total", "Total duration of gRPC method calls in seconds");

        public override async Task<TResponse> UnaryServerHandler<TRequest, TResponse>(
            TRequest request,
            ServerCallContext context,
            UnaryServerMethod<TRequest, TResponse> continuation)
        {
            grpcRequestsReceived.Inc();

            var stopwatch = Stopwatch.StartNew();
            try
            {
                // Perform actions before the gRPC method call (if needed)

                // Continue with the gRPC method call
                var response = await continuation(request, context);

                // Perform actions after the gRPC method call (if needed)

                return response;
            }
            finally
            {
                stopwatch.Stop();
                grpcMethodDurations.Inc(stopwatch.Elapsed.TotalSeconds);
            }
        }
    }

}
