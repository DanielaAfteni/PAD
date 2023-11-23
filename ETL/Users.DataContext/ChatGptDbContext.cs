using System;
using System.Collections.Generic;
using Microsoft.EntityFrameworkCore;

namespace Users.DataContext;

public partial class ChatGptDbContext : DbContext
{
    public ChatGptDbContext(DbContextOptions<ChatGptDbContext> options)
        : base(options)
    {
    }

    public virtual DbSet<ChatUser> ChatUsers { get; set; }

    public virtual DbSet<QuestionCommandTable> QuestionCommandTables { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<ChatUser>(entity =>
        {
            entity.HasKey(e => e.Name).HasName("chat_users_pkey");

            entity.ToTable("chat_users");

            entity.Property(e => e.Name)
                .HasMaxLength(255)
                .HasColumnName("name");
            entity.Property(e => e.NameAppearance)
                .HasMaxLength(255)
                .HasColumnName("name_appearance");
        });

        modelBuilder.Entity<QuestionCommandTable>(entity =>
        {
            entity.HasKey(e => e.Id).HasName("question_command_table_pkey");

            entity.ToTable("question_command_table");

            entity.HasIndex(e => e.NewQuestionCommand, "question_command_table_new_question_command_key").IsUnique();

            entity.Property(e => e.Id).HasColumnName("id");
            entity.Property(e => e.NewQuestionCommand)
                .HasMaxLength(255)
                .HasColumnName("new_question_command");
            entity.Property(e => e.NewQuestionPrompt)
                .HasMaxLength(255)
                .HasColumnName("new_question_prompt");
        });

        OnModelCreatingPartial(modelBuilder);
    }

    partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
}
