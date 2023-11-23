using Microsoft.EntityFrameworkCore;

namespace DataWarehouse.DataContext
{
    public class WarehouseDataContext : DbContext
    { 
        public WarehouseDataContext(DbContextOptions<WarehouseDataContext> options) : base(options) { }
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
        }
        public DbSet<User> Users { get; set; }
        public DbSet<ChatUser> ChatUsers { get; set; }
        public DbSet<QuestionCommandTable> QuestionCommands { get; set; }
    }
}
