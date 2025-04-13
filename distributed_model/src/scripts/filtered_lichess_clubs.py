import csv
from bs4 import BeautifulSoup

# Открываем HTML-файл и парсим его с помощью BeautifulSoup
with open('./a.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Список ключевых слов для поиска стран
country_keywords = [
    "USA", "Russia", "Iran", "Turkey", "India", "Brazil", "China", "Mexico", 
    "Argentina", "Lebanon", "Sri Lanka", "Kyrgyz Republic", "Sudan", "Japan",
    "France", "Germany", "Italy", "Spain", "Australia", "Egypt", "Ukraine", "England"
]

# Список для хранения подходящих клубов
filtered_clubs = []

# Найти все строки таблицы с клубами
club_rows = soup.find_all('tr')  # Предположим, что клубы находятся в строках таблицы

# Обрабатываем каждую строку таблицы
for row in club_rows:
    # Извлекаем название клуба и количество участников
    columns = row.find_all('td')
    if len(columns) >= 2:  # Убедимся, что в строке есть хотя бы 2 колонки (название и участники)
        club_name = columns[0].text.strip()  # Название клуба
        participants = columns[1].text.strip()  # Количество участников
        
        # Фильтруем клубы, которые содержат страну в названии
        if any(country in club_name for country in country_keywords):
            filtered_clubs.append([club_name, participants])

# Сохраняем отфильтрованные клубы в CSV
with open('filtered_lichess_clubs.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Club Name', 'Participants'])  # Заголовок
    for club in filtered_clubs:
        writer.writerow(club)

print(f"Сохранено {len(filtered_clubs)} клубов в файл 'filtered_lichess_clubs.csv'.")
