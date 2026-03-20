# 📦 Sistema de Controle de Estoque (Flask + Docker + SRE)

![Docker Pulls](https://img.shields.io/docker/pulls/jpablonunes/contro-estoque-1)
![Docker Image Size](https://img.shields.io/docker/image-size/jpablonunes/contro-estoque-1)
![Build Status](https://img.shields.io/badge/status-online-brightgreen)

Este projeto é uma solução completa de controle de estoque conteinerizada, projetada com foco em **resiliência, portabilidade e segurança**. A aplicação utiliza uma arquitetura de microserviços isolados para garantir que o banco de dados, o servidor web e a lógica da aplicação operem de forma independente e segura.

🔗 **Acesse em produção:** [https://meuprojetoestoque.duckdns.org/](https://meuprojetoestoque.duckdns.org/)

---

## 🏗️ Arquitetura da Infraestrutura

Diferente de aplicações monolíticas simples, este projeto implementa um fluxo de tráfego moderno utilizando **Proxy Reverso**:

* **Nginx:** Atua como a "porta de entrada", gerenciando a terminação SSL e o redirecionamento de tráfego.
* **Flask App (Gunicorn):** O core da aplicação, rodando em uma imagem imutável hospedada no Docker Hub.
* **PostgreSQL 15:** Banco de dados relacional com volumes persistentes para garantir que os dados sobrevivam a reinicializações.
* **Certbot (Let's Encrypt):** Automação completa para emissão e renovação de certificados SSL/TLS.

---

## 🚀 Como subir em uma máquina Linux (Deploy Rápido)

Este projeto foi otimizado para o conceito de **"Zero Configuration"**. Basta ter o Docker instalado e rodar um comando.

### 1. Pré-requisitos
Certifique-se de ter o Docker e o Docker Compose instalados em sua VM Linux:
```bash
sudo apt update && sudo apt install docker.io docker-compose -y
2. Clonar o Repositório
Bash
git clone [https://github.com/juanvinas/controle-estoque-docker.git](https://github.com/juanvinas/controle-estoque-docker.git)
cd controle-estoque-docker
3. Configurar Variáveis de Ambiente
Crie um arquivo .env para proteger suas credenciais (não suba este arquivo para o Git!):

Bash
nano .env
Exemplo de conteúdo:

Snippet de código
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=estoque_db
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app-gmail
4. Start do Ambiente
Como o projeto utiliza a imagem oficial já compilada no Docker Hub, o deploy é instantâneo:

Bash
docker-compose up -d
🛡️ Diferenciais de SRE & DevOps
Imutabilidade: O deploy utiliza imagens pré-construídas em jpablonunes/contro-estoque-1, garantindo que o comportamento seja idêntico em qualquer servidor.

Networking: Containers isolados em uma rede bridge interna, expondo apenas as portas estritamente necessárias (80/443).

Persistência de Dados: Uso de Docker Volumes para o PostgreSQL, evitando a perda de inventário em caso de falha do container.

Segurança: Terminação SSL configurada com Nginx para tráfego criptografado.

🧰 Funcionalidades Principais
✅ Cadastro, edição e exclusão de produtos com histórico de movimentação.

✅ Alertas de Estoque Baixo: Envio automático de e-mail via SMTP quando um item atinge o limite crítico.

✅ Dashboard responsivo para acesso via mobile ou desktop.

✅ Logs centralizados via Docker para monitoramento de saúde da aplicação.

Desenvolvido por Juan Vinas
Atualmente atuando como Suporte de TI e migrando para DevOps/SRE.
