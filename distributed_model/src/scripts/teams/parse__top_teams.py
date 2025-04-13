import time
import csv
import berserk

def save_to_csv(data, filename):
    """Сохраняет список команд в CSV-файл."""
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["name", "nbMembers","id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for team in data:
            writer.writerow(team)
    print(f"Сохранено {len(data)} записей в {filename}")

def fetch_popular_teams(client, num_pages=250, pause=2, intermediate_save_file="teams_intermediate.csv"):
    teams_data = []
    for page in range(1, num_pages + 1):
        print(f"Запрос страницы {page}...")
        while True:
            try:
                result = client.teams.get_popular(page=page)
                break  # Если запрос успешен, выходим из цикла
            except Exception as e:
                # Если произошла ошибка, ждем 10 секунд и пробуем снова
                print(f"Ошибка при запросе страницы {page}: {e}")
                print("Жду 10 секунд перед повторной попыткой...")
                time.sleep(30)

        # Извлекаем список команд; ключ может называться "teams" или быть в другом формате
        teams = result.get("currentPageResults", [])
        for team in teams:
            name = team.get("name")
            nb_members = team.get("nbMembers")
            if name is not None and nb_members is not None:
                teams_data.append({
                    "id": team.get("id"),
                    "name": name,
                    "nbMembers": nb_members
                })
        # Сохраняем промежуточные результаты каждые 10 страниц
        if page % 10 == 0:
            print(f"Промежуточное сохранение после страницы {page}...")
            save_to_csv(teams_data, intermediate_save_file)
        time.sleep(pause)
    return teams_data

if __name__ == "__main__":
    # Создаем сессию и клиента для доступа к API Lichess
    session = berserk.TokenSession("lip_ThtMyF4qw6xgT04WmMA6")
    client = berserk.Client(session=session)
    
    # Получаем данные по популярным командам с первых 250 страниц
    # больше 40 страниц не дает
    teams_data = fetch_popular_teams(client, num_pages=40, pause=0.02, intermediate_save_file="teams_intermediate.csv")
    
    # Финальное сохранение данных
    final_csv = "teams_data.csv"
    save_to_csv(teams_data, final_csv)
    print("Скрипт завершен. Все данные сохранены.")
