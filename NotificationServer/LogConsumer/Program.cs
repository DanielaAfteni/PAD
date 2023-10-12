using LogConsumer.Configurations;
using LogConsumer.Services;
using Microsoft.Extensions.DependencyInjection;
using RabbitMQUtils;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
var services = builder.Services;
var configuration = builder.Configuration;
services.AddGrpc();
services.Configure<DatabaseSettings>(configuration.GetSection("MongoDatabase"));
services.Configure<RabbitMqOptions>(x => x.ConnectionString = configuration.GetConnectionString("RabbitMQ")!);
services.Configure<ConsumerOptions>(configuration.GetSection("ConsumerOptions"));
services.AddSingleton<LogService>();
services.AddHostedService<RabbitLogConsumer>();
var app = builder.Build();

app.Run();
