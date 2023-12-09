using MongoDB.Bson.Serialization.Attributes;
using MongoDB.Bson;

namespace MongoLogs.DataContext
{
    public class ServiceLog
    {
        [BsonId]
        [BsonRepresentation(BsonType.ObjectId)]
        public string Id { get; set; } = string.Empty;
        public string ServiceName { get; set; } = string.Empty;
        public string ServiceMessage { get; set; } = string.Empty;

        [BsonRepresentation(BsonType.String)]
        public DateTimeOffset CreatedAt { get; set; }
    }
}
