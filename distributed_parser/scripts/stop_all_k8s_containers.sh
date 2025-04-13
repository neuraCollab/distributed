#!/bin/bash

# Получаем список всех пространств имен, исключая системные
NAMESPACES=$(kubectl get namespaces --no-headers -o custom-columns=":metadata.name" | grep -vE 'kube-system|default|kube-public|kube-node-lease')

for ns in $NAMESPACES; do
    echo "Обрабатываем пространство имен: $ns"

    # Масштабируем все Deployments до 0
    deployments=$(kubectl get deployments -n "$ns" -o name)
    for deploy in $deployments; do
        echo "Масштабируем Deployment: $deploy в 0 реплик"
        kubectl scale --replicas=0 "$deploy" -n "$ns"
    done

    # Масштабируем все StatefulSets до 0
    statefulsets=$(kubectl get statefulsets -n "$ns" -o name)
    for sts in $statefulsets; do
        echo "Масштабируем StatefulSet: $sts в 0 реплик"
        kubectl scale --replicas=0 "$sts" -n "$ns"
    done

    # Масштабируем все DaemonSets до 0 (что не всегда применимо, но возможно)
    daemonsets=$(kubectl get daemonsets -n "$ns" -o name)
    for ds in $daemonsets; do
        echo "Масштабируем DaemonSet: $ds до 0 реплик"
        kubectl scale --replicas=0 "$ds" -n "$ns"
    done

    echo "---------------------------------------"
done

echo "Все Deployments, StatefulSets и DaemonSets масштабированы до 0 реплик."
