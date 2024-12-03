import mercadopago
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Configurar o Mercado Pago SDK
sdk = mercadopago.SDK("APP_USR-8273006733257385-112812-1c84938b60e15305a58b0da20ec2708e-294303894")  # Substitua pelo seu Access Token

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Porta configurada pelo Render ou padrão 5000
    app.run(host='0.0.0.0', port=port)
