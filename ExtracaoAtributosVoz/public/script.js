// Variáveis Globais
let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let timerInterval;
let startTime;

// Elementos DOM
const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const submitBtn = document.getElementById("submitBtn");
const micCircle = document.getElementById("mic-circle");
const timerEl = document.getElementById("timer");
const statusTextEl = document.getElementById("status-text");
const recordTextEl = document.getElementById("record-text");
const resultadoEl = document.getElementById("resultado");

// --- Funções de Timer ---

function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    const elapsed = Date.now() - startTime;
    const totalSeconds = Math.floor(elapsed / 1000);
    const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
    const seconds = String(totalSeconds % 60).padStart(2, '0');
    timerEl.innerText = `${minutes}:${seconds}`;
}

function stopTimer() {
    clearInterval(timerInterval);
    timerEl.innerText = "00:00";
}

// --- Event Listeners e Lógica de Gravação ---

recordBtn.onclick = async () => {
    if (isRecording) return; 

    try {
        // Solicita acesso ao microfone
        let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        audioChunks = [];

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);

        mediaRecorder.onstop = async () => {
            isRecording = false;
            stopTimer();
            statusTextEl.innerText = "Pronto para enviar";
            micCircle.classList.remove('recording');

            // Habilita botão de Envio e desabilita o Parar
            submitBtn.disabled = false;
            stopBtn.disabled = true;
            
            // Alterna a exibição: Oculta Parar, mostra Iniciar
            recordBtn.style.display = 'block';
            stopBtn.style.display = 'none';

            // Para todas as faixas do stream para liberar o microfone
            stream.getTracks().forEach(track => track.stop());
        };

        // Inicia a gravação
        mediaRecorder.start();
        isRecording = true;
        startTimer();
        statusTextEl.innerText = "Gravando...";
        micCircle.classList.add('recording');

        // Alterna botões (COM A CORREÇÃO DE HABILITAÇÃO)
        recordBtn.style.display = 'none';
        stopBtn.style.display = 'block';
        stopBtn.disabled = false; // 👈 CORREÇÃO PRINCIPAL
        
        submitBtn.disabled = true; // Desabilita Enviar enquanto grava

    } catch (err) {
        statusTextEl.innerText = "Erro ao acessar o microfone. Verifique as permissões.";
        console.error("Erro ao acessar o microfone: ", err);
    }
};

stopBtn.onclick = () => {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        stopBtn.disabled = true; // Desabilita enquanto processa a parada
        statusTextEl.innerText = "Processando...";
    }
};

submitBtn.onclick = async () => {
    if (audioChunks.length === 0 || isRecording) return;
    
    statusTextEl.innerText = "Enviando...";
    submitBtn.disabled = true;

    try {
        const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
        const file = new File([audioBlob], "gravacao.wav", { type: "audio/wav" });

        const formData = new FormData();
        formData.append("audio", file);
        
        const cpf = document.getElementById('cpf').value;
        formData.append("cpf", cpf); 

        const resp = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        if (!resp.ok) {
            throw new Error(`Erro HTTP: ${resp.status}`);
        }

        const data = await resp.json();
        resultadoEl.innerText = data.resultado;
        statusTextEl.innerText = "Gravação enviada com sucesso!";
        
    } catch (error) {
        resultadoEl.innerText = `Erro no envio: ${error.message}`;
        statusTextEl.innerText = "Falha no envio da gravação.";
    } finally {
        // Limpa e redefine para o estado inicial
        recordTextEl.innerText = "Iniciar Gravação";
        submitBtn.disabled = true; 
        audioChunks = []; 
    }
};

// --- Configuração Inicial ---
document.addEventListener('DOMContentLoaded', () => {
    // Esconde o botão de Parar no início
    stopBtn.style.display = 'none';
    submitBtn.disabled = true;
});