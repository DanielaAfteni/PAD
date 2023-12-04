using DotnetGateway.Endpoints.ChatGpt;
using Microsoft.Extensions.Options;
using System.Text;
using System.Text.Json;

namespace DotnetGateway.Services
{
    public class LoadBalancerService
    {
        private ReplicaConfiguration _configuration { get; set; }
        private List<Uri> _addresses = [];
        private DockerService _dockerService;
        private HttpClient _httpClient;
        private int _nextReplicaIndex = 0;
        public LoadBalancerService(IOptions<ReplicaConfiguration> configuration, DockerService dockerService, HttpClient client)
        {
            _configuration = configuration.Value;
            _dockerService = dockerService;
            _httpClient = client;
        }

        public async Task<string> Balance(Request req,int depth)
        {
            if(depth > 10) { return ""; }
            try
            {
                using var jsonContent = new StringContent(JsonSerializer.Serialize(req), Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync(await GetNextReplicaAddress(), jsonContent);
                var jsonResponse = await response.Content.ReadAsStringAsync();
                return jsonResponse;
            }catch(Exception ex) 
            {
                Thread.Sleep(1000);
                return await Balance(req,++depth);
            }

        }
        private async Task ManageAddresses()
        {
            await CheckExistingContainers();
            var count = _addresses.Count;
            for (int i = 0; i < _configuration.NumberOfReplicas - count; i++)
            {
                var machinePort = GetAvailablePort();
                await _dockerService.CreateAndRunContainerAsync(
                    _configuration.ImageName,
                    $"{_configuration.ContainerName}{Guid.NewGuid().ToString("N")[..8]}"
                    , _configuration.NetworkName,
                    _configuration.HostName, machinePort, _configuration.VirtualPort);
                var newAddress = new Uri($"http://{_configuration.ExternalHost}:{machinePort}/chat");
                _addresses.Add(newAddress);
            }
        }
        private async Task CheckExistingContainers()
        {
            var containerInfo = await _dockerService.FindContainersByNameAsync(_configuration.ContainerName);
            var listOfContainerUris = new List<Uri>();
            containerInfo.ForEach(x =>
            {
                listOfContainerUris.Add(new Uri($"http://{_configuration.ExternalHost}:{x.HostPort}/chat"));
            });
            _addresses = new(listOfContainerUris);
        }
        private async Task<Uri> GetNextReplicaAddress()
        {

            await ManageAddresses();
            var selectedAddress = _addresses[_nextReplicaIndex];

            _nextReplicaIndex = (_nextReplicaIndex + 1) % _addresses.Count;

            return selectedAddress;
        }
        private string GetAvailablePort()
        {
            string[] rangeParts = _configuration.PortRange.Split('-');
            if (rangeParts.Length != 2 || !int.TryParse(rangeParts[0], out int startPort) || !int.TryParse(rangeParts[1], out int endPort))
            {
                throw new ArgumentException("Invalid port range format");
            }
            List<int> allPorts = new(Enumerable.Range(startPort, endPort - startPort + 1));
            _addresses.ForEach(a =>
            {
                if (a.Port > 0)
                {
                    allPorts.Remove(a.Port);
                }
            });
            if (allPorts.Count > 0)
            {
                return allPorts[new Random().Next(allPorts.Count)].ToString();
            }
            throw new InvalidOperationException("No available ports in the specified range");
        }
    }
    public class ReplicaConfiguration
    {
        public int NumberOfReplicas { get; set; }
        public string PortRange { get; set; }
        public string HostName { get; set; }
        public string ImageName { get; set; }
        public string ContainerName { get; set; }
        public string NetworkName { get; set; }
        public string VirtualPort { get; set; }
        public string ExternalHost { get; set; }
    }
}
