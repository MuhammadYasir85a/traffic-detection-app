// app/Settings.tsx
import React from 'react';
import { View, Text, Switch, StyleSheet, ScrollView } from 'react-native';
import { useState } from 'react';
import { Ionicons } from '@expo/vector-icons';

export default function Settings() {
  const [autoStart, setAutoStart] = useState(false);
  const [confidence, setConfidence] = useState(0.5);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.header}>Settings</Text>

    

      <View style={styles.card}>
        <Ionicons name="information-circle" size={24} color="#4ecca3" style={styles.icon} />
        <Text style={styles.label}>App Version</Text>
        <Text style={styles.value}>1.0.0</Text>
      </View>

      <View style={styles.card}>
        <Ionicons name="mail" size={24} color="#4ecca3" style={styles.icon} />
        <Text style={styles.label}>Developer Contact</Text>
        <Text style={styles.value}>yasir@trafficai.com</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    backgroundColor: '#121212',
    flexGrow: 1,
  },
  header: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 20,
  },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1f1f1f',
    padding: 15,
    borderRadius: 12,
    marginBottom: 15,
    shadowColor: '#4ecca3',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 5,
  },
  icon: {
    marginRight: 12,
  },
  label: {
    flex: 1,
    color: '#ffffff',
    fontSize: 16,
  },
  value: {
    color: '#aaaaaa',
    fontSize: 14,
  },
});
