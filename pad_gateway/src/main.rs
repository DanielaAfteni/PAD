#[path = "models/chat_gpt.rs"]
mod chat_gpt;
#[path = "handlers/my_handlers.rs"]
mod my_handlers;
use axum::{routing::post, Router};
use my_handlers::chat_gpt_handler;
use serde_derive::Deserialize;
use std::io::Read;
use std::net::SocketAddr;
use std::{fs::File, sync::Arc};
use tokio::sync::Mutex;
use tower::ServiceBuilder;
use tower_http::trace::TraceLayer;
#[tokio::main]
async fn main() {
    print!("hello");
    let mut config_file = File::open("config.toml").expect("Unable to open config file");
    let mut config_toml = String::new();
    config_file
        .read_to_string(&mut config_toml)
        .expect("Unable to read config file");

    let config: AppConfig = toml::from_str(&config_toml).expect("Failed to parse TOML");
    let urls = Arc::new(Mutex::new(config.addresses.into_iter().cycle()));
    let app = Router::new()
        .route("/chat", post(chat_gpt_handler))
        .with_state(urls)
        .layer(ServiceBuilder::new().layer(TraceLayer::new_for_http()));
    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));

    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap()
}
#[derive(Debug, Deserialize)]
struct AppConfig {
    addresses: Vec<String>,
}
