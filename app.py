# -*- coding: utf-8 -*-
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "chave-it-suporte")

# Configuração do banco (Usando DATABASE_URI do seu .env)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Logs de Auditoria
logging.basicConfig(filename='estoque_audit.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Configuração do login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# --- MODELOS ---
class Estoque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    limite_alerta = db.Column(db.Integer, nullable=False)

class EmailAlerta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

# --- FUNÇÃO DE ENVIO DE E-MAIL ---
def enviar_email_alerta(nome_item, quantidade, limite):
    remetente = os.getenv("EMAIL_REMETENTE")
    senha = os.getenv("SENHA_EMAIL")
    
    # Busca todos os e-mails cadastrados no banco de dados
    destinatarios = [e.email for e in EmailAlerta.query.all()]
    
    if not destinatarios:
        logging.info(f"ALERTA: Item {nome_item} baixo, mas nenhum e-mail cadastrado.")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = remetente
        msg["Subject"] = f"Alerta de Estoque: {nome_item}"
        
        corpo = f"O item {nome_item} atingiu o limite.\nQtd Atual: {quantidade}\nLimite: {limite}"
        msg.attach(MIMEText(corpo, "plain", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(remetente, senha)
            for destinatario in destinatarios:
                msg["To"] = destinatario
                server.send_message(msg)
        logging.info(f"EMAIL: Alerta enviado para {len(destinatarios)} pessoas.")
    except Exception as e:
        logging.error(f"ERRO EMAIL: {str(e)}")

# --- ROTAS ---

@app.route('/')
def home():
    produtos = Estoque.query.all()
    emails = EmailAlerta.query.all()
    return render_template('index.html', produtos=produtos, emails=emails)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        if user == os.getenv("USER_LOGIN") and password == os.getenv("USER_PASSWORD"):
            login_user(User(user))
            return redirect(url_for('home'))
        flash("Usuario ou senha invalidos", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/adicionar', methods=['POST'])
@login_required
def adicionar_item():
    item = request.form['item']
    quantidade = int(request.form['quantidade'])
    limite = int(request.form['limite'])
    novo = Estoque(item=item, quantidade=quantidade, limite_alerta=limite)
    db.session.add(novo)
    db.session.commit()
    
    if quantidade <= limite:
        enviar_email_alerta(item, quantidade, limite)
    return redirect(url_for('home'))

@app.route('/remover/<int:id>', methods=['POST'])
@login_required
def remover_item(id):
    produto = Estoque.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/atualizar/<int:id>/<string:acao>', methods=['POST'])
@login_required
def atualizar_item(id, acao):
    produto = Estoque.query.get_or_404(id)
    if acao == "mais":
        produto.quantidade += 1
    elif acao == "menos" and produto.quantidade > 0:
        produto.quantidade -= 1
    
    db.session.commit()
    if produto.quantidade <= produto.limite_alerta:
        enviar_email_alerta(produto.item, produto.quantidade, produto.limite_alerta)
    return redirect(url_for('home'))

# Rotas de Gerenciamento de E-mail
@app.route('/email/cadastrar', methods=['POST'])
@login_required
def cadastrar_email():
    email = request.form.get('email')
    if email:
        try:
            novo = EmailAlerta(email=email)
            db.session.add(novo)
            db.session.commit()
            flash("E-mail adicionado!", "success")
        except:
            db.session.rollback()
            flash("E-mail ja cadastrado", "warning")
    return redirect(url_for('home'))

@app.route('/email/remover/<int:id>', methods=['POST'])
@login_required
def remover_email(id):
    email_obj = EmailAlerta.query.get_or_404(id)
    db.session.delete(email_obj)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
