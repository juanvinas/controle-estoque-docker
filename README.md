# 📦 Controle de Estoque com Flask + Docker + Supabase

Este projeto é uma aplicação web desenvolvida com **Flask**, empacotada em um contêiner **Docker** e orquestrada com **Docker Compose**. A persistência dos dados é feita através de um banco de dados **PostgreSQL hospedado no Supabase**, permitindo escalabilidade e integração com serviços modernos.

🔗 Acesse a aplicação em produção: [http://meuprojetoestoque.duckdns.org:8080/](http://meuprojetoestoque.duckdns.org:8080/)

---

## 🚀 Tecnologias Utilizadas

- **Python 3.10+**
- **Flask** — framework web leve e flexível
- **Docker** — empacotamento e isolamento da aplicação
- **Docker Compose** — orquestração de múltiplos serviços
- **Supabase** — banco de dados PostgreSQL gerenciado na nuvem
- **DuckDNS** — serviço gratuito de DNS dinâmico para acesso público à aplicação
- **SMTP** — envio automático de e-mails para alertas de estoque

---

## 🧰 Funcionalidades

- Cadastro, edição e exclusão de produtos
- Controle de estoque com quantidade e movimentações
- Integração com banco de dados externo via Supabase
- Interface web simples e responsiva
- Envio automático de e-mail quando um item atinge o limite mínimo de estoque
- Pronto para deploy em ambientes cloud ou EC2

---

## ⚙️ Como executar localmente

### Pré-requisitos

- Docker e Docker Compose instalados
- Conta no [Supabase](https://supabase.com) com um projeto e banco configurado

### Passos

1. Clone o repositório:

```bash
git clone git@github.com:juanvinas/controle-estoque-docker.git
cd controle-estoque-docker
