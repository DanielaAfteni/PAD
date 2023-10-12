import unittest
from tts_stt_service.tts_stt_service import app  # Import your Flask app from the correct module
from flask import Flask

class TTSSTTServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_tts_endpoint(self):
        response = self.app.post('/tts', data={
            'user_email': 'test@example.com',
            'phrase': 'Hello, world!',
            'tts': 'This is a test.'
        })

        self.assertEqual(response.status_code, 201)  # Ensure a successful response

    def test_stt_endpoint(self):
        response = self.app.post('/stt', data={
            'user_email': 'test@example.com',
            'phrase': 'Hello, world!',
            'stt': 'This is a test.'
        })

        self.assertEqual(response.status_code, 201)  # Ensure a successful response

    def test_status_endpoint(self):
        response = self.app.get('/status')

        self.assertEqual(response.status_code, 200)  # Ensure a successful response
        self.assertIn(b'"status":"Healthy"', response.data)  # Ensure the service is reported as healthy

if __name__ == '__main__':
    unittest.main()

# py unittest_tts_stt.py