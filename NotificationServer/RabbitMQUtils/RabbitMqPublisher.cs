using Microsoft.Extensions.Options;
using RabbitMQ.Client;
using System.Collections.Concurrent;
using System.Text;

namespace RabbitMQUtils
{
    public class RabbitMqPublisher
    {
        private readonly ConnectionFactory factory;
        private readonly int _channelLimit = 1;
        private readonly int _processingLimit = 100;
        private readonly ChannelManager _channelManager;

        public RabbitMqPublisher(IOptions<RabbitMqOptions> options)
        {
            //factory = new ConnectionFactory
            //{
            //    Uri = new Uri(options.Value.ConnectionString!)
            //};
            factory = new ConnectionFactory
            {
                HostName = "localhost"
            };
            _channelManager = new ChannelManager(factory,_channelLimit,_processingLimit);
        }
        public void SendExchangeAsyncAck(string exchangeName, string message)
        {
            _channelManager.Publish(message, exchangeName, ChannelType.Exchange);
        }
        public void SendQueueAsyncAck(string queueName, string message)
        {
            _channelManager.Publish(message, queueName, ChannelType.Queue);
        }

    }
}