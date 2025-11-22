# -*- coding: utf-8 -*-
"""
Ядро LBKI CSV - инструмента: чтение, обработка, запись.
Используется и CLI, и GUI.
"""

import csv
import os
import zipfile

# === Определение кодировки и разделителя ===

def detect_encoding(file_path):
    """Определяем кодировку: utf-8 или cp1251."""
    for enc in ['utf-8', 'cp1251']:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                f.read(1000)
            return enc
        except UnicodeDecodeError:
            continue
    return None

def detect_delimiter(file_path, encoding):
    """Угадываем разделитель по частоте."""
    with open(file_path, 'r', encoding=encoding) as f:
        sample = f.read(1024)
    delimiters = [',', ';', '\t']
    best_delim = ','
    max_count = 0
    for delim in delimiters:
        count = sample.count(delim)
        if count > max_count:
            max_count = count
            best_delim = delim
    return best_delim if max_count > 0 else ','

def read_csv(file_path):
    """Читаем CSV → (headers, rows, encoding)."""
    encoding = detect_encoding(file_path)
    if not encoding:
        return None, None, None

    delimiter = detect_delimiter(file_path, encoding)
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            data = list(reader)
        if not data:
            return [], [], encoding
        headers = data[0]
        rows = data[1:]
        return headers, rows, encoding
    except Exception:
        return None, None, None

def write_csv(file_path, headers, rows, encoding='utf-8'):
    """Сохраняем CSV."""
    try:
        with open(file_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        return True
    except Exception:
        return False

# === Функции обработки (возвращают (headers, rows)) ===

def count_rows(headers, rows):
    """Подсчёт строк - только информация, не изменяет данные."""
    return len(rows), len(headers)

def get_first_n(headers, rows, n):
    """Первые N строк."""
    return headers, rows[:n]

def filter_by_text(headers, rows, query):
    """Фильтр по подстроке - оставляет только строки с найденным значением."""
    filtered = [row for row in rows if any(query.lower() in cell.lower() for cell in row)]
    return headers, filtered

def select_columns(headers, rows, col_names):
    """Выбор столбцов."""
    indices = []
    for name in col_names:
        if name in headers:
            indices.append(headers.index(name))
        else:
            return None, None
    new_rows = [[row[i] for i in indices] for row in rows]
    return [headers[i] for i in indices], new_rows

def remove_duplicates(headers, rows):
    """Удаление дублей."""
    seen = set()
    unique_rows = []
    for row in rows:
        key = tuple(row)
        if key not in seen:
            seen.add(key)
            unique_rows.append(row)
    return headers, unique_rows

def group_by_column(headers, rows, col_name):
    """Свод по столбцу."""
    if col_name not in headers:
        return None, None
    idx = headers.index(col_name)
    count_dict = {}
    for row in rows:
        key = row[idx].strip()
        count_dict[key] = count_dict.get(key, 0) + 1
    result = [["Значение", "Количество"]] + [[k, str(v)] for k, v in sorted(count_dict.items())]
    return result[0], result[1:]

def split_into_chunks(headers, rows, chunk_size):
    """Делим на части."""
    chunks = []
    for i in range(0, len(rows), chunk_size):
        chunks.append(rows[i:i+chunk_size])
    return headers, chunks

def zip_chunks(chunks, headers, base_name, zip_name):
    """Упаковка частей в ZIP."""
    temp_dir = "temp_split_parts"
    os.makedirs(temp_dir, exist_ok=True)
    files_to_zip = []

    for i, chunk in enumerate(chunks):
        filename = f"{base_name}_{i+1}.csv"
        filepath = os.path.join(temp_dir, filename)
        if not write_csv(filepath, headers, chunk, 'utf-8'):
            return False
        files_to_zip.append(filepath)

    try:
        with zipfile.ZipFile(zip_name, 'w') as z:
            for file in files_to_zip:
                z.write(file, os.path.basename(file))
        # Удаляем временные файлы
        for file in files_to_zip:
            os.remove(file)
        os.rmdir(temp_dir)
        return True
    except Exception:
        return False
