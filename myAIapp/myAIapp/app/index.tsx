// app/index.tsx
import { useEffect } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { router } from 'expo-router';

export default function SplashScreen() {
  useEffect(() => {
    const timer = setTimeout(() => {
      router.replace('/dashboard');
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}> Traffic Counter </Text>
      <ActivityIndicator size="large" color="#00FFFF" style={styles.spinner} />
      <Text style={styles.loading}>Loading...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1a',
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 32,
    color: '#00FFFF',
    fontWeight: 'bold',
    marginBottom: 20,
  },
  spinner: {
    marginTop: 20,
  },
  loading: {
    color: '#ccc',
    marginTop: 10,
    fontSize: 16,
  },
});
