import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Image,
  ActivityIndicator,
  ScrollView,
  Modal,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';

export default function StartDetection() {
  const [selectedMedia, setSelectedMedia] = useState<any>(null);
  const [resultImage, setResultImage] = useState<string | null>(null);
  const [counts, setCounts] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const BACKEND_URL = 'http://192.168.10.5:5000';

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
      setShowDetails(false);
    }
  };

  const sendToBackend = async () => {
    if (!selectedMedia) return;

    if (isDetecting) {
      // Stop detection
      setIsDetecting(false);
      setSelectedMedia(null);
      setResultImage(null);
      setCounts(null);
      setShowDetails(false);
      return;
    }

    setIsDetecting(true);
    setLoading(true);

    const uri = selectedMedia.uri;
    const fileType = uri.endsWith('.mp4') ? 'video' : 'image';
    const endpoint = fileType === 'image' ? '/detect-image' : '/detect-video';
    const apiUrl = `${BACKEND_URL}${endpoint}`;

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

  const handleDownload = async () => {
    if (!resultImage) return;

    try {
      const fileUri = FileSystem.documentDirectory + 'result.jpg';
      await FileSystem.writeAsStringAsync(fileUri, resultImage.split(',')[1], {
        encoding: FileSystem.EncodingType.Base64,
      });
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status === 'granted') {
        await MediaLibrary.saveToLibraryAsync(fileUri);
        alert('Downloaded to gallery!');
      } else {
        alert('Permission denied to save image.');
      }
    } catch (err) {
      console.error(err);
      alert('Failed to download.');
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
        style={[
          styles.button,
          { backgroundColor: isDetecting ? '#ff0033' : '#00ffff', marginTop: 10 },
        ]}
        onPress={sendToBackend}
        disabled={loading}
      >
        <Text style={[styles.buttonText, { color: '#000' }]}>
          {isDetecting ? 'Stop Detection' : loading ? 'Processing...' : 'Start Detection'}
        </Text>
      </TouchableOpacity>

      {loading && <ActivityIndicator size="large" color="#00ffff" style={{ marginTop: 20 }} />}

      {resultImage && (
        <>
          <Text style={[styles.countTitle, { marginTop: 20 }]}>Detection Output:</Text>
          <Image
            source={{ uri: resultImage }}
            style={styles.resultImage}
            resizeMode="contain"
          />

          <View style={styles.buttonRow}>
            <TouchableOpacity style={styles.smallButton} onPress={() => setShowDetails(true)}>
              <Text style={styles.buttonText}>Details</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.smallButton} onPress={handleDownload}>
              <Text style={styles.buttonText}>Download</Text>
            </TouchableOpacity>
          </View>

          {/* Details Modal */}
          <Modal visible={showDetails} animationType="slide" transparent={true}>
            <View style={styles.modalOverlay}>
              <View style={styles.modalContent}>
                <Text style={styles.countTitle}>Object Count:</Text>
                {Object.keys(counts).map((cls) => (
                  <Text key={cls} style={styles.countText}>
                    {cls}: {counts[cls]}
                  </Text>
                ))}
                <TouchableOpacity
                  style={[styles.button, { marginTop: 20 }]}
                  onPress={() => setShowDetails(false)}
                >
                  <Text style={styles.buttonText}>Close</Text>
                </TouchableOpacity>
              </View>
            </View>
          </Modal>
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
    marginTop: 15,
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
  smallButton: {
    backgroundColor: '#1f2937',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 10,
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
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#1f2937',
    padding: 20,
    borderRadius: 15,
    alignItems: 'center',
    width: '80%',
  },
});
