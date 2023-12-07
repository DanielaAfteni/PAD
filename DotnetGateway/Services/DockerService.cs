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

        public async Task CreateAndRunContainerAsync(string imageName, string containerName, string networkName, string hostName, string machinePort, string virtualPort)
        {
            await RunContainerAsync(imageName, containerName, networkName, hostName, machinePort, virtualPort);
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
                Env = new List<string>
        {
            "DB_USER_MASTER=postgres",
            "DB_PASSWORD_MASTER=password",
            "DB_HOST_MASTER=chat-gpt-database",
            "DB_NAME_MASTER=chat-gpt-db",
            "DB_USER_REPLICA_1=postgres",
            "DB_PASSWORD_REPLICA_1=password",
            "DB_HOST_REPLICA_1=chat-gpt-database1",
            "DB_NAME_REPLICA_1=chat-gpt-db1",
            "DB_USER_REPLICA_2=postgres",
            "DB_PASSWORD_REPLICA_2=password",
            "DB_HOST_REPLICA_2=chat-gpt-database2",
            "DB_NAME_REPLICA_2=chat-gpt-db2",
            "DB_USER_REPLICA_3=postgres",
            "DB_PASSWORD_REPLICA_3=password",
            "DB_HOST_REPLICA_3=chat-gpt-database3",
            "DB_NAME_REPLICA_3=chat-gpt-db3",
            "DB_USER_REPLICA_4=postgres",
            "DB_PASSWORD_REPLICA_4=password",
            "DB_HOST_REPLICA_4=chat-gpt-database4",
            "DB_NAME_REPLICA_4=chat-gpt-db4",
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
