#!/bin/bash

# Загрузка переменных из .env файла
export $(grep -v '^#' ../.env | xargs)

# Проверка, что переменная KUBERNETES_NAMESPACE задана
if [ -z "$KUBERNETES_NAMESPACE" ]; then
    echo "Error: KUBERNETES_NAMESPACE is not set in the .env file."
    exit 1
fi

# Создание namespace для проекта (если он не существует)
kubectl create namespace $KUBERNETES_NAMESPACE || echo "Namespace $KUBERNETES_NAMESPACE already exists"

# Создание ConfigMap с переменными окружения
envsubst < ../kubernetes/env-configmap.yaml | kubectl apply -n $KUBERNETES_NAMESPACE -f -

# Применение конфигураций для координатора
envsubst < ../kubernetes/coordinator-deployment.yaml | kubectl apply -n $KUBERNETES_NAMESPACE -f -
envsubst < ../kubernetes/coordinator-service.yaml | kubectl apply -n $KUBERNETES_NAMESPACE -f -

# Применение конфигураций для воркеров
envsubst < ../kubernetes/worker-deployment.yaml | kubectl apply -n $KUBERNETES_NAMESPACE -f -
envsubst < ../kubernetes/worker-service.yaml | kubectl apply -n $KUBERNETES_NAMESPACE -f -

# Применение конфигураций для Cassandra
envsubst < ../kubernetes/cassandra-statefulset.yaml | kubectl apply -n $KUBERNETES_NAMESPACE -f -
envsubst < ../kubernetes/cassandra-service.yaml | kubectl apply -n $KUBERNETES_NAMESPACE -f -

echo "All components have been deployed to Kubernetes namespace $KUBERNETES_NAMESPACE!"
