import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Agregar el directorio lambda al path
sys.path.append(os.path.dirname(__file__))

from lambda_function import SpaceXDataProcessor, lambda_handler

class TestSpaceXDataProcessor(unittest.TestCase):
    
    def setUp(self):
        self.processor = SpaceXDataProcessor()
        self.sample_launch = {
            'id': 'test123',
            'name': 'Test Mission',
            'success': True,
            'upcoming': False,
            'date_utc': '2024-01-01T00:00:00.000Z',
            'date_unix': 1704067200,
            'rocket': {'name': 'Falcon 9'},
            'launchpad': {'name': 'KSC LC-39A', 'full_name': 'Kennedy Space Center Launch Complex 39A'},
            'payloads': [{'name': 'Test Satellite', 'type': 'Satellite'}],
            'links': {
                'patch': {'small': 'https://images2.imgbox.com/test.png'},
                'webcast': 'https://youtube.com/test',
                'article': 'https://spaceflightnow.com/test',
                'wikipedia': 'https://en.wikipedia.org/test'
            },
            'details': 'Test launch details',
            'flight_number': 1
        }
    
    @patch('lambda_function.requests.get')
    def test_fetch_launches_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [self.sample_launch]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.processor.fetch_launches_data()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Test Mission')
    
    def test_transform_launch_data_success(self):
        transformed = self.processor.transform_launch_data(self.sample_launch)
        
        self.assertEqual(transformed['mission_name'], 'Test Mission')
        self.assertEqual(transformed['status'], 'success')
        self.assertEqual(transformed['rocket_name'], 'Falcon 9')
        self.assertEqual(transformed['payload_names'], ['Test Satellite'])
    
    def test_transform_launch_data_upcoming(self):
        upcoming_launch = self.sample_launch.copy()
        upcoming_launch['upcoming'] = True
        upcoming_launch['success'] = None
        
        transformed = self.processor.transform_launch_data(upcoming_launch)
        self.assertEqual(transformed['status'], 'upcoming')
    
    @patch('lambda_function.table')
    def test_upsert_launch_data_success(self, mock_table):
        mock_table.put_item.return_value = {}
        
        result = self.processor.upsert_launch_data({'launch_id': 'test123'})
        self.assertTrue(result)

class TestLambdaHandler(unittest.TestCase):
    
    @patch('lambda_function.SpaceXDataProcessor')
    def test_lambda_handler_success(self, mock_processor):
        mock_instance = MagicMock()
        mock_instance.process_launches.return_value = {
            'total_processed': 10,
            'successful_upserts': 10,
            'failed_upserts': 0
        }
        mock_processor.return_value = mock_instance
        
        response = lambda_handler({}, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['message'], 'SpaceX data processed successfully')

if __name__ == '__main__':
    unittest.main()
