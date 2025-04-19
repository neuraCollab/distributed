#!/usr/bin/env python3
import argparse
import re
import csv
import requests
from datetime import datetime

APACHE_LOG_URL = (
    "https://raw.githubusercontent.com/elastic/examples/"
    "master/Common%20Data%20Formats/apache_logs/apache_logs"
)

LOG_PATTERN = re.compile(
    r'^\S+ \S+ \S+ \[(?P<ts>[^\]]+)\] '
    r'"(?:GET|POST) (?P<endpoint>\S+) HTTP/[^"]+" \d+ (?P<size>\d+)'
)


def parse_apache_line(line: str):
    m = LOG_PATTERN.match(line)
    if not m:
        return None
    ts = datetime.strptime(m.group('ts'), '%d/%b/%Y:%H:%M:%S %z')
    ts_iso = ts.astimezone().isoformat()
    size = int(m.group('size'))
    latency_s = size / 500.0
    return ts_iso, m.group('endpoint'), latency_s

def download_and_parse(max_lines: int, output_csv: str):
    """
    Скачивает первые max_lines строк из большого apache_logs-файла,
    парсит их и сохраняет в CSV (timestamp, endpoint, latency).
    """
    resp = requests.get(APACHE_LOG_URL, stream=True)
    resp.raise_for_status()
    writer = csv.writer(open(output_csv, 'w', newline='', encoding='utf-8'))
    writer.writerow(['timestamp', 'endpoint', 'latency'])
    count = 0
    for raw in resp.iter_lines(decode_unicode=True):
        if count >= max_lines:
            break
        parsed = parse_apache_line(raw)
        if parsed:
            writer.writerow(parsed)
            count += 1
    print(f"Parsed {count} lines → {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Скачать тестовый apache_logs и вывести logs.csv"
    )
    parser.add_argument(
        '-n', '--lines',
        type=int,
        default=500,
        help="Сколько строк парсить (по умолчанию 500)"
    )
    parser.add_argument(
        '-o', '--output',
        default='logs.csv',
        help="Имя выходного CSV (по умолчанию logs.csv)"
    )
    args = parser.parse_args()
    download_and_parse(args.lines, args.output)
    print(f"Saved to {args.output}")