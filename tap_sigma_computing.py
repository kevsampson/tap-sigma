#!/usr/bin/env python3
"""
Tests for tap-sigma-computing
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests

# Import the tap (assuming the main file is named tap_sigma_computing.py)
from tap_sigma_computing import SigmaComputingClient, SigmaComputingTap


class TestSigmaComputingClient(unittest.TestCase):
    """Test cases for SigmaComputingClient"""
    
    def setUp(self):
        self.config = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'base_url': 'https://aws-api.sigmacomputing.com'
        }
        self.client = SigmaComputingClient(self.config)
    
    def test_init(self):
        """Test client initialization"""
        self.assertEqual(self.client.client_id, 'test_client_id')
        self.assertEqual(self.client.client_secret, 'test_client_secret')
        self.assertEqual(self.client.base_url, 'https://aws-api.sigmacomputing.com')
        self.assertEqual(self.client.token_url, 'https://aws-api.sigmacomputing.com/v2/auth/token')
        self.assertEqual(self.client.api_url, 'https://aws-api.sigmacomputing.com/v2')
    
    @patch('requests.post')
    def test_get_access_token_success(self, mock_post):
        """Test successful token acquisition"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_token',
            'expires_in': 3600
        }
        mock_post.return_value = mock_response
        
        token = self.client._get_access_token()
        
        self.assertEqual(token, 'test_token')
        self.assertEqual(self.client.access_token, 'test_token')
        self.assertIsNotNone(self.client.token_expires_at)
        
        # Verify the POST request was made correctly
        mock_post.assert_called_once_with(
            'https://aws-api.sigmacomputing.com/v2/auth/token',
            data={
                'grant_type': 'client_credentials',
                'client_id': 'test_client_id',
                'client_secret': 'test_client_secret'
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
    
    @patch('requests.post')
    def test_get_access_token_failure(self, mock_post):
        """Test token acquisition failure"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.client._get_access_token()
        
        self.assertIn('Failed to get access token', str(context.exception))
    
    @patch('requests.post')
    def test_token_reuse(self, mock_post):
        """Test that valid tokens are reused"""
        # Set up a valid token that hasn't expired
        self.client.access_token = 'existing_token'
        self.client.token_expires_at = datetime.now() + timedelta(minutes=30)
        
        token = self.client._get_access_token()
        
        # Should return existing token without making HTTP request
        self.assertEqual(token, 'existing_token')
        mock_post.assert_not_called()
    
    @patch.object(SigmaComputingClient, '_get_access_token')
    @patch('requests.Session.get')
    def test_make_request_success(self, mock_get, mock_get_token):
        """Test successful API request"""
        mock_get_token.return_value = 'test_token'
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test_data'}
        mock_get.return_value = mock_response
        
        result = self.client._make_request('workbooks')
        
        self.assertEqual(result, {'data': 'test_data'})
        mock_get.assert_called_once()
        
        # Check that the request was made with correct headers
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], 'https://aws-api.sigmacomputing.com/v2/workbooks')
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test_token')
    
    @patch.object(SigmaComputingClient, '_get_access_token')
    @patch('requests.Session.get')
    def test_make_request_token_refresh(self, mock_get, mock_get_token):
        """Test automatic token refresh on 401 response"""
        mock_get_token.side_effect = ['expired_token', 'new_token']
        
        # First response: 401 Unauthorized
        mock_response_401 = Mock()
        mock_response_401.status_code = 401
        
        # Second response: 200 OK
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'data': 'success'}
        
        mock_get.side_effect = [mock_response_401, mock_response_200]
        
        result = self.client._make_request('workbooks')
        
        self.assertEqual(result, {'data': 'success'})
        self.assertEqual(mock_get.call_count, 2)
        self.assertEqual(mock_get_token.call_count, 2)
    
    @patch.object(SigmaComputingClient, '_make_request')
    def test_get_paginated_data(self, mock_make_request):
        """Test pagination handling"""
        # Mock responses for pagination
        mock_make_request.side_effect = [
            {
                'entries': [{'id': 1}, {'id': 2}],
                'total': 3
            },
            {
                'entries': [{'id': 3}],
                'total': 3
            }
        ]
        
        results = list(self.client.get_paginated_data('workbooks'))
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], {'id': 1})
        self.assertEqual(results[1], {'id': 2})
        self.assertEqual(results[2], {'id': 3})
        
        # Verify pagination parameters
        self.assertEqual(mock_make_request.call_count, 2)
        
        # First call should have offset=0
        args1, kwargs1 = mock_make_request.call_args_list[0]
        self.assertEqual(kwargs1['params']['offset'], 0)
        
        # Second call should have offset=2
        args2, kwargs2 = mock_make_request.call_args_list[1]
        self.assertEqual(kwargs2['params']['offset'], 2)


class TestSigmaComputingTap(unittest.TestCase):
    """Test cases for SigmaComputingTap"""
    
    def setUp(self):
        self.config = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'base_url': 'https://aws-api.sigmacomputing.com'
        }
        self.state = {}
        self.tap = SigmaComputingTap(self.config, self.state)
    
    def test_init(self):
        """Test tap initialization"""
        self.assertEqual(self.tap.config, self.config)
        self.assertEqual(self.tap.state, {})
        self.assertIsInstance(self.tap.client, SigmaComputingClient)
        self.assertIn('workbooks', self.tap.streams)
        self.assertIn('users', self.tap.streams)
    
    def test_discover(self):
        """Test catalog discovery"""
        catalog = self.tap.discover()
        
        # Should have all expected streams
        stream_names = [stream.stream for stream in catalog.streams]
        expected_streams = ['workbooks', 'users', 'teams', 'connections', 'datasets', 'folders', 'user_attributes']
        
        for expected_stream in expected_streams:
            self.assertIn(expected_stream, stream_names)
        
        # Check workbooks stream details
        workbooks_stream = next(s for s in catalog.streams if s.stream == 'workbooks')
        self.assertEqual(workbooks_stream.key_properties, ['workbookId'])
        self.assertEqual(workbooks_stream.replication_method, 'INCREMENTAL')
        self.assertEqual(workbooks_stream.replication_key, 'updatedAt')
        
        # Check schema has required properties
        schema_props = workbooks_stream.schema.to_dict()['properties']
        self.assertIn('workbookId', schema_props)
        self.assertIn('name', schema_props)
        self.assertIn('updatedAt', schema_props)
    
    @patch.object(SigmaComputingClient, 'get_paginated_data')
    def test_sync_workbooks(self, mock_get_data):
        """Test workbooks stream sync"""
        # Mock workbook data
        mock_workbooks = [
            {
                'workbookId': 'wb1',
                'name': 'Test Workbook 1',
                'createdAt': '2024-01-01T00:00:00Z',
                'updatedAt': '2024-01-01T12:00:00Z',
                'tags': ['test'],
                'isSample': False
            },
            {
                'workbookId': 'wb2', 
                'name': 'Test Workbook 2',
                'createdAt': '2024-01-02T00:00:00Z',
                'updatedAt': '2024-01-02T12:00:00Z',
                'tags': [],
                'isSample': True
            }
        ]
        mock_get_data.return_value = iter(mock_workbooks)
        
        # Mock singer.write_message to capture output
        with patch('singer.write_message') as mock_write:
            latest_bookmark = self.tap._sync_workbooks()
        
        # Should return the latest updatedAt value
        self.assertEqual(latest_bookmark, '2024-01-02T12:00:00Z')
        
        # Should have called write_message for each record
        record_messages = [call for call in mock_write.call_args_list if call[0][0].type == 'RECORD']
        self.assertEqual(len(record_messages), 2)
        
        # Check first record
        first_record = record_messages[0][0][0].record
        self.assertEqual(first_record['workbookId'], 'wb1')
        self.assertEqual(first_record['name'], 'Test Workbook 1')
        self.assertEqual(first_record['tags'], ['test'])
        self.assertEqual(first_record['isSample'], False)
    
    def test_sync_workbooks_with_bookmark(self):
        """Test workbooks sync with existing bookmark"""
        with patch.object(self.tap.client, 'get_paginated_data') as mock_get_data:
            mock_get_data.return_value = iter([])
            
            bookmark = '2024-01-01T00:00:00Z'
            self.tap._sync_workbooks(bookmark)
            
            # Should pass bookmark as updatedAfter parameter
            mock_get_data.assert_called_once_with('workbooks', {'updatedAfter': bookmark})


class TestIntegration(unittest.TestCase):
    """Integration tests (require real API credentials)"""
    
    def setUp(self):
        # These tests only run if environment variables are set
        import os
        self.client_id = os.getenv('SIGMA_CLIENT_ID')
        self.client_secret = os.getenv('SIGMA_CLIENT_SECRET')
        self.base_url = os.getenv('SIGMA_BASE_URL', 'https://aws-api.sigmacomputing.com')
        
        self.skip_integration = not (self.client_id and self.client_secret)
        
        if not self.skip_integration:
            self.config = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'base_url': self.base_url
            }
            self.client = SigmaComputingClient(self.config)
    
    def test_real_authentication(self):
        """Test authentication with real API"""
        if self.skip_integration:
            self.skipTest("Integration test credentials not provided")
        
        # This should not raise an exception
        token = self.client._get_access_token()
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
    
    def test_real_api_request(self):
        """Test making real API request"""
        if self.skip_integration:
            self.skipTest("Integration test credentials not provided")
        
        # Try to get workbooks (should work even if empty)
        try:
            workbooks = list(self.client.get_paginated_data('workbooks'))
            # Should return a list (even if empty)
            self.assertIsInstance(workbooks, list)
        except Exception as e:
            self.fail(f"Failed to fetch workbooks: {e}")


if __name__ == '__main__':
    unittest.main()
