using DotnetGateway.Services;
using FastEndpoints;
using System.Text.Json;

namespace DotnetGateway.Endpoints.ChatGpt
{
    public class AddCommandEndpoint : Endpoint<AddCommandRequest, AddCommandResponse>
    {
        public HttpClient HttpClient { get; set; }
        public DockerService DockerService { get; set; }
        public LoadBalancerService LoadBalancerService { get; set; }
        public override void Configure()
        {
            Post("/api/add");
            AllowAnonymous();
        }

        public override async Task HandleAsync(AddCommandRequest req, CancellationToken ct)
        {

            var jsonResponse = await LoadBalancerService.Balance(req);
            await SendAsync(JsonSerializer.Deserialize<AddCommandResponse>(jsonResponse), 200, ct);
        }
    }
    public class AddCommandRequest
    {
        public string command { get; set; }
        public string question { get; set; }
    }
    public class AddCommandResponse
    {
        public string response { get; set; }
    }
}
