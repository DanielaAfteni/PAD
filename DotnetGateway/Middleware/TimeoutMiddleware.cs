namespace DotnetGateway.Middleware
{
    public class TimeoutMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly TimeSpan _timeout;

        public TimeoutMiddleware(RequestDelegate next, TimeSpan timeout)
        {
            _next = next;
            _timeout = timeout;
        }

        public async Task Invoke(HttpContext context)
        {
            using var cts = new CancellationTokenSource();
            var task = _next(context);
            var timeoutTask = Task.Delay(_timeout, cts.Token);

            if (await Task.WhenAny(task, timeoutTask) == timeoutTask)
            {
                // Timeout occurred
                context.Response.StatusCode = 408; // Request Timeout
                await context.Response.WriteAsync("Request Timeout");
                cts.Cancel(); // Cancel the original request task
            }
            else
            {
                // Request completed within the timeout
                await task;
            }
        }
    }

    public static class TimeoutMiddlewareExtensions
    {
        public static IApplicationBuilder UseTimeoutMiddleware(this IApplicationBuilder builder, TimeSpan timeout)
        {
            return builder.UseMiddleware<TimeoutMiddleware>(timeout);
        }
    }
}
