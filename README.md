# 📦 Controle de Estoque com Flask + Docker + Postgres

Este projeto é uma aplicação web desenvolvida com **Flask**, empacotada em um contêiner **Docker** e orquestrada com **Docker Compose**.  
A persistência dos dados é feita através de um banco de dados **PostgreSQL** rodando em container próprio, garantindo robustez e persistência local.  
O acesso público é configurado via **DuckDNS**, permitindo que a aplicação seja acessada externamente por domínio dinâmico.

🔗 **Acesse a aplicação em produção:**  
[https://meuprojetoestoque.duckdns.org/]

---

## 🚀 Tecnologias Utilizadas
- **Python 3.10+** — linguagem principal  
- **Flask** — framework web leve e flexível  
- **Docker** — empacotamento e isolamento da aplicação  
- **Docker Compose** — orquestração de múltiplos serviços (Flask + Postgres)  
- **PostgreSQL** — banco de dados relacional persistente  
- **DuckDNS** — DNS dinâmico para acesso público  
- **SMTP (Gmail)** — envio automático de e-mails para alertas de estoque  

---

## 🧰 Funcionalidades
- Cadastro, edição e exclusão de produtos  
- Controle de estoque com movimentações e histórico  
- Persistência dos dados em banco **Postgres local**  
- Interface web simples e responsiva  
- Envio automático de e-mail quando um item atinge o limite mínimo de estoque  
- Deploy pronto para ambientes locais, servidores cloud ou EC2  

---

## ⚙️ Como executar localmente

### Pré-requisitos
- Docker e Docker Compose instalados  
- Conta no Gmail com senha de aplicativo configurada (para envio de e-mails)  

### Passos
1. Clone o repositório:
   ```bash
   git clone git@github.com:juanvinas/controle-estoque-docker.git
   cd controle-estoque-docker
