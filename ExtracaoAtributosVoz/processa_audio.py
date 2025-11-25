import sys
import json
import warnings
warnings.filterwarnings("ignore")
from mangabaTeste import extract_voice_features, agente_voz, perfil_falante


sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


if __name__ == "__main__":
    audio_path = sys.argv[1]

    features = extract_voice_features(audio_path)

    prompt = f"""
        Voce e um especialista em analise de voz e deteccao de sinais precoces de Parkinson.

        === PERFIL DO PACIENTE ===
        Idade: {perfil_falante['idade']}
        Sexo: {perfil_falante['sexo']}
        Tabagista: {perfil_falante['tabagista']}
        Condicoes medicas: {perfil_falante['condicoes_medicas']}

        === ATRIBUTOS ACUSTICOS ===
        A seguir estao os atributos acusticos extraidos da voz. Formate e apresente de forma clara:

        {json.dumps(features, indent=4)}

        === INSTRUCOES DE FORMATO ===
        - Retorne um bloco organizado contendo:
            1. Um resumo simples dos atributos acusticos.
            2. Um bloco formatado com cada feature e seu valor.
        - Linguagem simples, sem acentos.
        - Depois disso, retorne a conclusao final de maneira resumida baseada em comparação com numeros de pessoas com idade,gênero, e perfil parecidos

        IMPORTANTE:
        A ultima linha deve conter SOMENTE a conclusao final, sem justificativa adicional.
        """

    

    try:
        resposta = agente_voz.execute_task(prompt)
        print(resposta)
    except Exception as e:
        import sys
        print(f"[LOG] Agente falhou internamente: {e}", file=sys.stderr)
        print("Erro ao processar o áudio. Tente novamente.")  

