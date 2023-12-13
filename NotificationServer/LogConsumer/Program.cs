using LogConsumer.Configurations;
using LogConsumer.HealthChecks;
using LogConsumer.Services;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using Prometheus;
using RabbitMQUtils;

try
{
    var builder = WebApplication.CreateBuilder(args);

    // Add services to the container.

    // Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
    var services = builder.Services;
    var configuration = builder.Configuration;
    services.AddGrpc();
    services
        .AddGrpcHealthChecks()
        .AddCheck<ConnectionHealthCheck>("Rabbit connection ping")
        .AddCheck<MongoConnectionHealthCheck>("Mongo Connection ping")
        .ForwardToPrometheus();
    services.Configure<DatabaseSettings>(configuration.GetSection("MongoDatabase"));
    services.Configure<RabbitMqOptions>(x => x.ConnectionString = configuration.GetConnectionString("RabbitMQ")!);
    services.Configure<ConsumerOptions>(configuration.GetSection("ConsumerOptions"));
    services.Configure<HealthCheckPublisherOptions>(options =>
    {
        options.Delay = TimeSpan.FromSeconds(1);
        options.Period = TimeSpan.FromSeconds(15);
    });
    services.AddSingleton<LogService>();
    services.AddHostedService<RabbitLogConsumer>();
    services.AddGrpcReflection();
    var app = builder.Build();
    app.UseRouting();
    app.UseGrpcMetrics();
    app.MapGrpcHealthChecksService();
    app.MapGrpcReflectionService();
    app.MapMetrics();
    app.Run();
}

catch (Exception ex)
{
    Console.WriteLine(ex.ToString());
}

