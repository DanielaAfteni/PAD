using MongoDB.Driver;

namespace MongoLogs.DataContext
{
    public class MongoDbContext
    {
        private readonly IMongoDatabase _database;
        private readonly string _connectionString;
        private readonly string _databaseName;
        private readonly string _collectionName;
        public MongoDbContext(string connectionString, string databaseName, string collectionName)
        {
            _connectionString = connectionString;
            _databaseName = databaseName;
            _collectionName = collectionName;
        }

        public IMongoCollection<T> GetCollection<T>(string collectionName)
        {
            return _database.GetCollection<T>(collectionName);
        }
        public List<ServiceLog> GetLogs()
        {
            var client = new MongoClient(_connectionString);
            var mongoDb = client.GetDatabase(_databaseName);
            var collection = mongoDb.GetCollection<ServiceLog>(_collectionName);
            return collection.Find(Builders<ServiceLog>.Filter.Empty).ToList();
        }

    }
}
