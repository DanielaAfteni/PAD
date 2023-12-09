using Docker.DotNet;
using Docker.DotNet.Models;
using DotnetGateway.Middleware;
using DotnetGateway.Services;
using FastEndpoints;

var builder = WebApplication.CreateBuilder(args);
var services = builder.Services;
services.AddFastEndpoints();
services.AddHttpClient();
services.Configure<ReplicaConfiguration>(builder.Configuration.GetSection("ChatGptServiceReplicaOptions"));
services.AddSingleton<DockerService>();
services.AddSingleton<LoadBalancerService>();
var app = builder.Build();
app.UseFastEndpoints();
app.UseTimeoutMiddleware(TimeSpan.FromSeconds(30));
app.Run();

