using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RabbitMQUtils
{
    public class ChannelRmq
    {
        public string _EntityName { get; set; }
        private readonly IBasicProperties _props;
        private readonly IModel _channel;
        private ConcurrentDictionary<ulong, byte[]> _dictionary;
        private ChannelType _channelType;
        public ChannelRmq(ConnectionFactory factory, string entityName, ChannelType chanelType)
        {
            _channel = factory.CreateConnection()
                .CreateModel();
            _channel.ConfirmSelect();
            _channelType = chanelType;
            if (ChannelType.Queue == chanelType)
            {
                _channel.QueueDeclarePassive(entityName);
            }
            else if (ChannelType.Exchange == chanelType)
            {
                _channel.ExchangeDeclarePassive(entityName);
            }
            _EntityName = entityName;
            _channel.BasicAcks += ChannelOnBasicAcks;
            _channel.BasicNacks += ChannelOnBasicNacks;
            _dictionary = new ConcurrentDictionary<ulong, byte[]>();
            _props = _channel.CreateBasicProperties();
            _props.Persistent = true;
        }

        public long CountProcessing => _dictionary.Count;

        private void ChannelOnBasicNacks(object? sender, BasicNackEventArgs e)
        {
            var tempList = new List<byte[]>();
            var toUpdate = _dictionary.Where(x => x.Key <= e.DeliveryTag).ToList();
            if (e.Multiple)
            {
                toUpdate.ForEach(x =>
                {
                    tempList.Add(_dictionary[x.Key]);
                    if (!_dictionary.TryRemove(x.Key, out _))
                    {
                        Console.WriteLine("Error In removing entry on ChannelBasicNacks when Multiple");
                    }
                });
            }
            else
            {
                tempList.Add(_dictionary[e.DeliveryTag]);
                if (!_dictionary.TryRemove(e.DeliveryTag, out _))
                    Console.WriteLine("Error In removing entry on ChannelBasicNacks");
            }

            if (tempList.Count > 0)
            {
                tempList.ForEach(Publish);
            }
        }

        private void ChannelOnBasicAcks(object? sender, BasicAckEventArgs e)
        {
            var toUpdate = _dictionary.Where(x => x.Key <= e.DeliveryTag).ToList();
            if (e.Multiple)
            {
                toUpdate.ForEach(x =>
                {
                    if (_dictionary.TryGetValue(x.Key, out _) && !_dictionary.TryRemove(x.Key, out _))
                    {
                        Console.WriteLine("Error In removing entry on ChannelBasicAcks when Multiple");
                    }
                });
            }
            else if (_dictionary.TryGetValue(e.DeliveryTag, out _) && !_dictionary.TryRemove(e.DeliveryTag, out _))
            {
                Console.WriteLine("Error In removing entry on ChannelBasicAcks");
            }
        }

        public void Publish(string message)
        {
            var body = Encoding.UTF8.GetBytes(message);
            Publish(body);
        }

        private void Publish(byte[] message)
        {
            if (ChannelType.Queue == _channelType)
            {
                _channel.BasicPublish(
                    "",
                    routingKey: _EntityName,
                    basicProperties: _props,
                    body: message
                    );
            }
            else if (ChannelType.Exchange == _channelType)
            {
                _channel
                .BasicPublish(exchange: _EntityName,
                    routingKey: "",
                    basicProperties: _props,
                    body: message);
            }
            _dictionary.TryAdd(_channel.NextPublishSeqNo, message);

        }
    }
}
