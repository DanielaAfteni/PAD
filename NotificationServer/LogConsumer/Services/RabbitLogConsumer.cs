using LogConsumer.Configurations;
using Microsoft.Extensions.Options;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using RabbitMQUtils;
using System.Text;
using Grpc.Core;
using System.Text.Json;
using NotificationServiceServer;
using LogConsumer.Models;

namespace LogConsumer.Services
{
    public class RabbitLogConsumer : BackgroundService
    {
        private readonly RabbitMQ.Client.IConnection _connection;
        private readonly IModel _channel;
        private readonly ILogger _logger;
        private readonly ChannelType _channelType;
        private readonly ConsumerOptions _consumerOptions;
        private readonly RabbitMqOptions _rabbitMqOptions;
        private readonly LogService _logService;

        public RabbitLogConsumer(IOptions<RabbitMqOptions> options, IOptions<ConsumerOptions> consumerOptions, ILogger<RabbitLogConsumer> logger
            ,LogService logService)
        {
            _logger = logger;
            _consumerOptions = consumerOptions.Value;
            var factory = new ConnectionFactory { Uri = new Uri(options.Value.ConnectionString)};
            _connection = factory.CreateConnection();
            _channel = _connection.CreateModel();
            _channel.BasicQos(_consumerOptions.PrefetchSize, _consumerOptions.PrefetchCount, false);
            _logService = logService;
            _rabbitMqOptions = options.Value;
            _channelType = ChannelType.Queue;
            DeclareEntity();
            
        }
        protected override Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _logger.LogInformation("Started Background Task!");
            stoppingToken.ThrowIfCancellationRequested();
            var consumer = new EventingBasicConsumer(_channel);
            consumer.Received += async (ch, ea) =>
            {
                try
                {
                    _logger.LogInformation("Received Message");
                    var content = Encoding.UTF8.GetString(ea.Body.ToArray());
                    var logRequest = JsonSerializer.Deserialize<LogRequest>(content) ?? throw new Exception("LogRequest was null");
                    var serviceLog = new ServiceLog
                    {
                        ServiceMessage = logRequest.ServiceMessage,
                        ServiceName = logRequest.ServiceName,
                        CreatedAt = logRequest.Time.ToDateTimeOffset()
                    };
                    await _logService.AddLog(serviceLog);
                    _channel.BasicAck(ea.DeliveryTag, multiple: false);
                }
                catch (Exception ex)
                {
                    _logger.LogError("Couldn't save log\n {error}", ex);
                    _channel.BasicNack(ea.DeliveryTag, false,false);
                }
            };
            _channel.BasicConsume(_consumerOptions.ChannelTarget, false, consumer);
            return Task.CompletedTask;
        }
        private void DeclareEntity()
        {
            if( _channelType == ChannelType.Queue )
            {
                DeclareQueue();
            }
            else if(_channelType == ChannelType.Exchange)
            {
                DeclareExchange();
            }
        }
        private void DeclareQueue()
        {
            _channel.QueueDeclarePassive(_consumerOptions.ChannelTarget);
        }
        private void DeclareExchange()
        {
            _channel.ExchangeDeclarePassive(_consumerOptions.ChannelTarget);
        }
    }
}
