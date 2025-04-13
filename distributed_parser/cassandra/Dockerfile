# Используем официальный образ Cassandra
FROM cassandra:latest

# Открываем стандартный порт Cassandra
EXPOSE 7000 7001 7199 9042 9160

# Копируем .env файл в контейнер (необязательно, если переменные подаются через docker-compose)
COPY ../.env /app/.env

# Используем переменные окружения из .env
ENV CASSANDRA_CLUSTER_NAME ${CASSANDRA_CLUSTER_NAME}
ENV CASSANDRA_DC ${CASSANDRA_DC}
ENV CASSANDRA_RACK ${CASSANDRA_RACK}
ENV CASSANDRA_SEEDS ${CASSANDRA_SEEDS}
ENV CASSANDRA_LISTEN_ADDRESS ${CASSANDRA_LISTEN_ADDRESS}
ENV CASSANDRA_BROADCAST_ADDRESS ${CASSANDRA_BROADCAST_ADDRESS}
ENV CASSANDRA_BROADCAST_RPC_ADDRESS ${CASSANDRA_BROADCAST_RPC_ADDRESS}
ENV CASSANDRA_ENDPOINT_SNITCH ${CASSANDRA_ENDPOINT_SNITCH}

# Старт сервера Cassandra
CMD ["cassandra", "-f"]
