//StartDetection.tsx code
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image, ActivityIndicator, ScrollView } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';

export default function StartDetection() {
  const [selectedMedia, setSelectedMedia] = useState<any>(null);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [counts, setCounts] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const BACKEND_URL = "http://192.168.10.7:5000"; // Replace YOUR_IP with your local IP (e.g., 192.168.1.100)

  const pickMedia = async (type: 'image' | 'video') => {
    let result;
    if (type === 'image') {
      result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        quality: 1,
        base64: false,
      });
    } else {
      result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Videos,
      });
    }

    if (!result.canceled) {
      setSelectedMedia(result.assets[0]);
      setResultImage(null);
      setCounts(null);
    }
  };

  const sendToBackend = async () => {
    if (!selectedMedia) return;

    setLoading(true);
    const uri = selectedMedia.uri;
    const fileType = uri.endsWith('.mp4') ? 'video' : 'image';
    const endpoint = fileType === 'image' ? '/detect-image' : '/detect-video';
    const apiUrl = `${BACKEND_URL}${endpoint}`;

    const fileInfo = await FileSystem.getInfoAsync(uri);
    const fileData = {
      uri,
      type: fileType === 'image' ? 'image/jpeg' : 'video/mp4',
      name: fileType === 'image' ? 'image.jpg' : 'video.mp4',
    };

    const formData = new FormData();
    formData.append('media', fileData as any);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        body: formData,
      });

      const json = await response.json();
      if (json.processed_image) {
        setResultImage(`data:image/jpeg;base64,${json.processed_image}`);
        setCounts(json.count_by_type);
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Start Detection</Text>

      <View style={styles.buttonRow}>
        <TouchableOpacity style={styles.button} onPress={() => pickMedia('image')}>
          <Text style={styles.buttonText}>Upload Image</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.button} onPress={() => pickMedia('video')}>
          <Text style={styles.buttonText}>Upload Video</Text>
        </TouchableOpacity>
      </View>

      {selectedMedia && (
        <Text style={styles.fileName}>
          Selected: {selectedMedia.name || selectedMedia.uri.split('/').pop()}
        </Text>
      )}

      <TouchableOpacity
        style={[styles.button, { backgroundColor: '#00ffff' }]}
        onPress={sendToBackend}
        disabled={loading}
      >
        <Text style={[styles.buttonText, { color: '#000' }]}>
          {loading ? 'Processing...' : 'Start Detection'}
        </Text>
      </TouchableOpacity>

      {loading && <ActivityIndicator size="large" color="#00ffff" style={{ marginTop: 20 }} />}

      {resultImage && (
        <>
          <Image source={{ uri: resultImage }} style={styles.resultImage} resizeMode="contain" />
          <View style={styles.countBox}>
            <Text style={styles.countTitle}>Object Count:</Text>
            {Object.keys(counts).map((cls) => (
              <Text key={cls} style={styles.countText}>
                {cls}: {counts[cls]}
              </Text>
            ))}
          </View>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: '#0a0f1a',
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 26,
    color: '#00ffff',
    marginVertical: 20,
    fontWeight: 'bold',
  },
  buttonRow: {
    flexDirection: 'row',
    marginBottom: 20,
    gap: 10,
  },
  button: {
    backgroundColor: '#1f2937',
    padding: 15,
    borderRadius: 15,
    borderColor: '#00ffff',
    borderWidth: 1,
    marginHorizontal: 5,
  },
  buttonText: {
    color: '#ffffff',
    fontWeight: '600',
    fontSize: 16,
  },
  fileName: {
    color: '#ffffff',
    marginVertical: 10,
    textAlign: 'center',
  },
  resultImage: {
    width: '100%',
    height: 300,
    marginTop: 20,
    borderRadius: 10,
    borderColor: '#00ffff',
    borderWidth: 1,
  },
  countBox: {
    marginTop: 20,
    backgroundColor: '#1f2937',
    padding: 15,
    borderRadius: 10,
    width: '100%',
    alignItems: 'center',
  },
  countTitle: {
    color: '#00ffff',
    fontWeight: 'bold',
    fontSize: 18,
    marginBottom: 10,
  },
  countText: {
    color: '#ffffff',
    fontSize: 16,
  },
});
