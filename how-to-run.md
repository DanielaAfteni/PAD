### How To Run Existing Services

1. Go to root folder where docker-compose.yml is located.

2. ```
   docker build -t notification-server -f NotificationServiceServer/Dockerfile .

   docker build -t log-consumer -f LogConsumer/Dockerfile .

   docker compose up -d
   ```
