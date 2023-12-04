using Docker.DotNet.Models;
using Docker.DotNet;

namespace DotnetGateway.Services
{
    public class DockerService
    {
        private readonly IDockerClient _dockerClient;
        public DockerService()
        {
            _dockerClient = new DockerClientConfiguration(new Uri("tcp://host.docker.internal:2375")).CreateClient();
            //_dockerClient = new DockerClientConfiguration(new Uri("tcp://localhost:2375")).CreateClient();
        }

        public async Task CreateAndRunContainerAsync(string imageName, string containerName, string networkName, string hostName,string machinePort,string virtualPort)
        {
            await RunContainerAsync(imageName, containerName, networkName, hostName,machinePort,virtualPort);
        }

        private async Task RunContainerAsync(string imageName, string containerName, string networkName, string hostName, string machinePort, string virtualPort)
        {
            var createParameters = new CreateContainerParameters
            {
                Image = imageName,
                Name = containerName,
                Hostname = hostName,
                NetworkingConfig = new NetworkingConfig
                {
                    EndpointsConfig = new Dictionary<string, EndpointSettings>
                {
                    { networkName, new EndpointSettings() },
                },
                },
                ExposedPorts = new Dictionary<string, EmptyStruct>
                {
                    {
                        virtualPort,new EmptyStruct()
                    }
                },
                HostConfig = new HostConfig
                {
                    PortBindings = new Dictionary<string, IList<PortBinding>>
                    {
                        {
                            virtualPort, new List<PortBinding>
                            {
                                new() { HostPort = machinePort }
                            }
                        },
            // Add more port bindings as needed
        },
                },
            };

            var response = await _dockerClient.Containers.CreateContainerAsync(createParameters);

            await _dockerClient.Containers.StartContainerAsync(response.ID, new ContainerStartParameters());
        }
        public async Task<List<ContainerInfo>> FindContainersByNameAsync(string keyword)
        {
            var containers = await _dockerClient.Containers.ListContainersAsync(new ContainersListParameters());

            return containers
                .Where(container => container.Names.Any(name => name.Contains(keyword, StringComparison.OrdinalIgnoreCase)))
                .Select(container =>
                new ContainerInfo
                {
                    ContainerId = container.ID,
                    HostPort = GetHostPortFromContainer(container),
                }).ToList();
        }
        private int GetHostPortFromContainer(ContainerListResponse container)
        {
            var firstExposedPort = container.Ports.FirstOrDefault();
            return firstExposedPort?.PublicPort ?? 0;
        }
        public class ContainerInfo
        {
            public string ContainerId { get; set; }
            public int HostPort { get; set; }
        }

    }

}
