using DotnetGateway.Services;
using FastEndpoints;
using System.Text;
using System.Text.Json;

namespace DotnetGateway.Endpoints.ChatGpt
{
    public class ChatGptGetEndpoint : Endpoint<Request, Response>
    {
        public HttpClient HttpClient { get; set; }
        public DockerService DockerService { get; set; }
        public LoadBalancerService LoadBalancerService { get; set; }
        public override void Configure()
        {
            Post("/api/ask");
            AllowAnonymous();
        }

        public override async Task HandleAsync(Request req, CancellationToken ct)
        {
            var jsonResponse = await LoadBalancerService.Balance(req,1);
            await SendAsync(JsonSerializer.Deserialize<Response>(jsonResponse), 200, ct);

        }
    }
    public class Request
    {
        public string user_email { get; set; }
        public string question { get; set; }
    }
    public class Response
    {
        public string response { get; set; }
    }
}
