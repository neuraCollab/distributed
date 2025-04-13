ANSIBLE_DIR = ./ansible
INVENTORY = $(ANSIBLE_DIR)/inventory.ini

.PHONY: all build run stop_docker stop_k8s

all:  pre_requirements build run

pre_requirements:
	 sudo apt-get update && sudo apt install ansible -y
# Задача для выполнения основного playbook (build и запуск)
build:
	ansible-playbook -i $(INVENTORY) $(ANSIBLE_DIR)/playbook.yml --tags all --ask-become-pass

b:
	ansible-playbook -i $(INVENTORY) $(ANSIBLE_DIR)/playbook.yml --tags generate_protos 
# Задача для запуска координатора и воркера
run:
	ansible-playbook -i $(INVENTORY) $(ANSIBLE_DIR)/playbook.yml --tags run_coordinator,run_worker

# Задача для остановки Docker контейнеров
stop_docker:
	ansible-playbook -i $(INVENTORY) $(ANSIBLE_DIR)/stop_docker_containers.yml

# Задача для остановки Kubernetes контейнеров
stop_k8s:
	ansible-playbook -i $(INVENTORY) $(ANSIBLE_DIR)/stop_k8s_containers.yml
