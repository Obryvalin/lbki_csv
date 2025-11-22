# -*- coding: utf-8 -*-
"""
CLI версия LBKI CSV: меню или команды через argv.
"""

import sys
import os
from lbki_csv import *

def print_help():
    print("""
Использование:
  python lbki_cli.py <файл.csv>                        → запуск меню
  python lbki_cli.py <файл.csv> --count                → подсчитать строки
  python lbki_cli.py <файл.csv> --head N               → первые N строк
  python lbki_cli.py <файл.csv> --search "текст"       → поиск
  python lbki_cli.py <файл.csv> --select col1,col2     → выбрать столбцы
  python lbki_cli.py <файл.csv> --dedup --zip 1000     → удалить дубли + разделить в ZIP
    """)
    sys.exit(1)

def main_menu(headers, rows, file_path):
    while True:
        print("\n" + "="*60)
        print("LBKI CSV — CLI")
        print("1. Подсчитать строки")
        print("2. Показать первые N строк")
        print("3. Поиск по строке")
        print("4. Выбрать столбцы")
        print("5. Сменить кодировку")
        print("6. Удалить дубли")
        print("7. Свод по столбцу")
        print("8. Разделить и упаковать в ZIP")
        print("9. Выйти")
        choice = input("\nВыберите: ").strip()

        if choice == '1':
            cnt, cols = count_rows(headers, rows)
            print(f"\nСтрок: {cnt}, Столбцов: {cols}")

        elif choice == '2':
            try:
                n = int(input("N = "))
                h, r = get_first_n(headers, rows, n)
                print("\t".join(h))
                for row in r:
                    print("\t".join(row))
            except:
                print("Ошибка ввода.")

        elif choice == '3':
            query = input("Поиск: ")
            h, matches = search_in_rows(headers, rows, query)
            print(f"Найдено: {len(matches)}")
            print("\t".join(h))
            for m in matches:
                print("\t".join(m))

        elif choice == '4':
            cols = input(f"Столбцы (через запятую): [{', '.join(headers)}]\n")
            col_names = [c.strip() for c in cols.split(',')]
            new_headers, new_rows = select_columns(headers, rows, col_names)
            if new_headers is None:
                print(new_rows)
            else:
                out = input("Файл: ") or "selected.csv"
                if not out.endswith('.csv'): out += '.csv'
                if write_csv(out, new_headers, new_rows):
                    print(f"Сохранено: {out}")

        elif choice == '5':
            enc = input("Кодировка (utf-8/cp1251): ").strip()
            if enc not in ['utf-8', 'cp1251']:
                print("Только utf-8 или cp1251")
                continue
            out = input("Выходной файл: ") or f"converted_{os.path.basename(file_path)}"
            if write_csv(out, headers, rows, enc):
                print(f"Сохранено в {enc}: {out}")

        elif choice == '6':
            h, r = remove_duplicates(headers, rows)
            out = input("Файл без дублей: ") or "dedup.csv"
            if write_csv(out, h, r):
                print(f"Дубли удалены. Сохранено: {out}")
                rows[:] = r  # обновляем

        elif choice == '7':
            col = input(f"Столбец для свода? [{', '.join(headers)}]: ")
            h, r = group_by_column(headers, rows, col)
            if h is None:
                print(r)
            else:
                out = input("Файл свода: ") or "group.csv"
                if write_csv(out, h, r):
                    print(f"Свод сохранён: {out}")

        elif choice == '8':
            try:
                n = int(input("Размер части: "))
                base = input("Имя частей: ") or "part"
                zip_name = input("ZIP файл: ") or "parts.zip"
                h, chunks = split_into_chunks(headers, rows, n)
                if zip_chunks(chunks, h, base, zip_name):
                    print(f"Части упакованы: {zip_name}")
                else:
                    print("Ошибка упаковки.")
            except:
                print("Ошибка ввода.")

        elif choice == '9':
            print("Выход.")
            break

        else:
            print("Неверный выбор.")

def run_commands(headers, rows, file_path, args):
    actions = []
    output_encoding = 'utf-8'

    i = 1
    while i < len(args):
        arg = args[i]
        if arg == '--count':
            cnt, cols = count_rows(headers, rows)
            print(f"COUNT: {cnt} строк, {cols} столбцов")
        elif arg == '--head' and i+1 < len(args):
            n = int(args[i+1]); i += 1
            h, r = get_first_n(headers, rows, n)
            print("\t".join(h))
            for row in r: print("\t".join(row))
        elif arg == '--search' and i+1 < len(args):
            query = args[i+1]; i += 1
            h, matches = search_in_rows(headers, rows, query)
            print(f"SEARCH '{query}' → {len(matches)} результатов")
            for m in matches: print("\t".join(m))
        elif arg == '--select' and i+1 < len(args):
            cols = [c.strip() for c in args[i+1].split(',')]; i += 1
            h, r = select_columns(headers, rows, cols)
            if h: write_csv('selected.csv', h, r); print("SELECT → selected.csv")
            else: print(r)
        elif arg == '--dedup':
            headers, rows = remove_duplicates(headers, rows)
            print(f"DEDUP: осталось {len(rows)} строк")
        elif arg == '--zip' and i+1 < len(args):
            n = int(args[i+1]); i += 1
            h, chunks = split_into_chunks(headers, rows, n)
            if zip_chunks(chunks, h, 'part', 'split.zip'):
                print("ZIP: split.zip готов")
            else:
                print("Ошибка ZIP")
        else:
            print(f"Неизвестный аргумент: {arg}")
        i += 1

def main():
    if len(sys.argv) < 2:
        print_help()

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Файл не найден: {file_path}")
        sys.exit(1)

    headers, rows, encoding = read_csv(file_path)
    if headers is None:
        print("Ошибка чтения файла.")
        sys.exit(1)

    print(f"Загружено: {len(headers)} столбцов, {len(rows)} строк")

    if len(sys.argv) == 2:
        main_menu(headers, rows, file_path)
    else:
        run_commands(headers, rows, file_path, sys.argv[2:])

if __name__ == "__main__":
    main()