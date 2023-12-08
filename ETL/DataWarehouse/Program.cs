using ChatGPT.DataContext;
using DataWarehouse.Configuration;
using DataWarehouse.DataContext;
using DataWarehouse.Services;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Users.DataContext;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddDbContextPool<WarehouseDataContext>(x =>
{
    x.UseNpgsql(builder.Configuration.GetConnectionString("DataWarehouse"));
    //x.UseSnakeCaseNamingConvention();
});
builder.Services.AddDbContextPool<ChatGptDbContext>(x =>
{
    x.UseNpgsql(builder.Configuration.GetConnectionString("Chat-GPT"));
});
builder.Services.AddDbContextPool<UserDbContext>(x =>
{
    x.UseNpgsql(builder.Configuration.GetConnectionString("Users"));
});
builder.Services.Configure<DatabaseSettings>(builder.Configuration.GetSection("MongoDatabase"));
builder.Services.AddHostedService<ETLService>();

builder.Services.AddSwaggerGen();

var app = builder.Build();
try
{
    await using var scope = app.Services.CreateAsyncScope();
    using var db = scope.ServiceProvider.GetService<WarehouseDataContext>();
    await db.Database.MigrateAsync();
}
catch (Exception) { }

app.Run();
