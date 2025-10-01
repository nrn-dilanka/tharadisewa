import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';

const LoadingScreen = ({ message = 'Loading...', size = 'large', color = '#007bff' }) => {
  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <ActivityIndicator size={size} color={color} />
        <Text style={styles.message}>{message}</Text>
      </View>
    </View>
  );
};

const LoadingOverlay = ({ visible, message = 'Loading...', backgroundColor = 'rgba(0,0,0,0.5)' }) => {
  if (!visible) return null;

  return (
    <View style={[styles.overlay, { backgroundColor }]}>
      <View style={styles.overlayContent}>
        <ActivityIndicator size="large" color="#fff" />
        <Text style={styles.overlayMessage}>{message}</Text>
      </View>
    </View>
  );
};

const InlineLoader = ({ loading, message, size = 'small', color = '#007bff', style }) => {
  if (!loading) return null;

  return (
    <View style={[styles.inlineContainer, style]}>
      <ActivityIndicator size={size} color={color} />
      {message && <Text style={styles.inlineMessage}>{message}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
  },
  content: {
    alignItems: 'center',
    padding: 20,
  },
  message: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  overlayContent: {
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.8)',
    padding: 20,
    borderRadius: 10,
  },
  overlayMessage: {
    marginTop: 12,
    fontSize: 16,
    color: '#fff',
    textAlign: 'center',
  },
  inlineContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 10,
  },
  inlineMessage: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
  },
});

export { LoadingScreen, LoadingOverlay, InlineLoader };
export default LoadingScreen;