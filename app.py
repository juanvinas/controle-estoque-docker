# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from functools import wraps
import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURAÇÕES INICIAIS ---
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "chave-secreta-devops-2026")

# --- CONFIGURAÇÃO DE LOGS (AUDITORIA) ---
logging.basicConfig(
    filename='estoque_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 🔗 Conexão com PostgreSQL Local (usando o host 'db' do compose)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 📧 CONFIGURAÇÃO DO GMAIL
EMAIL_REMETENTE = os.getenv("EMAIL_REMETENTE")
SENHA_EMAIL = os.getenv("SENHA_EMAIL")

# 🔐 CREDENCIAIS DE ACESSO (Definidas no .env)
LOGIN_USER = os.getenv("USER_LOGIN", "admin")
LOGIN_PASSWORD = os.getenv("USER_PASSWORD", "123456")

# Lista na memória (limpa ao reiniciar o container)
emails_cadastrados = []

# --- DECORATOR PARA PROTEGER ROTAS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logado" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

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
            msg["Subject"] = f"Alerta de Estoque Baixo: {nome_item}"
            msg.set_charset("utf-8")

            corpo = f"O item {nome_item} está com o estoque baixo!\nQuantidade atual: {quantidade}\nLimite: {limite}"
            # Normaliza espaços invisíveis
            corpo = corpo.replace("\xa0", " ")

            msg.attach(MIMEText(corpo, "plain", "utf-8"))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(EMAIL_REMETENTE, SENHA_EMAIL)
                server.send_message(msg)

            logging.info(f"EMAIL: Alerta enviado para {destinatario} sobre o item {nome_item}")
        except Exception as e:
            logging.error(f"ERRO EMAIL: {e}")

# --- ROTAS DE AUTENTICAÇÃO ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario == LOGIN_USER and senha == LOGIN_PASSWORD:
            session["logado"] = True
            logging.info(f"AUTH: Usuário {usuario} logou com sucesso.")
            return redirect(url_for("index"))

        logging.warning(f"AUTH: Tentativa de login inválida para o usuário: {usuario}")
        return render_template("login.html", erro="Usuário ou senha incorretos")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logado", None)
    return redirect(url_for("login"))

# --- ROTAS DE OPERAÇÃO (PROTEGIDAS) ---
@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/itens")
@login_required
def itens():
    dados = Estoque.query.all()
    resultado = [
        {"item": i.item, "quantidade": i.quantidade, "limite_alerta": i.limite_alerta, "status": i.status}
        for i in dados
    ]
    return jsonify(resultado)

@app.route("/adicionar", methods=["POST"])
@login_required
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

    logging.info(f"ESTOQUE: Item '{nome}' adicionado com {quantidade} unidades.")

    if limite_alerta and quantidade <= limite_alerta:
        enviar_email_alerta(nome, quantidade, limite_alerta)

    return jsonify({"mensagem": "Item adicionado com sucesso!"})

@app.route("/atualizar_quantidade", methods=["POST"])
@login_required
def atualizar_quantidade():
    dados = request.get_json()
    nome = dados.get("item")
    delta = int(dados.get("delta", 0))

    item = Estoque.query.filter_by(item=nome).first()
    if not item:
        return jsonify({"erro": "Item não encontrado"}), 404

    item.quantidade += delta
    db.session.commit()

    logging.info(f"ESTOQUE: Quantidade de '{nome}' alterada em {delta}. Total: {item.quantidade}")

    if item.limite_alerta and item.quantidade <= item.limite_alerta:
        enviar_email_alerta(item.item, item.quantidade, item.limite_alerta)

    return jsonify({"mensagem": "Quantidade atualizada"})

# --- ROTAS DE CONFIGURAÇÃO DE E-MAIL ---
@app.route("/registrar-email", methods=["POST"])
@login_required
def registrar_email():
    email = request.form.get("email")
    if email and email not in emails_cadastrados:
        emails_cadastrados.append(email.strip())
        logging.info(f"CONFIG: E-mail {email} cadastrado para alertas.")
    return redirect(url_for("index"))

@app.route("/remover-email", methods=["POST"])
@login_required
def remover_email():
    email = request.form.get("email")
    if email in emails_cadastrados:
        emails_cadastrados.remove(email)
        logging.info(f"CONFIG: E-mail {email} removido dos alertas.")
    return redirect(url_for("index"))

# --- SEED E INICIALIZAÇÃO ---
with app.app_context():
    db.create_all()
    if not Estoque.query.first():
        itens_fixos = [
            {"item": "carregador", "quantidade": 10, "limite_alerta": 2},
            {"item": "mouse", "quantidade": 15, "limite_alerta": 3},
            {"item": "headset", "quantidade": 8, "limite_alerta": 2},
            {"item": "pilha AA", "quantidade": 20, "limite_alerta": 5},
            {"item": "pilha AAA", "quantidade": 25, "limite_alerta": 5},
        ]
        for d in itens_fixos:
            db.session.add(Estoque(item=d["item"], quantidade=d["quantidade"], limite_alerta=d["limite_alerta"]))
        db.session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
