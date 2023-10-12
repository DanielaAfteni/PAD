import unittest
from chat_gpt_service.chat_gpt_service import app
import json

class ChatGptServiceTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_tts_endpoint(self):
        # Define a sample data payload for the POST request
        data = {
            'user_email': 'test@example.com',
            'phrase': 'Hello, world!',
            'question': 'What is the meaning of life?'
        }

        # Send a POST request to the '/chat' endpoint
        response = self.app.post('/chat', data=data)

        # Check the response status code
        self.assertEqual(response.status_code, 201)

        # Parse the response JSON
        response_data = json.loads(response.data.decode('utf-8'))

        # Add more assertions to check the response data as needed

    def test_status_endpoint(self):
        # Send a GET request to the '/status' endpoint
        response = self.app.get('/status')

        # Check the response status code
        self.assertEqual(response.status_code, 200)

        # Parse the response JSON
        response_data = json.loads(response.data.decode('utf-8'))

        # Add more assertions to check the response data as needed

if __name__ == '__main__':
    unittest.main()


# py unittest_chat_gpt.py