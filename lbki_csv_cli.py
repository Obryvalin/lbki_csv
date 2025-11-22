# -*- coding: utf-8 -*-
"""
CLI версия LBKI CSV: Консольный интерфейс.
Поддерживает интерактивный режим и режим с argv для последовательности действий.

Примеры:
  python lbki_csv_cli.py data.csv                    # Интерактивный режим
  python lbki_csv_cli.py data.csv 4 3 8 output.csv   # Выбрать столбцы, удалить дубли, сохранить
"""

import sys
import os
from lbki_csv import *

def print_menu():
    """Выводит меню действий"""
    print("\n" + "="*50)
    print("МЕНЮ ДЕЙСТВИЙ:")
    print("1. Подсчитать строки")
    print("2. Показать первые N строк")
    print("3. Фильтр по текс��у")
    print("4. Выбрать столбцы")
    print("5. Удалить дубли")
    print("6. Свод по столбцу")
    print("7. Разделить в ZIP")
    print("8. Сохранить результат")
    print("9. Сбросить к исходным")
    print("0. Выход")
    print("="*50)

def execute_action(action, headers, rows, original_headers, original_rows):
    """Выполняет действие и возвращает (headers, rows, should_continue)"""
    
    if action == 1:  # Подсчитать строки
        cnt, cols = count_rows(headers, rows)
        print(f"\n✓ Строк: {cnt}, Столбцов: {cols}")
        return headers, rows, True
    
    elif action == 2:  # Показать первые N
        try:
            n = int(input("Сколько строк показать? "))
            if n <= 0:
                print("Число должно быть положительным")
                return headers, rows, True
            h, r = get_first_n(headers, rows, n)
            print("\n" + "\t".join(h))
            for row in r:
                print("\t".join(row))
            return headers, rows, True
        except ValueError:
            print("Введите число")
            return headers, rows, True
    
    elif action == 3:  # Фильтр по тексту
        query = input("Введите текст для фильтра: ")
        h, filtered = filter_by_text(headers, rows, query)
        filtered_count = len(filtered)
        print(f"\n✓ Отфильтровано: {filtered_count} строк")
        print("\t".join(h))
        for row in filtered:
            print("\t".join(row))
        return h, filtered, True
    
    elif action == 4:  # Выбрать столбцы
        print(f"\nДоступные столбцы: {', '.join(headers)}")
        cols = input("Столбцы через запятую: ")
        names = [c.strip() for c in cols.split(',')]
        h, r = select_columns(headers, rows, names)
        if h:
            print(f"✓ Выбрано {len(h)} столбцов")
            return h, r, True
        else:
            print("✗ Ошибка: неверные столбцы")
            return headers, rows, True
    
    elif action == 5:  # Удалить дубли
        h, r = remove_duplicates(headers, rows)
        deleted = len(rows) - len(r)
        print(f"✓ Удалено дублей: {deleted}")
        return h, r, True
    
    elif action == 6:  # Свод по столбцу
        print(f"\nДоступные столбцы: {', '.join(headers)}")
        col = input("Столбец для свода: ")
        h, r = group_by_column(headers, rows, col)
        if h:
            print(f"\n✓ Свод по '{col}':")
            print("\t".join(h))
            for row in r:
                print("\t".join(row))
            return h, r, True
        else:
            print("✗ Ошибка: столбец не найден")
            return headers, rows, True
    
    elif action == 7:  # Разделить в ZIP
        try:
            chunk_size = int(input("По сколько строк в части? "))
            if chunk_size <= 0:
                print("Число должно быть положительным")
                return headers, rows, True
            
            base_name = input("Базовое имя частей (по умолчанию 'part'): ").strip() or "part"
            zip_name = input("Имя ZIP-архива: ").strip()
            if not zip_name.endswith('.zip'):
                zip_name += '.zip'
            
            h, chunks = split_into_chunks(headers, rows, chunk_size)
            if zip_chunks(chunks, h, base_name, zip_name):
                print(f"✓ ZIP создан: {zip_name}")
            else:
                print("✗ Ошибка при создании ZIP")
            return headers, rows, True
        except ValueError:
            print("Введите число")
            return headers, rows, True
    
    elif action == 8:  # Сохранить результат
        file_out = input("Имя выходного файла (.csv): ").strip()
        if not file_out.endswith('.csv'):
            file_out += '.csv'
        
        if write_csv(file_out, headers, rows):
            print(f"✓ Сохранено: {file_out}")
        else:
            print("✗ Ошибка при сохранении")
        return headers, rows, True
    
    elif action == 9:  # Сбросить к исходным
        print("✓ Данные сброшены к исходным")
        return original_headers, original_rows, True
    
    elif action == 0:  # Выход
        return headers, rows, False
    
    else:
        print("✗ Неверный выбор")
        return headers, rows, True

def interactive_mode(file_path):
    """Интерактивный режим"""
    print(f"\n[LBKI CSV] Обрабатываю: {file_path}")
    
    headers, rows, encoding = read_csv(file_path)
    if headers is None:
        print("✗ Не удалось прочитать файл")
        return
    
    original_headers = headers
    original_rows = rows
    
    print(f"✓ Кодировка: {encoding}")
    print(f"✓ Загружено: {len(headers)} столбцов, {len(rows)} строк")
    
    while True:
        print(f"\nТекущие данные: {len(headers)} столбцов, {len(rows)} строк")
        print_menu()
        
        try:
            choice = int(input("Выберите действие (0-9): "))
            headers, rows, should_continue = execute_action(
                choice, headers, rows, original_headers, original_rows
            )
            if not should_continue:
                print("До свидания!")
                break
        except ValueError:
            print("✗ Введите число")

def batch_mode(file_path, actions, output_file):
    """Режим пакетной обработки через argv"""
    print(f"\n[LBKI CSV] Обрабатываю: {file_path}")
    
    headers, rows, encoding = read_csv(file_path)
    if headers is None:
        print("✗ Не удалось прочитать файл")
        return
    
    original_headers = headers
    original_rows = rows
    
    print(f"✓ Кодировка: {encoding}")
    print(f"✓ Загружено: {len(headers)} столбцов, {len(rows)} строк")
    
    # Выполняем действия
    for action_str in actions:
        try:
            action = int(action_str)
            print(f"\n→ Выполняю действие {action}...")
            headers, rows, _ = execute_action(
                action, headers, rows, original_headers, original_rows
            )
        except ValueError:
            print(f"✗ Неверное действие: {action_str}")
            return
    
    # Сохраняем результат
    if output_file:
        if not output_file.endswith('.csv'):
            output_file += '.csv'
        if write_csv(output_file, headers, rows, encoding):
            print(f"\n✓ Результат сохранён: {output_file}")
        else:
            print("✗ Ошибка при сохранении")
    else:
        print(f"\n✓ Финальные данные: {len(headers)} столбцов, {len(rows)} строк")

def main():
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python lbki_csv_cli.py <файл.csv>                    # Интерактивный режим")
        print("  python lbki_csv_cli.py <файл.csv> 4 5 8 <output.csv> # Пакетный режим")
        print("\nДействия:")
        print("  1 - Подсчитать строки")
        print("  2 - Показать первые N")
        print("  3 - Поиск")
        print("  4 - Выбрать столбцы")
        print("  5 - Удалить дубли")
        print("  6 - Свод по столбцу")
        print("  7 - Разделить в ZIP")
        print("  8 - Сохранить результат")
        print("  9 - Сбросить к исходным")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.isfile(file_path):
        print(f"✗ Файл не найден: {file_path}")
        sys.exit(1)
    
    # Проверяем, есть ли действия в argv
    if len(sys.argv) > 2:
        # Пакетный режим
        actions = sys.argv[2:-1]
        output_file = sys.argv[-1]
        batch_mode(file_path, actions, output_file)
    else:
        # Интерактивный режим
        interactive_mode(file_path)

if __name__ == "__main__":
    main()
