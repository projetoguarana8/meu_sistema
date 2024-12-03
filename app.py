import mercadopago
from flask import Flask, render_template, request, redirect, url_for, jsonify
import os

app = Flask(__name__)

# Configurar o Mercado Pago SDK com o seu Access Token
sdk = mercadopago.SDK("APP_USR-8273006733257385-112812-1c84938b60e15305a58b0da20ec2708e-294303894")  # Substitua pela sua chave de acesso

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
                "unit_price": total
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

@app.route('/pagamento_dinheiro', methods=['POST'])
def pagamento_dinheiro():
    valor_pago = float(request.form['valor_pago'])
    preco = float(request.form['preco'])
    quantidade = int(request.form['quantidade'])

    # Calcula o total
    total = preco * quantidade

    # Calcula o troco
    troco = valor_pago - total

    if troco < 0:
        return f"Valor pago insuficiente. Faltam R${-troco:.2f}"

    # Redireciona para a página de troco com os valores calculados
    return render_template('troco.html', valor_pago=valor_pago, total=total, troco=troco)

# Webhook para processar notificações do Mercado Pago
@app.route('/webhook', methods=['POST'])
def webhook():
    # Verifica se a assinatura secreta está presente no cabeçalho
    secret = request.headers.get('X-Hook-Secret')
    if secret != os.getenv('bb547928cc2e1b0ce376d08618a8cd8fad16ed0debba4a316e349710d06e848'):  # Substitua por sua chave secreta
        return "Unauthorized", 401

    # Captura os dados enviados pelo webhook
    data = request.json
    if not data:
        return "Bad Request", 400

    # Processa a notificação
    action = data.get('action')
    payment_id = data.get('data', {}).get('id')

    if action == "payment.updated":
        # Insira a lógica de tratamento para pagamentos atualizados aqui
        print(f"Pagamento atualizado! ID: {payment_id}")
    
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Porta configurada pelo Render ou padrão 5000
    app.run(host='0.0.0.0', port=port)
