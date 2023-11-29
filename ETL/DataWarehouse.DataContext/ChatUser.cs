using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataWarehouse.DataContext
{
    public class ChatUser
    {
        public int Id { get; set; }
        public string Name { get; set; } = null!;
        public string NameAppearance { get; set; } = null!;
    }
}
