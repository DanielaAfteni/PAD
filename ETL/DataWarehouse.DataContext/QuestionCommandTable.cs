using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataWarehouse.DataContext
{
    public class QuestionCommandTable
    {
        public int Id { get; set; }
        public int ExternalId { get; set; }

        public string? NewQuestionCommand { get; set; }

        public string? NewQuestionPrompt { get; set; }
    }
}
