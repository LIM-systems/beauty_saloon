from datetime import datetime, timedelta


def find_available_slots(visits, selected_date, work_start, work_end, service_duration):
    """
    Найти доступные слоты времени для записи на услугу.

    :param visits: список визитов [(start_time, duration_in_minutes)]
    :param selected_date: дата, для которой ищем доступные слоты (str, формат "%Y-%m-%d")
    :param work_start: начало рабочего дня (datetime.time)
    :param work_end: конец рабочего дня (datetime.time)
    :param service_duration: длительность новой услуги в минутах (int)
    :return: список доступных временных слотов [datetime.time]
    """
    # Преобразуем selected_date в объект datetime
    selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    # Получаем текущее время
    now = datetime.now()

    # Если выбранная дата раньше текущей, возвращаем пустой список
    if selected_date < now.date():
        return []

    # Если дата равна текущей, учитываем текущее время как ограничение
    if selected_date == now.date():
        start_time = now
    else:
        start_time = datetime.combine(selected_date, datetime.min.time())

    # Преобразуем визиты в занятые интервалы (start_time, end_time)
    busy_intervals = []
    for visit_start_time, duration in visits:
        # Преобразуем время визита в объект datetime
        visit_start_dt = datetime.combine(selected_date, visit_start_time)
        visit_end_dt = visit_start_dt + timedelta(minutes=duration)
        busy_intervals.append((visit_start_dt, visit_end_dt))

    # Добавляем начало и конец рабочего дня
    work_start_dt = datetime.combine(selected_date, work_start)
    work_end_dt = datetime.combine(selected_date, work_end)

    # Сортируем интервалы
    busy_intervals.sort()

    # Объединяем пересекающиеся и смежные интервалы
    merged_intervals = []
    for start, end in busy_intervals:
        if merged_intervals and merged_intervals[-1][1] >= start:
            merged_intervals[-1] = (merged_intervals[-1]
                                    [0], max(merged_intervals[-1][1], end))
        else:
            merged_intervals.append((start, end))

    # Проверяем каждый временной слот (с шагом 15 минут)
    available_slots = []
    current_time = start_time.replace(second=0, microsecond=0)

    # Убедимся, что проверяем время только в пределах рабочего дня
    while current_time + timedelta(minutes=service_duration) <= work_end_dt:
        # Время окончания услуги
        service_end_time = current_time + timedelta(minutes=service_duration)

        # Проверяем, пересекается ли текущий слот с занятыми интервалами
        is_free = all(not (current_time < end and service_end_time > start)
                      for start, end in merged_intervals)

        # Если слот свободен, добавляем его в доступные
        if is_free:
            # Убедимся, что слот находится в пределах рабочего дня
            if current_time >= work_start_dt and service_end_time <= work_end_dt:
                available_slots.append(current_time.time())

        # Переходим к следующему 15-минутному слоту
        current_time += timedelta(minutes=15)

    return available_slots


# Пример данных
visits = [
    (datetime.strptime("09:00", "%H:%M").time(), 30),  # Визит с 09:00 до 09:30
    (datetime.strptime("10:00", "%H:%M").time(), 60),  # Визит с 10:00 до 11:00
    (datetime.strptime("12:15", "%H:%M").time(), 45),  # Визит с 12:15 до 13:00
    (datetime.strptime("15:00", "%H:%M").time(), 30),  # Визит с 15:00 до 15:30
    (datetime.strptime("17:00", "%H:%M").time(), 30),
]

selected_date = '2025-01-29'  # Например, выбираем 29 января 2025
work_start = datetime.strptime("09:00", "%H:%M").time()  # Начало рабочего дня
work_end = datetime.strptime("18:00", "%H:%M").time()  # Конец рабочего дня

service_duration = 60  # Длительность новой услуги: 1 час

# Найти доступные слоты
available_slots = find_available_slots(
    visits, selected_date, work_start, work_end, service_duration)

# Вывести результаты
print("Доступные временные слоты:")
for slot in available_slots:
    print(slot)
