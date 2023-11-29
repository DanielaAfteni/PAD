using System;
using System.Collections.Generic;

namespace Users.DataContext;

public partial class QuestionCommandTable
{
    public int Id { get; set; }

    public string? NewQuestionCommand { get; set; }

    public string? NewQuestionPrompt { get; set; }
}
