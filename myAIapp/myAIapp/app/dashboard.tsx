// dashboard.tsx
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';

export default function Dashboard() {
  const router = useRouter();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Traffic Counter</Text>

      <TouchableOpacity style={styles.button} onPress={() => router.push('/StartDetection')}>
        <Text style={styles.buttonText}>Start Detection</Text>
      </TouchableOpacity>

      {/* Settings button - you can add more features later */}
      <TouchableOpacity style={styles.button} onPress={() => router.push('/Settings')}>
        <Text style={styles.buttonText}>Settings</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0f1a',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    color: '#00ffff',
    marginBottom: 40,
    fontWeight: 'bold',
  },
  button: {
    width: '100%',
    backgroundColor: '#1f2937',
    padding: 20,
    borderRadius: 20,
    marginBottom: 20,
    alignItems: 'center',
    shadowColor: '#00ffff',
    shadowOffset: { width: -4, height: 6 },
    shadowOpacity: 0.6,
    shadowRadius: 8,
    elevation: 10,
    borderWidth: 1,
    borderColor: '#00ffff',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
    textShadowColor: '#000000',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 2,
  },
});
