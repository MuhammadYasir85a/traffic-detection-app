import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ScrollView } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export default function StartDetection() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);

  const [filters, setFilters] = useState<{
    Car: boolean;
    Truck: boolean;
    Motorbike: boolean;
  }>({
    Car: true,
    Truck: true,
    Motorbike: true,
  });

  const toggleFilter = (vehicle: 'Car' | 'Truck' | 'Motorbike') => {
    setFilters((prev) => ({
      ...prev,
      [vehicle]: !prev[vehicle],
    }));
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 1,
    });

    if (!result.canceled && result.assets.length > 0) {
      setSelectedImage(result.assets[0].uri);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      <View style={styles.card}>
        <Text style={styles.title}>Start Detection</Text>

        <TouchableOpacity style={styles.button} onPress={pickImage}>
          <Text style={styles.buttonText}>📷 Upload Image</Text>
        </TouchableOpacity>

        {selectedImage && (
          <Image
            source={{ uri: selectedImage }}
            style={styles.imagePreview}
            resizeMode="contain"
          />
        )}

        <View style={styles.filterContainer}>
          {(['Car', 'Truck', 'Motorbike'] as const).map((vehicle) => (
            <TouchableOpacity
              key={vehicle}
              style={[
                styles.filterButton,
                filters[vehicle] && styles.activeFilter,
              ]}
              onPress={() => toggleFilter(vehicle)}
            >
              <Text
                style={[
                  styles.filterText,
                  filters[vehicle] && styles.activeFilterText,
                ]}
              >
                {vehicle}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <TouchableOpacity
          style={[styles.detectButton, isDetecting && styles.detecting]}
          onPress={() => setIsDetecting(!isDetecting)}
        >
          <Text style={styles.detectButtonText}>
            {isDetecting ? '⛔ Stop Detection' : '▶️ Start Detection'}
          </Text>
        </TouchableOpacity>

        <Text style={styles.countText}>
          🚗 Car: {filters.Car ? Math.floor(Math.random() * 10) : 0} | 🚛 Truck: {filters.Truck ? Math.floor(Math.random() * 5) : 0} | 🏍️ Motorbike: {filters.Motorbike ? Math.floor(Math.random() * 7) : 0}
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollContainer: {
    flexGrow: 1,
    backgroundColor: '#0e1220',
    paddingVertical: 30,
    alignItems: 'center',
    justifyContent: 'center',
  },
  card: {
    width: '92%',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    borderRadius: 20,
    padding: 20,
    borderColor: '#00ffe0',
    borderWidth: 1,
    shadowColor: '#00ffe0',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 8 },
    shadowRadius: 20,
    backdropFilter: 'blur(10px)',
  },
  title: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#00ffe0',
    marginBottom: 20,
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#131c31',
    paddingVertical: 12,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#00ffe0',
    alignItems: 'center',
    marginBottom: 15,
    elevation: 5,
    shadowColor: '#00ffff',
    shadowOpacity: 0.3,
    shadowOffset: { width: 0, height: 3 },
    shadowRadius: 8,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  imagePreview: {
    width: '100%',
    height: 200,
    marginVertical: 15,
    borderRadius: 15,
    borderWidth: 1,
    borderColor: '#00ffe0',
  },
  filterContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-evenly',
    marginTop: 10,
  },
  filterButton: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 12,
    margin: 5,
    borderWidth: 1,
    borderColor: '#00ffe0',
    backgroundColor: '#1c2434',
  },
  activeFilter: {
    backgroundColor: '#00ffe0',
  },
  filterText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  activeFilterText: {
    color: '#000000',
  },
  detectButton: {
    marginTop: 25,
    backgroundColor: '#131c31',
    paddingVertical: 14,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#00ffe0',
    elevation: 6,
    shadowColor: '#00ffe0',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.4,
    shadowRadius: 10,
  },
  detecting: {
    backgroundColor: '#00ffe0',
  },
  detectButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  countText: {
    color: '#ffffff',
    fontSize: 15,
    marginTop: 25,
    textAlign: 'center',
  },
});
