use serde_derive::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct ChatGPTRequest {
    user_email: String,
    question: String,
}
#[derive(Serialize, Deserialize, Debug)]
pub struct ChatGPTResponse {
    pub response: String,
}
