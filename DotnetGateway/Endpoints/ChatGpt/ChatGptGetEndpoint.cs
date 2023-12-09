using DotnetGateway.Services;
using FastEndpoints;
using System.Text;
using System.Text.Json;

namespace DotnetGateway.Endpoints.ChatGpt
{
    public class ChatGptGetEndpoint : Endpoint<ChatGptRequest, ChatGptResponse>
    {
        public HttpClient HttpClient { get; set; }
        public DockerService DockerService { get; set; }
        public LoadBalancerService LoadBalancerService { get; set; }
        public override void Configure()
        {
            Post("/api/ask");
            AllowAnonymous();
        }

        public override async Task HandleAsync(ChatGptRequest req, CancellationToken ct)
        {
            var jsonResponse = await LoadBalancerService.Balance(req);
            await SendAsync(JsonSerializer.Deserialize<ChatGptResponse>(jsonResponse), 200, ct);
        }
    }
    public class ChatGptRequest
    {
        public string user_email { get; set; }
        public string question { get; set; }
    }
    public class ChatGptResponse
    {
        public string response { get; set; }
    }
}
