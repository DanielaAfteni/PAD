import unittest
import chat_gpt_service  # Import your Flask application
from datetime import datetime

class ChatGPTServiceTest(unittest.TestCase):
    
    def setUp(self):
        # Create a test client for the Flask application
        self.app = chat_gpt_service.app.test_client()
        self.app.testing = True

    def test_chat_route(self):
        # Test the '/chat' route
        response = self.app.post('/chat', data={'user_email': 'test@test.com', 'phrase': 'Hello', 'question': 'What is 2+2?'})
        self.assertEqual(response.status_code, 200)

        # You can add more assertions to test the response content
        # For example, assert that the response contains the expected data.

    def test_get_status_route(self):
        # Test the '/status' route
        response = self.app.get('/status')
        self.assertEqual(response.status_code, 200)

        # You can add more assertions to test the response content
        # For example, assert that the response contains the expected status.

    def test_create_new_obj(self):
        # Test the create_new_obj function
        current_time = datetime.now()
        new_obj = chat_gpt_service.create_new_obj("test@test.com", "Hello", current_time)
        self.assertEqual(new_obj["user_email"], "test@test.com")
        self.assertEqual(new_obj["phrase"], "Hello")
        # Add more assertions as needed

    # Add more test cases as needed for other functions and routes

if __name__ == '__main__':
    unittest.main()

# py chat_gpt_service\unittest_chat_gpt.py