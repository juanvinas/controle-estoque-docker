from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÕES INICIAIS ---
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "chave-secreta")  # necessária para sessões

# 🔗 Conexão com PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 📧 CONFIGURAÇÃO DO GMAIL
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
SENHA_EMAIL = os.getenv("SENHA_EMAIL")

# Lista de e-mails cadastrados via interface
emails_cadastrados = []

# --- MODELO DE ESTOQUE ---
class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), unique=True, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    limite_alerta = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default="bom")

# --- FUNÇÃO PARA ENVIAR ALERTA POR EMAIL ---
def enviar_email_alerta(nome_item, quantidade, limite):
    for destinatario in emails_cadastrados:
        try:
            msg = MIMEMultipart()
            msg["From"] = EMAIL_REMETENTE
            msg["To"] = destinatario
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

            print(f"[EMAIL ENVIADO] Alerta enviado para {destinatario}")
        except Exception as e:
            print(f"[ERRO EMAIL] Não foi possível enviar para {destinatario}: {e}")

# --- ROTAS ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/registrar-email", methods=["POST"])
def registrar_email():
    email = request.form.get("email")
    if email and email not in emails_cadastrados:
        emails_cadastrados.append(email)
        print(f"[EMAIL REGISTRADO] {email}")
    return redirect(url_for("index"))

@app.route("/remover-email", methods=["POST"])
def remover_email():
    email = request.form.get("email")
    if email in emails_cadastrados:
        emails_cadastrados.remove(email)
        print(f"[EMAIL REMOVIDO] {email}")
    return redirect(url_for("index"))

@app.route("/itens")
def itens():
    dados = Estoque.query.all()
    resultado = [
        {"item": i.item, "quantidade": i.quantidade, "limite_alerta": i.limite_alerta, "status": i.status}
        for i in dados
    ]
    return jsonify(resultado)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    dados = request.get_json()
    nome = dados.get("item")
    quantidade = int(dados.get("quantidade", 0))
    limite_alerta = int(dados.get("limite_alerta", 0))

    existe = Estoque.query.filter_by(item=nome).first()
    if existe:
        return jsonify({"erro": "Item já existe."}), 400

    novo = Estoque(item=nome, quantidade=quantidade, limite_alerta=limite_alerta, status="bom")
    db.session.add(novo)
    db.session.commit()

    if limite_alerta and quantidade <= limite_alerta:
        enviar_email_alerta(nome, quantidade, limite_alerta)

    return jsonify({"mensagem": "Item adicionado com sucesso!"})

@app.route("/atualizar_quantidade", methods=["POST"])
def atualizar_quantidade():
    dados = request.get_json()
    nome = dados.get("item")
    delta = int(dados.get("delta", 0))

    item = Estoque.query.filter_by(item=nome).first()
    if not item:
        return jsonify({"erro": "Item não encontrado"}), 404

    item.quantidade += delta
    db.session.commit()

    if item.limite_alerta and item.quantidade <= item.limite_alerta:
        enviar_email_alerta(item.item, item.quantidade, item.limite_alerta)

    return jsonify({"mensagem": "Quantidade atualizada"})

# --- NOVA ROTA PARA ATUALIZAR LIMITE ---
@app.route("/atualizar_limite", methods=["POST"])
def atualizar_limite():
    dados = request.get_json()
    nome = dados.get("item")
    novo_limite = int(dados.get("limite_alerta", 0))

    item = Estoque.query.filter_by(item=nome).first()
    if not item:
        return jsonify({"erro": "Item não encontrado"}), 404

    item.limite_alerta = novo_limite
    db.session.commit()

    return jsonify({"mensagem": f"Limite de alerta do item {nome} atualizado para {novo_limite}"})

# --- SEED INICIAL ---
with app.app_context():
    db.create_all()

    itens_fixos = [
        {"item": "carregador", "quantidade": 10, "limite_alerta": 2},
        {"item": "mouse", "quantidade": 15, "limite_alerta": 3},
        {"item": "headset", "quantidade": 8, "limite_alerta": 2},
        {"item": "pilha AA", "quantidade": 20, "limite_alerta": 5},
        {"item": "pilha AAA", "quantidade": 25, "limite_alerta": 5},
    ]

    for dados in itens_fixos:
        existe = Estoque.query.filter_by(item=dados["item"]).first()
        if not existe:
            novo = Estoque(
                item=dados["item"],
                quantidade=dados["quantidade"],
                limite_alerta=dados["limite_alerta"],
                status="bom"
            )
            db.session.add(novo)
    db.session.commit()

if __name__ == "__main__":
    host = "0.0.0.0" if os.getenv("FLASK_ENV") == "production" else "127.0.0.1"
    port = 5000
    debug = False if os.getenv("FLASK_ENV") == "production" else True
    app.run(host=host, port=port, debug=debug)
