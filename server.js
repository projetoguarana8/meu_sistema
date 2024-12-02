const express = require('express');
const path = require('path');
const app = express();

// Configuração do EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Middleware para servir arquivos estáticos (CSS e JS)
app.use(express.static(path.join(__dirname, 'public')));

// Rota principal: escolha de preço
app.get('/', (req, res) => {
    res.render('index'); // Renderiza index.ejs
});

// Rota: escolha de cobertura
app.get('/cobertura', (req, res) => {
    res.render('escolha_cobertura'); // Renderiza escolha_cobertura.ejs
});

// Rota: pagamento
app.get('/pagamento', (req, res) => {
    res.render('pagamento'); // Renderiza pagamento.ejs
});

// Inicia o servidor
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
