
using ChatGPT.DataContext;
using DataWarehouse.DataContext;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.DependencyInjection;
using Users.DataContext;

namespace DataWarehouse.Services
{
    public class ETLService : BackgroundService
    {
        private readonly IServiceScopeFactory _serviceScopeFactory;

        public ETLService(IServiceScopeFactory serviceScopeFactory)
        {
            _serviceScopeFactory = serviceScopeFactory;
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
            }
            catch (Exception ex)
            {
            }
            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
            await ExecuteAsync(stoppingToken);
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
                users = chatGptDbContext.ChatUsers.Where(x => !existingUsersNames.Contains(x.Name)).ToList();
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
