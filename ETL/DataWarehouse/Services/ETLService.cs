
using ChatGPT.DataContext;
using DataWarehouse.Configuration;
using DataWarehouse.DataContext;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using MongoLogs.DataContext;
using Users.DataContext;
using ServiceLog = DataWarehouse.DataContext.ServiceLog;

namespace DataWarehouse.Services
{
    public class ETLService : BackgroundService
    {
        private readonly IServiceScopeFactory _serviceScopeFactory;
        private readonly MongoDbContext _mongoDbContext;
        private readonly IOptions<DatabaseSettings> _dbSettings;
        public ETLService(IServiceScopeFactory serviceScopeFactory, IOptions<DatabaseSettings> dbSettings)
        {
            _serviceScopeFactory = serviceScopeFactory;
            _dbSettings = dbSettings;
            _mongoDbContext = new(dbSettings.Value.ConnectionString, dbSettings.Value.DatabaseName, dbSettings.Value.CollectionName);
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            try
            {
                using var scope = _serviceScopeFactory.CreateScope();
                var warehouseContext = scope.ServiceProvider.GetRequiredService<WarehouseDataContext>();
                var chatGptDbContext = scope.ServiceProvider.GetRequiredService<ChatGptDbContext>();
                var userDbContext = scope.ServiceProvider.GetRequiredService<UserDbContext>();
                ProcessUsers(warehouseContext, userDbContext);
                ProcessChatGptUsers(warehouseContext, chatGptDbContext);
                ProcessCommands(warehouseContext, chatGptDbContext);
                ProcessLogs(warehouseContext);
            }
            catch (Exception ex)
            {
            }
            await Task.Delay(TimeSpan.FromSeconds(60), stoppingToken);
            await ExecuteAsync(stoppingToken);
        }
        public void ProcessLogs(WarehouseDataContext warehouseContext)
        {
            var logs = _mongoDbContext.GetLogs();
            if (warehouseContext.ServiceLogs.Any())
            {
                logs = logs.Where(x => !warehouseContext.ServiceLogs.Any(y => y.Id == x.Id)).ToList();
            }
            logs.ForEach(x => warehouseContext.ServiceLogs.Add(new ServiceLog
            {
                Id = x.Id,
                CreatedAt = x.CreatedAt,
                ServiceMessage = x.ServiceMessage,
                ServiceName = x.ServiceName
            }));
            warehouseContext.SaveChanges();
        }
        public void ProcessUsers(WarehouseDataContext warehouseContext, UserDbContext userDbContext)
        {
            var users = userDbContext.Users.ToList();
            var existingUsersNames = warehouseContext.Users.Select(x => x.Name).ToList();
            if (warehouseContext.Users.Any())
            {
                users = userDbContext.Users.Where(x => !existingUsersNames.Contains(x.Name)).ToList();
            }
            users.ForEach(x => warehouseContext.Users.Add(new DataContext.User { Name = x.Name, Email = x.Email }));
            warehouseContext.SaveChanges();
        }
        public void ProcessChatGptUsers(WarehouseDataContext warehouseContext, ChatGptDbContext chatGptDbContext)
        {
            var users = chatGptDbContext.ChatUsers.ToList();
            var existingUsersNames = warehouseContext.ChatUsers.Select(x => x.Name).ToList();
            if (warehouseContext.ChatUsers.Any())
            {
                users = [.. chatGptDbContext.ChatUsers.Where(x => !existingUsersNames.Contains(x.Name))];
            }
            users.ForEach(x => warehouseContext.ChatUsers.Add(new DataContext.ChatUser { Name = x.Name, NameAppearance = x.NameAppearance }));
            warehouseContext.SaveChanges();
        }
        public void ProcessCommands(WarehouseDataContext warehouseContext, ChatGptDbContext chatGptDbContext)
        {
            var commands = chatGptDbContext.QuestionCommandTables.ToList();
            var existingCommands = warehouseContext.QuestionCommands.Select(x => x.ExternalId).ToList();
            if (warehouseContext.QuestionCommands.Any())
            {
                commands = chatGptDbContext.QuestionCommandTables.Where(x => !existingCommands.Contains(x.Id)).ToList();
            }
            commands.ForEach(x => warehouseContext.QuestionCommands.Add(new DataContext.QuestionCommandTable
            {
                ExternalId = x.Id,
                NewQuestionCommand = x.NewQuestionCommand,
                NewQuestionPrompt = x.NewQuestionPrompt
            }));
            warehouseContext.SaveChanges();
        }
    }
}
