import mercadopago
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import hmac
import hashlib

app = Flask(__name__)

# Configurar o Mercado Pago SDK
sdk = mercadopago.SDK("APP_USR-8273006733257385-112812-1c84938b60e15305a58b0da20ec2708e-294303894")  # Substitua pelo seu Access Token

# Chave secreta do webhook (substitua com a sua chave secreta)
WEBHOOK_SECRET = "bb547928cc2e1b0ce376d08618a8cd8fad16ed0debba4a316e349710d06e848c"

@app.route('/')
def escolha_preco():
    return render_template('index.html')

@app.route('/cobertura', methods=['POST'])
def escolha_cobertura():
    preco = request.form.get('preco')
    quantidade = int(request.form.get('quantidade'))  # Captura a quantidade
    return render_template('cobertura.html', preco=preco, quantidade=quantidade)

@app.route('/pagamento', methods=['POST'])
def pagamento():
    preco = request.form.get('preco')
    cobertura = request.form.get('cobertura')
    quantidade = int(request.form.get('quantidade'))  # Obtém a quantidade de Guaraná

    # Calcula o preço total
    total = float(preco) * quantidade

    # Criar preferência de pagamento
    preference_data = {
        "items": [
            {
                "title": f"Guaraná com {cobertura}",
                "quantity": quantidade,
                "currency_id": "BRL",
                "unit_price": float(preco)
            }
        ],
        "back_urls": {
            "success": url_for('sucesso', _external=True),
            "failure": url_for('falha', _external=True),
            "pending": url_for('pendente', _external=True)
        },
        "auto_return": "approved"
    }

    preference = sdk.preference().create(preference_data)
    init_point = preference["response"]["init_point"]

    return redirect(init_point)

@app.route('/sucesso')
def sucesso():
    return "Pagamento realizado com sucesso!"

@app.route('/falha')
def falha():
    return "O pagamento falhou. Tente novamente."

@app.route('/pendente')
def pendente():
    return "O pagamento está pendente. Aguarde a confirmação."

# Função para verificar a assinatura secreta
def verificar_assinatura(request):
    signature = request.headers.get('X-Mercadopago-Signature')
    payload = request.data  # Dados do corpo da requisição (payload)

    # Calculando o hash HMAC-SHA256 com a chave secreta
    calculated_signature = hmac.new(
        WEBHOOK_SECRET.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    # Comparando a assinatura calculada com a que veio no cabeçalho
    if not hmac.compare_digest(signature, calculated_signature):
        raise ValueError("Assinatura inválida")

# Rota para receber as notificações do Mercado Pago (Webhook)
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Verifica a assinatura para garantir que a requisição é do Mercado Pago
        verificar_assinatura(request)

        # O Mercado Pago enviará um payload com os dados do pagamento
        data = request.json

        # Verifique se a notificação foi recebida corretamente
        print(f"Notificação recebida: {data}")

        # Aqui você pode verificar o status do pagamento
        payment_id = data.get("data", {}).get("id")

        # Recupere a informação do pagamento através da API do Mercado Pago
        payment_info = sdk.payment().get(payment_id)

        status = payment_info["response"]["status"]
        
        # Verifique o status do pagamento e tome as ações necessárias
        if status == "approved":
            print("Pagamento aprovado")
            # Aqui você pode atualizar o status do pagamento no banco de dados ou tomar outras ações
        elif status == "pending":
            print("Pagamento pendente")
            # Aqui você pode marcar como "pendente"
        elif status == "rejected":
            print("Pagamento rejeitado")
            # Aqui você pode marcar como "rejeitado"
        
        return '', 200  # Responde que recebeu corretamente a notificação
    except ValueError as e:
        print(f"Erro de validação: {e}")
        return jsonify({"error": "Assinatura inválida"}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Porta configurada pelo Render ou padrão 5000
    app.run(host='0.0.0.0', port=port)
