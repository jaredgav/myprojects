import numpy as np
import librosa
import cv2

def image_to_music(image_path, audio_file):
    # Load the image
    img = cv2.imread(image_path, 0)

    # Resize the image to a fixed size
    img = cv2.resize(img, (224, 224))

    # Compute the mel spectrogram of the image
    mel_spec = librosa.feature.melspectrogram(img)

    # Load the audio file
    y, sr = librosa.load(audio_file)

    # Compute the chromagram of the audio file
    chroma = librosa.feature.chroma_stft(y, sr)

    # Compute the cosine similarity between the mel spectrogram and chromagram
    cos_sim = np.dot(mel_spec.T, chroma) / (np.linalg.norm(mel_spec) * np.linalg.norm(chroma))

    # Find the index of the most similar frame
    idx = np.argmax(cos_sim)

    # Compute the time of the most similar frame
    t = librosa.frames_to_time(idx)

    # Return the time in seconds
    return t
 
if __name__ == "__main__":
    image_to_music(r"C:\Users\jgavi\Pictures\nick.jpg", r"C:\Users\jgavi\Downloads\Looking B(L)ack.m4a")
