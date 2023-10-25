using LogConsumer.Configurations;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Microsoft.Extensions.Options;
using MongoDB.Driver;
using MongoDB.Driver.Core.Clusters;

namespace LogConsumer.HealthChecks
{
    public class MongoConnectionHealthCheck : IHealthCheck
    {
        private readonly ILogger<MongoConnectionHealthCheck> _logger;
        private readonly IOptions<DatabaseSettings> _databaseSettings;

        public MongoConnectionHealthCheck(ILogger<MongoConnectionHealthCheck> logger, IOptions<DatabaseSettings> databaseSettings)
        {
            _logger = logger;
            _databaseSettings = databaseSettings;
        }

        public Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken cancellationToken = default)
        {
            try
            {
                var mongoClient = new MongoClient(_databaseSettings.Value.ConnectionString);

                // Attempt to connect to the MongoDB server
                var isConnected = mongoClient.Cluster.Description.State == ClusterState.Connected;
                return isConnected ?  Task.FromResult(HealthCheckResult.Healthy("MongoDB connection is valid.")) 
                    : Task.FromResult(HealthCheckResult.Unhealthy("MongoDB connection failed."));
            }
            catch (Exception ex)
            {
                return Task.FromResult(HealthCheckResult.Unhealthy("MongoDB connection failed.", ex));
            }
        }
    }
}
