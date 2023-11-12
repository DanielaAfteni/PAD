using Microsoft.Extensions.Diagnostics.HealthChecks;
using NotificationServiceServer.HealthChecks;
using NotificationServiceServer.Interceptors;
using NotificationServiceServer.Services;
using Prometheus;
using RabbitMQUtils;

try
{
    var builder = WebApplication.CreateBuilder(args);

    // Additional configuration is required to successfully run gRPC on macOS.
    // For instructions on how to configure Kestrel and gRPC clients on macOS, visit https://go.microsoft.com/fwlink/?linkid=2099682

    // Add services to the container.
    var services = builder.Services;
    var configuration = builder.Configuration;
    services.AddGrpc(options =>
    {
        options.Interceptors.Add<MetricsInterceptor>();
    });
    services.AddGrpcHealthChecks()
                    .AddCheck<ConnectionHealthCheck>("Rabbit connection ping")
                    .ForwardToPrometheus();
    services.Configure<RabbitMqOptions>(x => x.ConnectionString = configuration.GetConnectionString("RabbitMQ")!);
    services.AddSingleton<RabbitMqPublisher>();
    services.AddScoped<NotificationService>();
    services.AddGrpcReflection();

    services.Configure<HealthCheckPublisherOptions>(options =>
    {
        options.Delay = TimeSpan.Zero;
        options.Period = TimeSpan.FromSeconds(10);
    });
    var app = builder.Build();

    // Configure the HTTP request pipeline.
    app.UseRouting();
    app.UseGrpcMetrics();
    app.MapGrpcService<NotificationService>();
    app.MapGrpcHealthChecksService();
    app.MapGrpcReflectionService();
    app.MapMetrics();
    app.Run();
}
catch (Exception ex)
{
    Console.WriteLine(ex.ToString());
}
