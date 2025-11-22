# -*- coding: utf-8 -*-
"""
CSV Мастер — Графическая версия (только tkinter + стандартные модули)
"""

import csv
import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, MULTIPLE, END

# --- ТЕ ЖЕ ФУНКЦИИ, ЧТО И РАНЬШЕ (без изменений) ---

def detect_encoding(file_path):
    for enc in ['utf-8', 'cp1251']:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                f.read(1000)
            return enc
        except UnicodeDecodeError:
            continue
    return None

def detect_delimiter(file_path, encoding):
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
    encoding = detect_encoding(file_path)
    if not encoding:
        messagebox.showerror("Ошибка", "Не удалось определить кодировку.")
        return None, None

    delimiter = detect_delimiter(file_path, encoding)
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            data = list(reader)
        if not data:
            messagebox.showinfo("Пустой файл", "Файл пуст.")
            return None, None
        headers = data[0]
        rows = data[1:]
        return headers, rows
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{e}")
        return None, None

def write_csv(file_path, headers, rows, encoding='utf-8'):
    try:
        with open(file_path, 'w', encoding=encoding, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось записать файл:\n{e}")
        return False

# --- НОВЫЙ GUI КЛАСС ---

class CSVToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Мастер — Ильич v1.0")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")

        self.file_path = None
        self.headers = None
        self.rows = None

        self.setup_ui()

    def setup_ui(self):
        # Заголовок
        title = tk.Label(self.root, text="CSV Мастер", font=("Arial", 16, "bold"), bg="#f0f0f0")
        title.pack(pady=10)

        # Кнопка выбора файла
        self.btn_load = tk.Button(self.root, text="📂 Открыть CSV файл", font=("Arial", 12),
                                  command=self.load_file, bg="#4CAF50", fg="white", width=30)
        self.btn_load.pack(pady=10)

        # Информация о файле
        self.info_label = tk.Label(self.root, text="Файл не загружен", bg="#f0f0f0", fg="gray")
        self.info_label.pack(pady=5)

        # Список функций
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.func_list = Listbox(frame, yscrollcommand=scrollbar.set, font=("Courier", 11),
                                 selectmode=MULTIPLE, height=10)
        self.func_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.func_list.yview)

        # Заполняем список функций (неактивен до загрузки)
        functions = [
            "1. Подсчитать строки",
            "2. Показать первые N строк",
            "3. Поиск по строке",
            "4. Выбрать столбцы",
            "5. Сменить кодировку",
            "6. Удалить дубли",
            "7. Свод по столбцу",
            "8. Разделить и ZIP"
        ]
        for func in functions:
            self.func_list.insert(END, func)

        # Кнопка выполнения
        self.btn_run = tk.Button(self.root, text="▶ Запустить выбранное", font=("Arial", 12),
                                 command=self.run_selected, bg="#2196F3", fg="white")
        self.btn_run.pack(pady=10)
        self.btn_run.config(state=tk.DISABLED)

    def load_file(self):
        path = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return

        self.file_path = path
        self.headers, self.rows = read_csv(path)
        if self.headers is None:
            return

        self.info_label.config(
            text=f"Загружено: {len(self.headers)} столбцов, {len(self.rows)} строк",
            fg="black"
        )
        self.btn_run.config(state=tk.NORMAL)
        messagebox.showinfo("Готово", f"Файл загружен.\nКодировка: UTF-8 или CP1251")

    def run_selected(self):
        if not self.func_list.curselection():
            messagebox.showwarning("Внимание", "Выберите хотя бы одну функцию.")
            return

        selected_indices = [i for i in self.func_list.curselection()]

        for idx in selected_indices:
            if idx == 0:
                self.count_rows()
            elif idx == 1:
                self.show_first_n()
            elif idx == 2:
                self.search_in_rows()
            elif idx == 3:
                self.save_selected_columns()
            elif idx == 4:
                self.change_encoding()
            elif idx == 5:
                self.remove_duplicates()
            elif idx == 6:
                self.group_by_column()
            elif idx == 7:
                self.split_and_zip()

    # --- ФУНКЦИИ-МЕТОДЫ (адаптированы под GUI) ---

    def count_rows(self):
        messagebox.showinfo("Результат", f"Количество строк данных: {len(self.rows)}")

    def show_first_n(self):
        def go():
            try:
                n = int(entry.get())
                if n <= 0:
                    raise ValueError
                top = tk.Toplevel(self.root)
                top.title("Первые строки")
                text = tk.Text(top, wrap=tk.NONE)
                text.pack(fill=tk.BOTH, expand=True)
                text.insert(tk.END, "\t".join(self.headers) + "\n")
                for row in self.rows[:n]:
                    text.insert(tk.END, "\t".join(row) + "\n")
                close = tk.Button(top, text="Закрыть", command=top.destroy)
                close.pack(pady=5)
                win.destroy()
            except:
                messagebox.showerror("Ошибка", "Введите положительное число.")

        win = tk.Toplevel(self.root)
        win.title("Сколько строк?")
        tk.Label(win, text="Сколько первых строк показать?").pack(pady=10)
        entry = tk.Entry(win)
        entry.pack(pady=5)
        tk.Button(win, text="Показать", command=go).pack(pady=10)

    def search_in_rows(self):
        query = tk.simpledialog.askstring("Поиск", "Введите строку для поиска:")
        if not query:
            return
        query = query.lower()
        matches = [row for row in self.rows if any(query in cell.lower() for cell in row)]
        if matches:
            top = tk.Toplevel(self.root)
            top.title(f"Найдено: {len(matches)}")
            text = tk.Text(top, wrap=tk.NONE)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert(tk.END, "\t".join(self.headers) + "\n")
            for match in matches:
                text.insert(tk.END, "\t".join(match) + "\n")
        else:
            messagebox.showinfo("Результат", "Ничего не найдено.")

    def save_selected_columns(self):
        cols = [f"{i}: {h}" for i, h in enumerate(self.headers)]
        selected = tk.simpledialog.askstring(
            "Столбцы", f"Введите номера столбцов через запятую:\n" + "\n".join(cols)
        )
        if not selected:
            return
        try:
            indices = [int(x.strip()) for x in selected.split(',')]
            col_names = [self.headers[i] for i in indices]
            rows_out = [[row[i] for i in indices] for row in self.rows]
            file_out = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if file_out and write_csv(file_out, col_names, rows_out):
                messagebox.showinfo("Готово", f"Сохранено в:\n{file_out}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def change_encoding(self):
        enc = tk.simpledialog.askstring("Кодировка", "В какую кодировку? (utf-8 / cp1251)")
        if enc not in ['utf-8', 'cp1251']:
            messagebox.showerror("Ошибка", "Только utf-8 или cp1251")
            return
        file_out = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if file_out and write_csv(file_out, self.headers, self.rows, encoding=enc):
            messagebox.showinfo("Готово", f"Кодировка изменена → {enc}")

    def remove_duplicates(self):
        unique_rows = []
        seen = set()
        for row in self.rows:
            key = tuple(row)
            if key not in seen:
                seen.add(key)
                unique_rows.append(row)
        if len(unique_rows) < len(self.rows):
            self.rows = unique_rows
            messagebox.showinfo("Дубли", f"Удалено: {len(self.rows) - len(unique_rows)} строк")
        else:
            messagebox.showinfo("Дубли", "Дублей не найдено")

    def group_by_column(self):
        col_name = tk.simpledialog.askstring("Свод", f"Столбец?\nДоступно: {', '.join(self.headers)}")
        if col_name not in self.headers:
            messagebox.showerror("Ошибка", "Неверное имя столбца")
            return
        idx = self.headers.index(col_name)
        count_dict = {}
        for row in self.rows:
            key = row[idx].strip()
            count_dict[key] = count_dict.get(key, 0) + 1

        result = [["Значение", "Количество"]] + [[k, str(v)] for k, v in sorted(count_dict.items())]

        text = "\n".join(f"{k}\t{v}" for k, v in sorted(count_dict.items()))
        top = tk.Toplevel(self.root)
        top.title("Свод")
        tk.Label(top, text=f"Свод по '{col_name}'", font=("bold")).pack(pady=5)
        text_widget = tk.Text(top, wrap=tk.NONE)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, "Значение\tКоличество\n")
        text_widget.insert(tk.END, text)
        save_btn = tk.Button(top, text="💾 Сохранить в CSV", command=lambda: self.save_if_needed(result))
        save_btn.pack(pady=5)

    def save_if_needed(self, data):
        file_out = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if file_out:
            try:
                with open(file_out, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(data)
                messagebox.showinfo("Готово", f"Сохранено: {file_out}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def split_and_zip(self):
        try:
            n = int(tk.simpledialog.askstring("Разделение", "Строк в части?"))
            base_name = tk.simpledialog.askstring("Имя", "Базовое имя частей?", initialvalue="part")
            zip_name = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP", "*.zip")])
            if not zip_name:
                return

            temp_dir = "temp_split_parts"
            os.makedirs(temp_dir, exist_ok=True)
            parts = []

            for i in range(0, len(self.rows), n):
                chunk = self.rows[i:i+n]
                filename = f"{base_name}_{i//n + 1}.csv"
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.headers)
                    writer.writerows(chunk)
                parts.append(filepath)

            with zipfile.ZipFile(zip_name, 'w') as z:
                for file in parts:
                    z.write(file, os.path.basename(file))

            for file in parts:
                os.remove(file)
            os.rmdir(temp_dir)

            messagebox.showinfo("Готово", f"Части упакованы в:\n{zip_name}")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


# --- ЗАПУСК ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVToolApp(root)
    root.mainloop()