using Polly.CircuitBreaker;
using Polly;

namespace DotnetGateway.Middleware
{
    public class CircuitBreakerMiddleware
    {
        private readonly RequestDelegate _next;
        private static AsyncCircuitBreakerPolicy _circuitBreakerPolicy;
        private static IAsyncPolicy _retryPolicy;
        public CircuitBreakerMiddleware(RequestDelegate next)
        {
            _next = next;

            _retryPolicy = Policy
                .Handle<Exception>() // Specify the type of exceptions to handle for retry
                .WaitAndRetryAsync(retryCount: 4, r => TimeSpan.FromSeconds(1.5)); // Retry 4 times before circuit breaker

            _circuitBreakerPolicy = Policy
                .Handle<Exception>()
                .AdvancedCircuitBreakerAsync(
                    failureThreshold: 0.5, // 50% actions must fail
                    samplingDuration: TimeSpan.FromSeconds(30), // Over any 10 second period
                    minimumThroughput: 7, // At least 7 actions in 10 seconds
                    durationOfBreak: TimeSpan.FromSeconds(30) // Break for 30 seconds
    );
        }

        public async Task InvokeAsync(HttpContext context)
        {
            try
            {
                // Wrap call in circuit breaker policy
                await _retryPolicy.WrapAsync(_circuitBreakerPolicy).ExecuteAsync(() => _next(context));
            }
            catch (BrokenCircuitException)
            {
                // Handle the case when the circuit is open
                context.Response.StatusCode = StatusCodes.Status503ServiceUnavailable;
                await context.Response.WriteAsync("Service unavailable.");
            }
        }
    }
}
