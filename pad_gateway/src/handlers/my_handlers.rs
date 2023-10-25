use std::{sync::Arc, vec::IntoIter};
use axum::http::StatusCode;
use reqwest;
use tokio::sync::Mutex;
use std::iter::Cycle;

pub async fn weatherforecast_handler(state: Arc<Mutex<Cycle<IntoIter<String>>>>) -> (StatusCode, String) {
    let mut state = state.lock().await; // Lock the Mutex
    let url = state.next();
    match url {
        Some(url) => {
            match reqwest::get(&url).await {
                Ok(res) => (StatusCode::OK, res.text().await.unwrap()),
                Err(err) => (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    format!("Server failed with {}", err),
                )
            }
        }
        None => (
            StatusCode::BAD_REQUEST,
            "URL is missing".to_string(),
        )
    }
}
pub async fn weatherforecast_handler_simple(url:&str) -> (StatusCode,String) {
    match reqwest::get(url).await {
                Ok(res) => (StatusCode::OK, res.text().await.unwrap()),
                Err(err) => (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    format!("Server failed with {}", err),
                ),
            }
}
