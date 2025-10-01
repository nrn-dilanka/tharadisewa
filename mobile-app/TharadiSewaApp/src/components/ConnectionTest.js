import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import api from '../services/api';
import { APP_CONFIG } from '../config/app';

const ConnectionTest = () => {
  const [testResult, setTestResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const testConnection = async () => {
    setIsLoading(true);
    setTestResult(null);

    const results = {
      timestamp: new Date().toLocaleString(),
      baseUrl: APP_CONFIG.API.BASE_URL,
      apiUrl: `${APP_CONFIG.API.BASE_URL}/api`,
      tests: [],
    };

    try {
      // Test 1: Basic server connection
      console.log('🧪 Testing basic server connection...');
      try {
        const response = await fetch(APP_CONFIG.API.BASE_URL, { 
          method: 'GET',
          timeout: 5000,
        });
        results.tests.push({
          name: 'Server Connection',
          status: response.status === 200 || response.status === 404 ? 'success' : 'warning',
          message: `Server responded with status ${response.status}`,
        });
      } catch (error) {
        results.tests.push({
          name: 'Server Connection',
          status: 'error',
          message: `Cannot reach server: ${error.message}`,
        });
      }

      // Test 2: API endpoint test
      console.log('🧪 Testing API endpoints...');
      try {
        const response = await api.get('/');
        results.tests.push({
          name: 'API Root',
          status: 'success',
          message: 'API root endpoint accessible',
        });
      } catch (error) {
        results.tests.push({
          name: 'API Root',
          status: error.response?.status ? 'warning' : 'error',
          message: error.response?.status 
            ? `API responded with ${error.response.status}` 
            : `API connection failed: ${error.message}`,
        });
      }

      // Test 3: Registration status endpoint
      console.log('🧪 Testing registration status endpoint...');
      try {
        const response = await api.get('/auth/registration-status/');
        results.tests.push({
          name: 'Registration Status',
          status: 'success',
          message: `Registration enabled: ${response.data.registration_enabled}`,
          data: response.data,
        });
      } catch (error) {
        results.tests.push({
          name: 'Registration Status',
          status: 'error',
          message: error.response?.data?.detail || error.message || 'Endpoint not available',
        });
      }

      // Test 4: User endpoint (might require auth)
      console.log('🧪 Testing user endpoint...');
      try {
        const response = await api.get('/users/');
        results.tests.push({
          name: 'Users Endpoint',
          status: 'success',
          message: 'Users endpoint accessible',
        });
      } catch (error) {
        results.tests.push({
          name: 'Users Endpoint',
          status: error.response?.status === 401 ? 'warning' : 'error',
          message: error.response?.status === 401 
            ? 'Endpoint requires authentication (expected)' 
            : (error.response?.data?.detail || error.message || 'Endpoint not available'),
        });
      }

    } catch (error) {
      results.tests.push({
        name: 'General Error',
        status: 'error',
        message: error.message,
      });
    }

    setTestResult(results);
    setIsLoading(false);
  };

  useEffect(() => {
    testConnection();
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return '#28a745';
      case 'warning': return '#ffc107';
      case 'error': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'error': return '❌';
      default: return '❓';
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🔗 Connection Test</Text>
      
      <TouchableOpacity 
        style={styles.testButton} 
        onPress={testConnection}
        disabled={isLoading}
      >
        {isLoading ? (
          <ActivityIndicator size="small" color="#fff" />
        ) : (
          <Text style={styles.testButtonText}>Run Connection Test</Text>
        )}
      </TouchableOpacity>

      {testResult && (
        <View style={styles.results}>
          <Text style={styles.resultTitle}>Test Results</Text>
          <Text style={styles.timestamp}>{testResult.timestamp}</Text>
          <Text style={styles.url}>API URL: {testResult.apiUrl}</Text>
          
          {testResult.tests.map((test, index) => (
            <View key={index} style={styles.testItem}>
              <Text style={styles.testName}>
                {getStatusIcon(test.status)} {test.name}
              </Text>
              <Text style={[styles.testMessage, { color: getStatusColor(test.status) }]}>
                {test.message}
              </Text>
              {test.data && (
                <Text style={styles.testData}>
                  {JSON.stringify(test.data, null, 2)}
                </Text>
              )}
            </View>
          ))}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    margin: 10,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
  },
  testButton: {
    backgroundColor: '#007bff',
    padding: 12,
    borderRadius: 6,
    alignItems: 'center',
    marginBottom: 15,
  },
  testButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  results: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#dee2e6',
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  timestamp: {
    fontSize: 12,
    color: '#6c757d',
    marginBottom: 5,
  },
  url: {
    fontSize: 12,
    color: '#6c757d',
    marginBottom: 15,
  },
  testItem: {
    marginBottom: 12,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  testName: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 4,
  },
  testMessage: {
    fontSize: 13,
    marginBottom: 4,
  },
  testData: {
    fontSize: 11,
    fontFamily: 'monospace',
    backgroundColor: '#f8f9fa',
    padding: 8,
    borderRadius: 4,
    color: '#495057',
  },
});

export default ConnectionTest;