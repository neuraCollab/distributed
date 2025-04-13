Да, вы можете использовать **Ansible** для автоматизации остановки всех контейнеров в вашем окружении Kubernetes или Docker вместо написания shell-скриптов. Ansible предоставляет мощные модули для управления Kubernetes и Docker, что делает процесс более управляемым, повторяемым и масштабируемым.

## Преимущества использования Ansible

1. **Повторяемость и идемпотентность**: Ansible гарантирует, что ваши задачи выполняются одинаково каждый раз без нежелательных побочных эффектов.
2. **Управление конфигурацией**: Легко управлять конфигурациями для различных сред (разработка, тестирование, продакшн).
3. **Масштабируемость**: Управляйте множеством узлов и кластеров одновременно.
4. **Документированность**: YAML-файлы Ansible служат документацией ваших процессов автоматизации.

## Использование Ansible для остановки контейнеров в Kubernetes

### Предварительные требования

1. **Ansible установлен на управляющем узле**: Убедитесь, что Ansible установлен. Если нет, установите его:
   ```bash
   sudo apt update
   sudo apt install ansible -y
   ```
2. **Доступ к кластеру Kubernetes**: Убедитесь, что `kubectl` настроен и может взаимодействовать с вашим кластером.
3. **Установлены необходимые модули Ansible**: Рекомендуется использовать коллекцию `community.kubernetes`.
   ```bash
   ansible-galaxy collection install community.kubernetes
   ```

### Пример Ansible Playbook для масштабирования всех Deployments, StatefulSets и DaemonSets до нуля

Создайте файл `stop_k8s_containers.yml` со следующим содержимым:

```yaml
---
- name: Остановить все Deployments, StatefulSets и DaemonSets в Kubernetes
  hosts: localhost
  gather_facts: no
  vars:
    # Пространства имен, которые нужно исключить (системные)
    excluded_namespaces:
      - kube-system
      - default
      - kube-public
      - kube-node-lease

  tasks:
    - name: Получить список всех пространств имен
      command: kubectl get namespaces -o json
      register: namespaces_result

    - name: Парсить имена пространств имен
      set_fact:
        namespaces: "{{ namespaces_result.stdout | from_json | json_query('items[?name!=`kube-system` && name!=`default` && name!=`kube-public` && name!=`kube-node-lease`].metadata.name') }}"

    - name: Масштабировать Deployments до 0 реплик
      community.kubernetes.k8s_scale:
        resource: deployment
        namespace: "{{ item }}"
        name: "{{ deploy.metadata.name }}"
        replicas: 0
        kind: Deployment
      loop: "{{ namespaces }}"
      loop_control:
        loop_var: namespace
      when: "'deployments' in namespace"
      register: scaled_deployments

    - name: Масштабировать StatefulSets до 0 реплик
      community.kubernetes.k8s_scale:
        resource: statefulset
        namespace: "{{ item }}"
        name: "{{ sts.metadata.name }}"
        replicas: 0
        kind: StatefulSet
      loop: "{{ namespaces }}"
      loop_control:
        loop_var: namespace
      when: "'statefulsets' in namespace"
      register: scaled_statefulsets

    - name: Масштабировать DaemonSets до 0 реплик (если применимо)
      community.kubernetes.k8s_scale:
        resource: daemonset
        namespace: "{{ item }}"
        name: "{{ ds.metadata.name }}"
        replicas: 0
        kind: DaemonSet
      loop: "{{ namespaces }}"
      loop_control:
        loop_var: namespace
      when: "'daemonsets' in namespace"
      register: scaled_daemonsets

    - name: Вывести сообщение об успешном масштабировании
      debug:
        msg: "Все Deployments, StatefulSets и DaemonSets масштабированы до 0 реплик в пространстве имен {{ item }}"
      loop: "{{ namespaces }}"
```

### Пояснение к Playbook

1. **Получение пространств имен**:
   - Используется команда `kubectl get namespaces -o json` для получения всех пространств имен.
   - Парсинг JSON-вывода для извлечения имен пространств, исключая системные (`kube-system`, `default`, `kube-public`, `kube-node-lease`).

2. **Масштабирование ресурсов**:
   - **Deployments**: Используется модуль `k8s_scale` для масштабирования всех Deployments в выбранных пространствах имен до 0 реплик.
   - **StatefulSets**: Аналогично масштабируются StatefulSets.
   - **DaemonSets**: Обычно DaemonSets должны иметь по одному поду на узел, поэтому масштабирование до 0 может быть не всегда применимо. Однако, если требуется, вы можете включить этот шаг.

3. **Вывод сообщений**: После успешного масштабирования выводится сообщение.

### Запуск Playbook

1. **Сохраните Playbook**: Сохраните приведённый выше код в файл `stop_k8s_containers.yml`.

2. **Запустите Playbook**:
   ```bash
   ansible-playbook stop_k8s_containers.yml
   ```

### Примечания

- **DaemonSets**: Масштабирование DaemonSets до 0 реплик может вызвать проблемы, так как DaemonSets предназначены для поддержания одного пода на узел. Если это не требуется, можно опустить шаг масштабирования DaemonSets.
- **Идёмпотентность**: Playbook можно запускать несколько раз без негативных последствий, поскольку масштабирование до 0 реплик повторяет состояние.
- **Восстановление**: Для возвращения ресурсов в рабочее состояние, создайте аналогичный Playbook с `replicas` равным исходному количеству.

## Использование Ansible для остановки всех Docker-контейнеров

Если вы хотите остановить все Docker-контейнеры на локальной машине или удалённых хостах, вы можете использовать Ansible с модулем `docker_container`.

### Пример Ansible Playbook для остановки всех Docker-контейнеров

Создайте файл `stop_docker_containers.yml` со следующим содержимым:

```yaml
---
- name: Остановить все Docker-контейнеры
  hosts: localhost  # Или укажите целевые хосты
  become: yes
  tasks:
    - name: Получить список всех запущенных контейнеров
      docker_container_info:
        all: false
      register: docker_containers

    - name: Остановить все запущенные контейнеры
      docker_container:
        name: "{{ item.Id }}"
        state: stopped
      loop: "{{ docker_containers.containers }}"
      when: docker_containers.containers | length > 0
      ignore_errors: yes

    - name: Вывести сообщение об успешной остановке
      debug:
        msg: "Все Docker-контейнеры остановлены."
      when: docker_containers.containers | length > 0
```

### Пояснение к Playbook

1. **Получение информации о контейнерах**:
   - Используется модуль `docker_container_info` для получения списка всех запущенных контейнеров.

2. **Остановка контейнеров**:
   - Используется модуль `docker_container` для остановки каждого контейнера по его идентификатору.
   - Параметр `ignore_errors: yes` позволяет продолжить выполнение даже если остановка некоторых контейнеров завершится с ошибкой.

3. **Вывод сообщения**: После успешной остановки выводится сообщение.

### Запуск Playbook

1. **Сохраните Playbook**: Сохраните приведённый выше код в файл `stop_docker_containers.yml`.

2. **Установите зависимости**: Убедитесь, что у вас установлены необходимые модули Ansible для Docker. Если вы используете Ansible коллекцию `community.docker`, установите её:
   ```bash
   ansible-galaxy collection install community.docker
   ```

3. **Запустите Playbook**:
   ```bash
   ansible-playbook stop_docker_containers.yml
   ```

### Примечания

- **Права доступа**: Для управления Docker-контейнерами может потребоваться повышенные привилегии (`become: yes`).
- **Идентификаторы контейнеров**: В данном примере используются идентификаторы контейнеров (`Id`). Можно использовать имена (`Names`) или другие атрибуты по необходимости.
- **Безопасность**: Будьте осторожны при остановке всех контейнеров, особенно на продакшн-серверах, чтобы избежать остановки критически важных сервисов.

## Заключение

Использование Ansible для управления контейнерами в Kubernetes и Docker предоставляет более структурированный и управляемый подход по сравнению с shell-скриптами. Вы можете легко масштабировать и изменять ваши процессы автоматизации, а также интегрировать их в более сложные пайплайны CI/CD.

**Рекомендации**:

1. **Тестирование**: Перед запуском Playbook в продакшене протестируйте его в тестовом окружении.
2. **Резервное копирование**: Убедитесь, что у вас есть резервные копии важных данных перед масштабированием или остановкой сервисов.
3. **Документация**: Документируйте ваши Playbook и процессы автоматизации для облегчения поддержки и передачи знаний.
4. **Мониторинг**: После остановки контейнеров следите за состоянием кластера и сервисов, чтобы убедиться, что всё работает как ожидается.

Если у вас возникнут дополнительные вопросы или потребуется помощь с более специфическими сценариями использования Ansible, пожалуйста, дайте знать!