# from flask import Flask, request, jsonify
# import openai
# import os
# from dotenv import load_dotenv

# app = Flask(__name__)

# # load_dotenv()
# # Replace 'YOUR_API_KEY' with your actual OpenAI API key
# openai.api_key = "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"


# @app.route('/chat', methods=['POST'])
# def chat():
#     # Get the user's question from the request
#     user_input = request.json.get('question', '')
#     print(user_input)

#     # Make a request to ChatGPT
#     response = openai.Completion.create(
#         engine="text-davinci-002",
#         prompt=f"Answer the following question: {user_input}",
#         max_tokens=50  # Adjust this based on your requirements
#     )

#     # Extract the response from ChatGPT
#     bot_response = response.choices[0].text.strip()

#     return jsonify({"response": bot_response})

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify
import openai

# Replace 'YOUR_API_KEY' with your actual GPT-3 API key
api_key = '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'

# Initialize Flask
app = Flask(__name__)

# Initialize the OpenAI API client
openai.api_key = api_key

# Define an endpoint for asking questions
@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        # Get the question from the request data
        data = request.json
        question = data['question']

        # Define a prompt for GPT-3
        prompt = f"Answer the following question:\n{question}\nAnswer:"

        # Generate a response from GPT-3
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=100  # You can adjust this as needed
        )

        # Extract the answer from the response
        answer = response.choices[0].text.strip()

        # Return the answer as a JSON response
        return jsonify({'answer': answer})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
