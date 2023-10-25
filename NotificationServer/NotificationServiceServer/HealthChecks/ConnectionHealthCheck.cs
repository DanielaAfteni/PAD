using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Options;
using RabbitMQ.Client;
using RabbitMQUtils;

namespace NotificationServiceServer.HealthChecks
{
    public class ConnectionHealthCheck : IHealthCheck
    {
        private readonly ILogger _logger;
        private readonly IOptions<RabbitMqOptions> _options;

        public ConnectionHealthCheck(IOptions<RabbitMqOptions> options, ILogger<ConnectionHealthCheck> logger)
        {
            _options = options;
            _logger = logger;
        }
        public Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
        {
            try
            {
                var factory = new ConnectionFactory { Uri = new Uri(_options.Value.ConnectionString) };
                using var connection = factory.CreateConnection();
                using var channel = connection.CreateModel();
                channel.QueueDeclarePassive("Notifications");
                if (connection.IsOpen)
                {
                    return Task.FromResult(HealthCheckResult.Healthy("Rabbit connection is working"));
                }
                throw new Exception("Rabbit Connection Health Check Failed");
            }
            catch (Exception)
            {
                return Task.FromResult(HealthCheckResult.Unhealthy("Rabbit Connection Health Check Failed"));
            }
        }
    }
}
