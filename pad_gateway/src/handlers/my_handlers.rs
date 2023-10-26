use axum::extract::State;
use axum::response::IntoResponse;
use axum::{http::StatusCode, Json};
use reqwest;
use std::iter::Cycle;
use std::{sync::Arc, vec::IntoIter};
use tokio::sync::Mutex;

use crate::chat_gpt::{ChatGPTRequest, ChatGPTResponse};

pub async fn chat_gpt_handler(
    State(state): State<Arc<Mutex<Cycle<IntoIter<String>>>>>,
    Json(request): Json<ChatGPTRequest>,
) -> Result<impl IntoResponse, StatusCode> {
    let mut state = state.lock().await; // Lock the Mutex
    let url = state.next();
    match url {
        Some(url) => {
            // let gpt_response: ChatGPTResponse = ChatGPTResponse {
            //     response: "hello".to_string(),
            // };
            if let Ok(gpt_response) = get_chat_gpt_response(&url, &request).await {
                Ok(gpt_response)
            } else {
                let response = ChatGPTResponse {
                    response: "Invalid Url".to_string(),
                };
                Ok(Json(response))
            }
        }
        None => {
            let response = ChatGPTResponse {
                response: "Invalid Url".to_string(),
            };
            Ok(Json(response))
        }
    }
}
pub async fn get_chat_gpt_response(
    url: &str,
    request: &ChatGPTRequest,
) -> Result<Json<ChatGPTResponse>, Box<dyn std::error::Error>> {
    let gpt_response: ChatGPTResponse = reqwest::Client::new()
        .post(url)
        .json(&request)
        .send()
        .await?
        .json()
        .await?;
    Ok(Json(gpt_response))
}
