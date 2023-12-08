using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataWarehouse.DataContext
{
    public class ServiceLog
    {
        public string Id { get; set; } = string.Empty;
        public string ServiceName { get; set; } = string.Empty;
        public string ServiceMessage { get; set; } = string.Empty;
        public DateTimeOffset CreatedAt { get; set; }
    }
}
