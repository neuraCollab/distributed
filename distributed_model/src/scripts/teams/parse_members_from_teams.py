import csv
import time
import requests
import json

# Параметры
lichess_host = "https://lichess.org"
input_csv = "teams_data.csv"       # CSV с колонкой "id" (идентификатор команды)
output_json = "teams_members.json" # Итоговый JSON с данными участников

all_teams_members = {}

with open(input_csv, newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        team_id = row.get("id")
        if not team_id:
            continue

        print(f"Запрашиваем участников команды '{team_id}'...")
        url = f"{lichess_host}/api/team/{team_id}/users"
        try:
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                print(f"Ошибка {response.status_code} при запросе {url}")
                continue

            # Собираем данные для команды: каждая строка – отдельный JSON-объект (NDJSON)
            members = []
            for line in response.iter_lines():
                if line:
                    try:
                        member = json.loads(line.decode('utf-8'))
                        members.append(member)
                    except Exception as e:
                        print("Ошибка обработки строки:", e)
            all_teams_members[team_id] = members
        except Exception as e:
            print(f"Ошибка при запросе участников команды {team_id}: {e}")

        # Сохраняем промежуточные результаты после обработки каждой команды
        with open(output_json, 'w', encoding='utf-8') as outfile:
            json.dump(all_teams_members, outfile, ensure_ascii=False, indent=2)
        print(f"Промежуточные результаты сохранены для команды '{team_id}'.")
        
        # Пауза между запросами для защиты от перегрузки сервера
        time.sleep(10)

print("Готово! Все данные об участниках команд сохранены в", output_json)
