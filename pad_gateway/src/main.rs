#[path="handlers/my_handlers.rs"]
mod my_handlers;
#[path="load_balancers/loadbalancer.rs"]
mod loadbalancer;
use std::{fs::File, sync::Arc};
use std::io::Read;
use axum::{Router, routing::get};
use my_handlers::weatherforecast_handler;
use my_handlers::weatherforecast_handler_simple;
use serde_derive::Deserialize;
use tokio::sync::Mutex;
use std::net::SocketAddr;
#[tokio::main]
async fn main() {
    let mut config_file = File::open("config.toml").expect("Unable to open config file");
    let mut config_toml = String::new();
    config_file.read_to_string(&mut config_toml).expect("Unable to read config file");

    let config:AppConfig = toml::from_str(&config_toml).expect("Failed to parse TOML");
    let urls = Arc::new(Mutex::new(config.addresses.into_iter().cycle()));
   
    let app = Router::new().route("/", get(|| {
        
        weatherforecast_handler(urls)
    }))
    .route("/simple", get(|| weatherforecast_handler_simple("http://localhost:7070/weatherforecast")));
    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));

    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();  
}

#[derive(Debug, Deserialize)]
struct AppConfig {
    addresses: Vec<String>,
}   