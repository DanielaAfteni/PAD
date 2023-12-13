#See https://aka.ms/customizecontainer to learn how to customize your debug container and how Visual Studio uses this Dockerfile to build your images for faster debugging.

FROM mcr.microsoft.com/dotnet/aspnet:7.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443
EXPOSE 5217

FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
WORKDIR /src
COPY ["LogConsumer/LogConsumer.csproj", "LogConsumer/"]
COPY ["RabbitMQUtils/RabbitMQUtils.csproj", "RabbitMQUtils/"]
RUN dotnet restore "LogConsumer/LogConsumer.csproj"
COPY . .
WORKDIR "/src/LogConsumer"
RUN dotnet build "LogConsumer.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "LogConsumer.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "LogConsumer.dll"]