from flask import Flask, request, jsonify, render_template 
from supabase import create_client
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# --- CONFIGURAÇÕES INICIAIS ---
app = Flask(__name__)
CORS(app)

# 🔐 CONFIGURAÇÃO DO SUPABASE
url = "https://twxhlhmaoojypxaazfkj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR3eGhsaG1hb29qeXB4YWF6ZmtqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTkyMDk1MiwiZXhwIjoyMDc1NDk2OTUyfQ.oIvjfGy7yYwZYgJXrRHolkCBxs8VWv7fSLe8PZmmsOI"
supabase = create_client(url, key)

# 📧 CONFIGURAÇÃO DO GMAIL
EMAIL_REMETENTE = "juansuportaws@gmail.com"
SENHA_EMAIL = "zuwu ndnd qvar ldae"
EMAIL_DESTINATARIO = "jpablonunesvinas@gmail.com"

# --- FUNÇÃO PARA ENVIAR ALERTA POR EMAIL ---
def enviar_email_alerta(nome_item, quantidade, limite):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_REMETENTE
        msg["To"] = EMAIL_DESTINATARIO
        msg["Subject"] = f"⚠️ Alerta de Estoque Baixo: {nome_item}"

        corpo = f"""
O item {nome_item} está com o estoque baixo!
Quantidade atual: {quantidade}
Limite configurado: {limite}
"""

        msg.attach(MIMEText(corpo, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_REMETENTE, SENHA_EMAIL)
            server.send_message(msg)

        print(f"[EMAIL ENVIADO] Alerta enviado sobre {nome_item}")
    except Exception as e:
        print(f"[ERRO EMAIL] Não foi possível enviar alerta: {e}")

# --- ROTAS ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/itens")
def itens():
    resp = supabase.table("estoque").select("*").execute()
    dados = [
        {"item": i["item"], "quantidade": i["quantidade"], "limite_alerta": i.get("limite_alerta")}
        for i in resp.data
    ]
    return jsonify(dados)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    dados = request.get_json()
    nome = dados.get("item")
    quantidade = int(dados.get("quantidade", 0))
    limite_alerta = int(dados.get("limite_alerta", 0))

    # Verifica duplicidade
    existe = supabase.table("estoque").select("*").eq("item", nome).execute()
    if existe.data:
        return jsonify({"erro": "Item já existe."}), 400

    supabase.table("estoque").insert({
        "item": nome,
        "quantidade": quantidade,
        "status": "bom",
        "limite_alerta": limite_alerta
    }).execute()

    if limite_alerta and quantidade <= limite_alerta:
        enviar_email_alerta(nome, quantidade, limite_alerta)

    return jsonify({"mensagem": "Item adicionado com sucesso!"})

@app.route("/atualizar_quantidade", methods=["POST"])
def atualizar_quantidade():
    dados = request.get_json()
    nome = dados.get("item")
    delta = int(dados.get("delta", 0))

    resp = supabase.table("estoque").select("*").eq("item", nome).execute()
    if not resp.data:
        return jsonify({"erro": "Item não encontrado"}), 404

    quantidade_atual = resp.data[0]["quantidade"]
    limite_alerta = resp.data[0].get("limite_alerta", 0)
    nova_quantidade = quantidade_atual + delta

    supabase.table("estoque").update({"quantidade": nova_quantidade}).eq("item", nome).execute()

    if limite_alerta and nova_quantidade <= limite_alerta:
        enviar_email_alerta(nome, nova_quantidade, limite_alerta)

    return jsonify({"mensagem": "Quantidade atualizada"})

@app.route("/deletar", methods=["POST"])
def deletar():
    dados = request.get_json()
    nome = dados.get("item")

    supabase.table("estoque").delete().eq("item", nome).execute()
    return jsonify({"mensagem": "Item deletado com sucesso!"})

if __name__ == "__main__":
    # Define host com base no ambiente: Docker (production) ou local (development)
    host = "0.0.0.0" if os.getenv("FLASK_ENV") == "production" else "127.0.0.1"
    port = 5000
    debug = False if os.getenv("FLASK_ENV") == "production" else True
    app.run(host=host, port=port, debug=debug)
