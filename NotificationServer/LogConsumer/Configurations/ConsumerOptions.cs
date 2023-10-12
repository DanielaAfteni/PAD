namespace LogConsumer.Configurations
{
    public class ConsumerOptions
    {
        public uint PrefetchSize { get; set; }
        public ushort PrefetchCount { get; set; }
        public string ChannelTarget { get; set; }
    }
}
