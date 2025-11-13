#!/bin/bash

# Script para ajustar limites de alerta dos itens no estoque
# Uso: ./ajustar_limites.sh [HOST]
# Exemplo interno (na própria EC2): ./ajustar_limites.sh localhost
# Exemplo externo (do seu PC): ./ajustar_limites.sh SEU_IP_PUBLICO

HOST=${1:-localhost}
PORT=8080

echo "🔧 Atualizando limites de alerta no host $HOST:$PORT ..."

curl -s -X POST http://$HOST:$PORT/atualizar_limite \
     -H "Content-Type: application/json" \
     -d '{"item":"mouse","limite_alerta":10}'

curl -s -X POST http://$HOST:$PORT/atualizar_limite \
     -H "Content-Type: application/json" \
     -d '{"item":"carregador","limite_alerta":10}'

curl -s -X POST http://$HOST:$PORT/atualizar_limite \
     -H "Content-Type: application/json" \
     -d '{"item":"headset","limite_alerta":10}'

curl -s -X POST http://$HOST:$PORT/atualizar_limite \
     -H "Content-Type: application/json" \
     -d '{"item":"pilha AA","limite_alerta":8}'

curl -s -X POST http://$HOST:$PORT/atualizar_limite \
     -H "Content-Type: application/json" \
     -d '{"item":"pilha AAA","limite_alerta":6}'

echo "✅ Limites ajustados com sucesso!"

echo "📋 Conferindo itens atualizados..."
curl -s http://$HOST:$PORT/itens | jq .
