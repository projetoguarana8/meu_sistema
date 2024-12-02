from flask import Flask, render_template, request, redirect, url_for # type: ignore
import mercadopago # type: ignore

app = Flask(__name__)

# Configuração do Mercado Pago
mp = mercadopago.SDK("SEU_ACCESS_TOKEN_AQUI")  # Substitua pelo seu token do Mercado Pago

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pagamento', methods=['POST'])
def pagamento():
    preco = request.form.get('preco')

    if not preco:
        return "Erro: Preço não selecionado.", 400

    # Configurando o item para pagamento
    preference_data = {
        "items": [
            {
                "title": f"Guaraná - R${preco}",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(preco)
            }
        ],
        "back_urls": {
            "success": url_for('sucesso', _external=True),
            "failure": url_for('erro', _external=True),
            "pending": url_for('pendente', _external=True)
        },
        "auto_return": "approved"
    }

    # Criando preferência de pagamento
    preference_response = mp.preference().create(preference_data)
    payment_link = preference_response["response"]["init_point"]

    return redirect(payment_link)

@app.route('/sucesso')
def sucesso():
    return "<h1>Pagamento realizado com sucesso!</h1>"

@app.route('/erro')
def erro():
    return "<h1>Pagamento falhou. Tente novamente.</h1>"

@app.route('/pendente')
def pendente():
    return "<h1>Seu pagamento está pendente. Aguarde a aprovação.</h1>"

if __name__ == '__main__':
    app.run(debug=True)
