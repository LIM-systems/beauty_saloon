import json
import csv
from datetime import datetime

# Пороговая дата (10 апреля 2025)
start_date = datetime(2025, 4, 10)


def parse_messages(messages):
    parsed = []
    status = ""  # Переменная для хранения статуса записи

    for entry in messages:
        if entry.get("type") != "message":
            continue

        # Преобразуем строку даты в datetime
        msg_date = datetime.fromisoformat(entry["date"])
        if msg_date < start_date:
            continue  # Пропускаем сообщения до 10 апреля 2025

        text = entry.get("text", [])
        if not isinstance(text, list):
            continue  # Пропускаем сообщения, где текст не является списком

        # Проверка статуса записи
        status = get_status_from_text(text)

        # Собираем информацию по клиенту, мастеру, услуге и времени
        client, phone, master, service, time, link = extract_details_from_text(
            text)

        # Сохраняем все данные в список
        parsed.append({
            "status": status,
            "client": client,
            "phone": phone,
            "master": master,
            "service": service,
            "time": time,
            "link": link
        })

    return parsed


def get_status_from_text(text):
    """
    Функция для извлечения статуса записи.
    """
    for item in text:
        if isinstance(item, dict):
            item_text = item.get("text", "")
            if "Новая запись!" in item_text:
                return "Новая запись"
            elif "Запись отменена!" in item_text:
                return "Запись отменена"
    return ""


def extract_details_from_text(text):
    """
    Функция для извлечения данных о клиенте, телефоне, мастере, услуге, времени и ссылке.
    """
    client, phone, master, service, time, link = "", "", "", "", "", ""

    for i, item in enumerate(text):
        if isinstance(item, str):
            # Поиск информации о клиенте, телефоне, мастере, услуге и времени
            if "Клиент:" in item:
                client = get_next_text(text, i)
            elif "Услуга:" in item:
                service = get_next_text(text, i)
            elif "Мастер:" in item:
                master = get_next_text(text, i)
            elif "Время:" in item:
                time = get_next_text(text, i)

    # Извлекаем телефон из элементов типа "code"
    phone = get_phone_from_text(text)

    # Извлекаем ссылку
    link = next((item["href"] for item in text if isinstance(
        item, dict) and item.get("type") == "text_link"), "")

    return client, phone, master, service, time, link


def get_next_text(text, index):
    """
    Функция для получения следующего текстового элемента после текущего.
    """
    if index + 1 < len(text) and isinstance(text[index + 1], dict):
        return text[index + 1]["text"]
    return ""


def get_phone_from_text(text):
    """
    Функция для извлечения номера телефона из элемента типа "code".
    """
    for item in text:
        if isinstance(item, dict) and item.get("type") == "code":
            return item.get("text", "")
    return ""


if __name__ == "__main__":
    try:
        # Чтение данных из JSON файла
        with open("data.json", "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        messages = raw_data.get("messages", [])
        parsed = parse_messages(messages)

        # Сохранение данных в CSV файл
        with open("parsed_messages.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                                    "status", "client", "phone", "master", "service", "time", "link"])
            writer.writeheader()
            writer.writerows(parsed)

        print("✅ Готово! Данные сохранены в parsed_messages.csv")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
