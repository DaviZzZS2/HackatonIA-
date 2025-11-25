import parselmouth
from parselmouth.praat import call
import librosa
import numpy as np

from pydub import AudioSegment
import os
import tempfile

def convert_to_wav(input_path):
    # Garante que a extensão final será WAV
    if input_path.lower().endswith(".wav"):
        return input_path  # já é WAV, então use direto

    # cria arquivo temporário WAV
    temp_wav = tempfile.mktemp(suffix=".wav")

    # carrega o áudio independente do formato
    audio = AudioSegment.from_file(input_path)

    # exporta para WAV (16-bit PCM)
    audio.export(temp_wav, format="wav")

    return temp_wav

def extract_voice_features(filepath):

    wav_path = convert_to_wav(filepath)
    # -----------------------------
    # 1. Load audio
    # -----------------------------
    y, sr = librosa.load(wav_path, sr=44100)
    
    sound = parselmouth.Sound(wav_path)
    

    # -----------------------------
    # 2. Fundamental Frequency (F0)
    # -----------------------------
    pitch = call(sound, "To Pitch", 0.0, 75, 600)
    f0_values = pitch.selected_array['frequency']
    f0_values = f0_values[f0_values > 0]  # remove zeros

    f0_mean = np.mean(f0_values) if len(f0_values) > 0 else 0
    f0_std  = np.std(f0_values) if len(f0_values) > 0 else 0
    f0_min  = np.min(f0_values) if len(f0_values) > 0 else 0
    f0_max  = np.max(f0_values) if len(f0_values) > 0 else 0

    # -----------------------------
    # 3. JITTER / SHIMMER (requires PointProcess)
    # -----------------------------
    point_process = call(sound, "To PointProcess (periodic, cc)", 75, 600)
    print(point_process)
    # Jitter
    jitter_local = call(point_process, 
                    "Get jitter (local)", 
                    0, 0,               # start, end (0 = toda duração)
                    0.0001,             # shortest period = 0.1 ms
                    0.02,               # longest period = 20 ms
                    1.3)                # maximum period factor



    # Shimmer
    shimmer_local = call([sound, point_process],
                     "Get shimmer (local)",
                     0, 0,          # start, end
                     0.0001,        # shortest period
                     0.02,          # longest period
                     1.3,           # max period factor
                     1.6)           # max amplitude factor
    
    # -----------------------------
    # 5. HNR (Harmonic-to-Noise Ratio)
    # -----------------------------
    hnr = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
    hnr_mean = call(hnr, "Get mean", 0, 0)

    # -----------------------------
    # 6. Formants (F1, F2, F3, F4)
    # -----------------------------
    formants = call(sound, "To Formant (burg)", 0.0, 5, 5000, 0.025, 50)

    def get_formant(formant_id):
        return call(formants, "Get mean", formant_id, 0, 0, "Hertz")

    F1 = get_formant(1)
    F2 = get_formant(2)
    F3 = get_formant(3)
    F4 = get_formant(4)

    # -----------------------------
    # 7. MFCCs (librosa)
    # -----------------------------
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)

    # -----------------------------
    # 8. Zero Crossing Rate
    # -----------------------------
    zcr = librosa.feature.zero_crossing_rate(y)
    zcr_mean = float(np.mean(zcr))

    # -----------------------------
    # 9. Energy (RMS)
    # -----------------------------
    rms = librosa.feature.rms(y=y)
    rms_mean = float(np.mean(rms))

    # -----------------------------
    # 10. Duration
    # -----------------------------
    duration = librosa.get_duration(y=y, sr=sr)

    # -----------------------------
    # RETURN ALL FEATURES
    # -----------------------------
    return {
        "f0_mean": float(f0_mean),
        "f0_std": float(f0_std),
        "f0_min": float(f0_min),
        "f0_max": float(f0_max),

        "jitter_local": float(jitter_local),
        "shimmer_local": float(shimmer_local),
        "hnr_mean": float(hnr_mean),

        "F1_mean": float(F1),
        "F2_mean": float(F2),
        "F3_mean": float(F3),
        "F4_mean": float(F4),

        "mfcc_means": mfcc_mean.tolist(),

        "zcr_mean": zcr_mean,
        "rms_mean": rms_mean,
        "duration_seconds": duration
    }


# -----------------------------
# EXAMPLE USAGE
# -----------------------------
if __name__ == "__main__":
    file = "C:\HackatonIA++\ExtracaoAtributosVoz\\teste.waptt.opus"
    feats = extract_voice_features(file)
    for k, v in feats.items():
        print(k, ":", v)
