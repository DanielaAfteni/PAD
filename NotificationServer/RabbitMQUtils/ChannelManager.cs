using RabbitMQ.Client;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RabbitMQUtils
{
    public class ChannelManager
    {
        private readonly List<ChannelRmq> _channels;
        private readonly int _channelLimit;
        private readonly long _limitProcessing;
        private readonly ConnectionFactory _factory;

        public ChannelManager(ConnectionFactory factory, int channelLimit,int limitProcessing)
        {
            _factory = factory;
            _channelLimit = channelLimit;
            _limitProcessing = limitProcessing;
            _channels = new List<ChannelRmq>();
        }

        public void Publish(string message, string entityName, ChannelType chanelType)
        {
            if (!_channels.All(x => x._EntityName == entityName))
            {
                _channels.Add(new ChannelRmq(_factory, entityName, chanelType));
            }

            var sender =
             _channels.FirstOrDefault(x => x._EntityName == entityName && x.CountProcessing < _limitProcessing);
            var newSender = false;
            if (sender == null && _channels.Count < _channelLimit)
            {
                sender = new ChannelRmq(_factory, entityName, chanelType);
                newSender = true;
                Console.WriteLine($"Create New Publisher {_channels.Count}");
            }
            else if (sender == null)
            {
                while (_channels.FirstOrDefault(x => x._EntityName == entityName && x.CountProcessing < _limitProcessing) == null)
                {
                    Thread.Sleep(1000);
                }
                sender = _channels.FirstOrDefault(x => x._EntityName == entityName && x.CountProcessing < _limitProcessing);
            }

            sender!.Publish(message);
            if (newSender)
            {
                _channels.Add(sender);
            }
        }
    }
}
