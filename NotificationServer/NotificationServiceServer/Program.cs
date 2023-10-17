using Microsoft.Extensions.Diagnostics.HealthChecks;
using NotificationServiceServer.Services;
using Prometheus;
using RabbitMQUtils;

var builder = WebApplication.CreateBuilder(args);

// Additional configuration is required to successfully run gRPC on macOS.
// For instructions on how to configure Kestrel and gRPC clients on macOS, visit https://go.microsoft.com/fwlink/?linkid=2099682

// Add services to the container.
var services = builder.Services;
var configuration = builder.Configuration;
services.AddGrpc();
builder.Services.AddGrpcHealthChecks()
                .AddCheck("Sample", () => HealthCheckResult.Healthy());
services.Configure<RabbitMqOptions>(x => x.ConnectionString = configuration.GetConnectionString("RabbitMQ")!);
services.AddSingleton<RabbitMqPublisher>();
services.AddScoped<NotificationService>();
services.AddGrpcReflection();
//services.AddGrpcHealthChecks(o =>
//{
//    o.Services.Map("", r => true);
//});

services.Configure<HealthCheckPublisherOptions>(options =>
{
    options.Delay = TimeSpan.Zero;
    options.Period = TimeSpan.FromSeconds(10);
});
var app = builder.Build();

// Configure the HTTP request pipeline.
app.MapGrpcService<NotificationService>();
app.MapGrpcHealthChecksService();
app.MapGrpcReflectionService();
app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");

app.Run();
