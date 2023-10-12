using RabbitMQUtils;
using Grpc.Core;
using System.Text.Json;

namespace NotificationServiceServer.Services
{
    public class NotificationService : Notification.NotificationBase
    {
        private readonly ILogger<NotificationService> _logger;
        private readonly RabbitMqPublisher _rabbitMqPublisher;
        public NotificationService (RabbitMqPublisher rabbitMqPublisher, ILogger<NotificationService> logger)
        {
            _logger = logger;
            _rabbitMqPublisher = rabbitMqPublisher;

        }
        public override Task<LogReply> SaveLogToRabbit(LogRequest request, ServerCallContext context)
        {
            try
            {
                var stringRequest = JsonSerializer.Serialize(request);
                var test = DateTimeOffset.FromUnixTimeSeconds(request.Time.Seconds).DateTime;
                _rabbitMqPublisher.SendQueueAsyncAck("Notifications", stringRequest);
                return Task.FromResult(new LogReply { IsSuccess = true });
            }
            catch(Exception ex) { 
                _logger.LogError(ex.Message);
                return Task.FromResult(new LogReply { IsSuccess=false });
            }
            
        }
    }
}
