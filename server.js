const express = require('express');
const path = require('path');
const mercadopago = require('mercadopago');
const app = express();

// Configuração do Mercado Pago (adicione sua chave de acesso)
mercadopago.configure({
    access_token: 'TEST-8273006733257385-112812-1b4d12c15bed39ef93f55c43e661770b-294303894' // Substitua pelo seu token de acesso do Mercado Pago
});

// Configuração do EJS
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Middleware para servir arquivos estáticos
app.use(express.static(path.join(__dirname, 'public')));

// Middleware para interpretar JSON no corpo das requisições
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rota principal: escolha de preço
app.get('/', (req, res) => {
    res.render('index');
});

// Rota para receber dados do preço
app.post('/escolha-preco', (req, res) => {
    const { preco } = req.body;
    if (!preco) {
        return res.status(400).json({ error: 'Preço não enviado.' });
    }
    console.log(`Preço recebido: R$${preco}`);
    res.status(200).json({ message: `Preço R$${preco} salvo com sucesso.` });
});

// Rota: escolha de cobertura
app.post('/escolha-cobertura', (req, res) => {
    const { cobertura } = req.body;
    if (!cobertura) {
        return res.status(400).json({ error: 'Cobertura não enviada.' });
    }
    console.log(`Cobertura recebida: ${cobertura}`);
    res.status(200).json({ message: `Cobertura ${cobertura} salva com sucesso.` });
});

// Rota: pagamento
app.post('/pagamento', async (req, res) => {
    const { preco, cobertura } = req.body;

    if (!preco || !cobertura) {
        return res.status(400).json({ error: 'Dados incompletos para o pagamento.' });
    }

    console.log(`Processando pagamento de R$${preco} com cobertura ${cobertura}`);

    // Criação do item de pagamento
    const item = {
        title: `Guaraná com cobertura de ${cobertura}`,
        quantity: 1,
        currency_id: 'BRL',
        unit_price: parseFloat(preco)
    };

    try {
        // Criação da preferência de pagamento
        const preference = await mercadopago.preferences.create({
            items: [item],
            back_urls: {
                success: 'http://localhost:3000/sucesso',
                failure: 'http://localhost:3000/erro',
                pending: 'http://localhost:3000/pendente'
            },
            auto_return: 'approved'
        });

        // Enviar o link de pagamento para o cliente
        res.status(200).json({ url: preference.body.init_point });
    } catch (error) {
        console.error('Erro ao criar pagamento:', error);
        res.status(500).json({ error: 'Erro ao processar pagamento.' });
    }
});

// Página de sucesso
app.get('/sucesso', (req, res) => {
    res.send('<h1>Pagamento realizado com sucesso!</h1>');
});

// Página de erro
app.get('/erro', (req, res) => {
    res.send('<h1>O pagamento falhou. Tente novamente.</h1>');
});

// Página de pagamento pendente
app.get('/pendente', (req, res) => {
    res.send('<h1>Seu pagamento está pendente. Aguarde a aprovação.</h1>');
});

// Inicia o servidor
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
