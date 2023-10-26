FROM rust:latest as builder

WORKDIR /rust-api-deployment-example

COPY . .

RUN cargo build 

EXPOSE 8080

CMD cargo run