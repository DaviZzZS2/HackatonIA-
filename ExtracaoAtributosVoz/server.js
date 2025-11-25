const express = require("express");
const multer = require("multer");
const { spawn } = require("child_process");
const path = require("path");

const app = express();
// Configura o multer para armazenar em 'uploads/'
const upload = multer({ dest: "uploads/" }); 

// Serve arquivos estáticos da pasta 'public'
app.use(express.static(path.join(__dirname, "public"))); 
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views")); // Define a pasta de views

app.get("/", (req, res) => {
    res.render("index"); // Renderiza o index.ejs
});

app.post("/upload", upload.single("audio"), (req, res) => {
    // O CPF foi enviado no FormData, ele estará em req.body
    const cpfPaciente = req.body.cpf; 
    const audioPath = req.file.path; // Caminho temporário do áudio

    console.log(`Recebido: CPF ${cpfPaciente}, Arquivo: ${audioPath}`);

    // Cria um processo Python, passando o caminho do áudio e o CPF
    const python = spawn("python", ["processa_audio.py", audioPath, cpfPaciente]);

    let result = "";
    let error = "";

    python.stdout.on("data", data => {
        result += data.toString();
    });
    
    python.stderr.on("data", data => {
        // Captura erros do script Python
        error += data.toString();
    });

    python.on("close", (code) => {
        if (code !== 0) {
            console.error(`Script Python falhou com código ${code}`);
            console.error(`Erro Python: ${error}`);
            // Retorna o erro em vez do resultado vazio
            return res.status(500).json({ 
                resultado: `Erro na análise de áudio (código ${code}):\n${error}` 
            });
        }
        // Retorna o resultado do stdout do script Python
        res.json({ resultado: result });
    });
    
    python.on("error", (err) => {
        console.error("Falha ao iniciar o processo Python:", err);
        res.status(500).json({ 
            resultado: `Erro no servidor: Falha ao executar o script de análise. (${err.message})` 
        });
    });
});

app.listen(4000, () => console.log("Servidor rodando em http://localhost:4000"));