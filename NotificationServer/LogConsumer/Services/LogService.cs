using LogConsumer.Configurations;
using LogConsumer.Models;
using Microsoft.Extensions.Options;
using MongoDB.Driver;

namespace LogConsumer.Services
{
    public class LogService
    {
        private readonly ILogger _logger;
        private readonly IMongoCollection<ServiceLog> _serviceLogCollection;
        public LogService(IOptions<DatabaseSettings> databaseSettings)
        {
            var mongoClient = new MongoClient(databaseSettings.Value.ConnectionString);
            var mongoDb = mongoClient.GetDatabase(databaseSettings.Value.DatabaseName);
            _serviceLogCollection = mongoDb.GetCollection<ServiceLog>(databaseSettings.Value.CollectionName);
        }
        public async Task<ServiceLog?> GetLog(string id) => await _serviceLogCollection.Find(x => x.Id == id).FirstOrDefaultAsync();
        public async Task AddLog(ServiceLog serviceLog) => await _serviceLogCollection.InsertOneAsync(serviceLog);
    }
}
