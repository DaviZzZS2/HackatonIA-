import parselmouth
from parselmouth.praat import call
import librosa
import numpy as np
import sys

from pydub import AudioSegment
import tempfile
from dotenv import load_dotenv
import os

sys.stderr = open(os.devnull, 'w')


# Carrega automaticamente as variáveis do arquivo .env
load_dotenv("C:\HackatonIA++\ExtracaoAtributosVoz\mangaba.env")

google_key = os.getenv("GOOGLE_API_KEY")



# ================================
# 🔹 MANGABA IA
# ================================
from mangaba import Agent

perfil_falante = {
    "idade": "21 Anos",
    "sexo": "Masculino",
    "tabagista": "Não",
    "condicoes_medicas": ["Nenhuma conhecida"]
}

agente_voz = Agent(
    role="Especialista em Análise de Voz",
    goal="Interpretar atributos acústicos e gerar análise baseada em bancos de dados.",
    backstory=(
        "Você é um especialista em processamento de sinais, fonética e análise clínica. "
        "Seu paciente atual tem o seguinte perfil: " + str(perfil_falante) + ". "
        "Use essas informações para calibrar sua análise acústica, pois "
        "elas influenciam métricas como F0 (frequência fundamental)."
    ),
    llm="models/gemini-pro-latest",  # ou outro modelo do Google Gemini
    verbose=False
)


def convert_to_wav(input_path):
    if input_path.lower().endswith(".wav"):
        return input_path

    temp_wav = tempfile.mktemp(suffix=".wav")
    audio = AudioSegment.from_file(input_path)
    audio.export(temp_wav, format="wav")

    return temp_wav


def extract_voice_features(filepath):

    wav_path = convert_to_wav(filepath)

    y, sr = librosa.load(wav_path, sr=44100)
    sound = parselmouth.Sound(wav_path)

    pitch = call(sound, "To Pitch", 0.0, 75, 600)
    f0_values = pitch.selected_array['frequency']
    f0_values = f0_values[f0_values > 0]

    f0_mean = np.mean(f0_values) if len(f0_values) > 0 else 0
    f0_std  = np.std(f0_values) if len(f0_values) > 0 else 0
    f0_min  = np.min(f0_values) if len(f0_values) > 0 else 0
    f0_max  = np.max(f0_values) if len(f0_values) > 0 else 0

    point_process = call(sound, "To PointProcess (periodic, cc)", 75, 600)

    jitter_local = call(point_process, 
                        "Get jitter (local)",
                        0, 0,
                        0.0001,
                        0.02,
                        1.3)

    shimmer_local = call([sound, point_process],
                         "Get shimmer (local)",
                         0, 0,
                         0.0001,
                         0.02,
                         1.3,
                         1.6)

    hnr = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
    hnr_mean = call(hnr, "Get mean", 0, 0)

    formants = call(sound, "To Formant (burg)", 0.0, 5, 5000, 0.025, 50)
    def get_formant(id): return call(formants, "Get mean", id, 0, 0, "Hertz")

    F1 = get_formant(1)
    F2 = get_formant(2)
    F3 = get_formant(3)
    F4 = get_formant(4)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean = np.mean(mfcc, axis=1)

    zcr_mean = float(np.mean(librosa.feature.zero_crossing_rate(y)))
    rms_mean = float(np.mean(librosa.feature.rms(y=y)))
    duration = librosa.get_duration(y=y, sr=sr)

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


# ================================
# 🔹 AGORA: ENVIAR OS DADOS AO AGENTE MANGABA
# ================================
if __name__ == "__main__":
    file = "C:\HackatonIA++\ExtracaoAtributosVoz\\teste.waptt.opus"

    features = extract_voice_features(file)

    # 📤 Envia para o agente de IA em vez de printar
    import json

    contexto_adicional = (
    "A faixa etária do falante é 20 anos. Ele é do sexo Feminino e relata ser "
    "não fumante. A instrução específica é: 'Avalie a estabilidade vocal "
    "comparando com padrões de não-fumantes da mesma faixa etária e sexo.'"
    )


    prompt = (
        "Você é um agente especializado em análise de voz.\n"
        + contexto_adicional + # Adicionando o contexto aqui
        "\n\nAqui estão os atributos extraídos:\n\n"
        + json.dumps(features, indent=4) +
        "\n\nPor favor gere uma análise detalhada."
    )

   
    resposta = agente_voz.execute_task(prompt)



    print("\n📌 **ANÁLISE DO AGENTE:**\n")
    print(resposta)
