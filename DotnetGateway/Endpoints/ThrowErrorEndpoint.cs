using FastEndpoints;

namespace DotnetGateway.Endpoints
{
    public class ThrowErrorEndpoint : EndpointWithoutRequest
    {
        public override void Configure()
        {
            Get("/api/throw");
            AllowAnonymous();
        }
        public override async Task HandleAsync(CancellationToken ct)
        {
            throw new Exception("We will reach it!");
        }
    }
}
