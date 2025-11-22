# -*- coding: utf-8 -*-
"""
GUI версия LBKI CSV: Графический интерфейс.
Операции выполняются последовательно на одном наборе данных.
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog, Listbox, Scrollbar, END, simpledialog, Text, ttk
from lbki_csv import *

class LogWindow:
    """Окно логирования"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Лог операций")
        self.window.geometry("600x300")
        
        # Текстовое поле для логов
        self.text = Text(self.window, wrap=tk.WORD, font=("Courier", 9), bg="#f5f5f5")
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Кнопка очистки
        tk.Button(self.window, text="Очистить лог", command=self.clear).pack(pady=5)
    
    def log(self, message, level="INFO"):
        """Добавляет сообщение в лог"""
        # Определяем цвет по ур��вню
        if level == "ERROR":
            prefix = "❌ "
            color = "red"
        elif level == "WARNING":
            prefix = "⚠️  "
            color = "orange"
        elif level == "SUCCESS":
            prefix = "✓ "
            color = "green"
        else:
            prefix = "ℹ️  "
            color = "black"
        
        # Добавляем текст
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, f"{prefix}{message}\n")
        self.text.tag_config(level, foreground=color)
        self.text.tag_add(level, f"end-{len(prefix)+len(message)+1}c", "end-1c")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)
        self.window.update()
    
    def clear(self):
        """Очищает лог"""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)

class LBKICSVApp:
    DELIMITERS = {
        "Запятая (,)": ",",
        "Точка с запятой (;)": ";",
        "Табуляция (\\t)": "\t",
        "Пробел ( )": " ",
        "Двоеточие (:)": ":",
        "Автоопределение": None
    }
    
    def __init__(self, root, file_path=None, delimiter=None):
        self.root = root
        self.root.title("LBKI CSV — GUI")
        self.root.geometry("750x600")

        self.file_path = None
        self.original_headers = None
        self.original_rows = None
        self.current_headers = None
        self.current_rows = None
        self.encoding = 'utf-8'
        self.delimiter = delimiter  # Пользовательский разделитель
        self.detected_delimiter = ','  # Автоопределённый разделитель
        
        # Создаём окно логирования
        self.log_window = LogWindow(self.root)

        self.setup_ui()
        
        # Загружаем файл из argv если передан
        if file_path:
            self.load_file_from_path(file_path)

    def setup_ui(self):
        # Заголовок
        tk.Label(self.root, text="LBKI CSV", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Метка для отображения имени файла
        self.file_label = tk.Label(self.root, text="", font=("Arial", 10), fg="#1976D2")
        self.file_label.pack(pady=5)
        
        # Фрейм для кнопок и выбора разделителя
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        
        # Кнопка открытия файла
        tk.Button(button_frame, text="📂 Открыть CSV", command=self.load_file,
                  bg="#4CAF50", fg="white", width=20).pack(side=tk.LEFT, padx=5)
        
        # Выбор разделителя
        tk.Label(button_frame, text="Разделитель:").pack(side=tk.LEFT, padx=5)
        self.delimiter_var = tk.StringVar(value="Автоопределение")
        delimiter_combo = ttk.Combobox(button_frame, textvariable=self.delimiter_var, 
                                       values=list(self.DELIMITERS.keys()), state="readonly", width=20)
        delimiter_combo.pack(side=tk.LEFT, padx=5)

        # Информация о данных
        self.info = tk.Label(self.root, text="Файл не загружен", fg="gray")
        self.info.pack(pady=5)

        # Список функций
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = Listbox(frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, height=10)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        funcs = [
            "1. Подсчитать строки",
            "2. Показать первые N",
            "3. Фильтр по тексту",
            "4. Выбрать столбцы",
            "5. Удалить дубли",
            "6. Свод по столбцу",
            "7. Разделить в ZIP",
            "8. Сохранить результат",
            "9. Сбросить к исходным"
        ]
        for f in funcs:
            self.listbox.insert(END, f)

        # Кнопка выполнения
        tk.Button(self.root, text="▶ Выполнить", command=self.run_selected,
                  bg="#2196F3", fg="white").pack(pady=10)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
        if not path: return
        self.load_file_from_path(path)

    def load_file_from_path(self, path):
        """Загружает файл по указанному пути"""
        if not os.path.isfile(path):
            self.log_window.log(f"Файл не найден: {path}", "ERROR")
            return
        
        self.file_path = path
        
        # Получаем разделитель из dropdown или используем переданный
        delimiter_name = self.delimiter_var.get()
        delimiter = self.DELIMITERS.get(delimiter_name)
        
        headers, rows, encoding, detected_delim = read_csv(path, delimiter)
        if headers is None:
            self.log_window.log("Не удалось прочитать файл", "ERROR")
            return
        
        # Сохраняем исходные данные
        self.original_headers = headers
        self.original_rows = rows
        self.current_headers = headers
        self.current_rows = rows
        self.encoding = encoding or 'utf-8'
        self.detected_delimiter = detected_delim
        
        # Получаем имя файла
        file_name = os.path.basename(path)
        
        # Обновляем заголовок окна
        self.root.title(f"LBKI CSV — {file_name}")
        
        # Обновляем метку с именем файла
        self.file_label.config(text=f"📄 {file_name}")
        
        # Обновляем информацию о загруженных данных
        self.update_info()
        self.listbox.config(state=tk.NORMAL)
        
        # Логируем
        delim_display = repr(detected_delim) if detected_delim else "автоопределение"
        self.log_window.log(f"Файл загружен: {file_name}", "SUCCESS")
        self.log_window.log(f"Кодировка: {encoding}, Разделитель: {delim_display}", "INFO")
        self.log_window.log(f"Данные: {len(headers)} столбцов, {len(rows)} строк", "INFO")

    def update_info(self):
        """Обновляет информацию о текущих данных"""
        if self.current_headers:
            self.info.config(
                text=f"Текущие данные: {len(self.current_headers)} колонок, {len(self.current_rows)} строк",
                fg="black"
            )
        else:
            self.info.config(text="Файл не загружен", fg="gray")

    def run_selected(self):
        if not self.current_headers:
            self.log_window.log("Сначала загрузите файл", "WARNING")
            return
        
        sel = self.listbox.curselection()
        if not sel:
            self.log_window.log("Выберите действие", "WARNING")
            return

        # Выполняем операции последовательно
        for i in sel:
            if i == 0:  # Подсчитать строки
                cnt, cols = count_rows(self.current_headers, self.current_rows)
                self.log_window.log(f"Подсчёт: {cnt} строк, {cols} столбцов", "INFO")
                self.show_data_window(f"Результат: {cnt} строк, {cols} столбцов", 
                                     ["Метрика", "Значение"],
                                     [["Строк", str(cnt)], ["Столбцов", str(cols)]])
            
            elif i == 1:  # Показать первые N
                n = simpledialog.askinteger("N", "Сколько строк?")
                if n and n > 0:
                    h, r = get_first_n(self.current_headers, self.current_rows, n)
                    self.log_window.log(f"Показаны первые {n} строк", "INFO")
                    self.show_data_window(f"Первые {n} строк", h, r)
            
            elif i == 2:  # Фильтр по тексту
                q = simpledialog.askstring("Фильтр", "Текст для фильтра:")
                if q:
                    h, filtered = filter_by_text(self.current_headers, self.current_rows, q)
                    filtered_count = len(filtered)
                    self.current_headers = h
                    self.current_rows = filtered
                    self.update_info()
                    self.log_window.log(f"Фильтр применён: '{q}' → {filtered_count} строк", "SUCCESS")
                    self.show_data_window(f"Отфильтровано: {filtered_count} строк", h, filtered)
            
            elif i == 3:  # Выбрать столбцы
                cols = simpledialog.askstring("Столбцы", f"Через запятую:\n{', '.join(self.current_headers)}")
                if cols:
                    names = [c.strip() for c in cols.split(',')]
                    h, r = select_columns(self.current_headers, self.current_rows, names)
                    if h:
                        self.current_headers = h
                        self.current_rows = r
                        self.update_info()
                        self.log_window.log(f"Столбцы выбраны: {', '.join(h)}", "SUCCESS")
                    else:
                        self.log_window.log(f"Ошибка: неверные столбцы", "ERROR")
            
            elif i == 4:  # Удалить дубли
                h, r = remove_duplicates(self.current_headers, self.current_rows)
                deleted = len(self.current_rows) - len(r)
                self.current_headers = h
                self.current_rows = r
                self.update_info()
                self.log_window.log(f"Дубли удалены: {deleted} строк удалено", "SUCCESS")
            
            elif i == 5:  # Свод по столбцу
                col = simpledialog.askstring("Свод", f"Столбец?\n{', '.join(self.current_headers)}")
                if col:
                    h, r = group_by_column(self.current_headers, self.current_rows, col)
                    if h:
                        self.current_headers = h
                        self.current_rows = r
                        self.update_info()
                        self.log_window.log(f"Свод по столбцу '{col}' выполнен", "SUCCESS")
                        self.show_data_window(f"Свод по '{col}'", h, r)
                    else:
                        self.log_window.log(f"Ошибка: столбец '{col}' не найден", "ERROR")
            
            elif i == 6:  # Разделить в ZIP
                n = simpledialog.askinteger("Разделение", "Строк в части?")
                if n and n > 0:
                    base = simpledialog.askstring("Имя", "Базовое имя?", initialvalue="part")
                    zip_name = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP", "*.zip")])
                    if zip_name:
                        h, chunks = split_into_chunks(self.current_headers, self.current_rows, n)
                        if zip_chunks(chunks, h, base, zip_name):
                            self.log_window.log(f"ZIP создан: {zip_name} ({len(chunks)} частей)", "SUCCESS")
                        else:
                            self.log_window.log("Ошибка при создании ZIP", "ERROR")
            
            elif i == 7:  # Сохранить результат
                if not self.current_headers:
                    self.log_window.log("Нет данных для сохранения", "WARNING")
                    return
                
                # Диалог выбора разделителя для сохранения
                save_delim = self.show_delimiter_dialog()
                if save_delim is None:
                    return
                
                file_out = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv"), ("All files", "*.*")])
                if file_out:
                    if write_csv(file_out, self.current_headers, self.current_rows, self.encoding, save_delim):
                        delim_display = repr(save_delim)
                        self.log_window.log(f"Файл сохранён: {file_out} (разделитель: {delim_display})", "SUCCESS")
                    else:
                        self.log_window.log("Ошибка при сохранении файла", "ERROR")
            
            elif i == 8:  # Сбросить к исходным
                self.current_headers = self.original_headers
                self.current_rows = self.original_rows
                self.update_info()
                self.log_window.log("Данные сброшены к исходным", "INFO")

    def show_delimiter_dialog(self):
        """Показывает диалог выбора разделителя для сохранения"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Выбор разделителя")
        dialog.geometry("300x220")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Выберите разделитель для сохранения:", font=("Arial", 10)).pack(pady=10)
        
        delimiter_var = tk.StringVar(value="Запятая (,)")
        for delim_name in self.DELIMITERS.keys():
            if delim_name != "Автоопределение":
                tk.Radiobutton(dialog, text=delim_name, variable=delimiter_var, value=delim_name).pack(anchor=tk.W, padx=20)
        
        result = [None]
        
        def ok():
            delim_name = delimiter_var.get()
            result[0] = self.DELIMITERS[delim_name]
            dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="OK", command=ok, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Отмена", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        self.root.wait_window(dialog)
        return result[0]

    def show_data_window(self, title, headers, rows):
        """Показывает данные в отдельном окне"""
        top = tk.Toplevel(self.root)
        top.title(title)
        top.geometry("600x400")
        
        text = tk.Text(top, wrap=tk.NONE, font=("Courier", 9))
        text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Добавляем заголовки
        text.insert(tk.END, "\t".join(headers) + "\n")
        text.insert(tk.END, "-" * 80 + "\n")
        
        # Добавляем строки
        for row in rows:
            text.insert(tk.END, "\t".join(str(cell) for cell in row) + "\n")
        
        text.config(state=tk.DISABLED)
        
        # Кнопка закрытия
        tk.Button(top, text="Закрыть", command=top.destroy).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Проверяем, передан ли файл в argv
    file_path = None
    delimiter = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    if len(sys.argv) > 2:
        # Второй аргумент - разделитель
        delim_arg = sys.argv[2]
        if delim_arg == "comma":
            delimiter = ","
        elif delim_arg == "semicolon":
            delimiter = ";"
        elif delim_arg == "tab":
            delimiter = "\t"
        elif delim_arg == "space":
            delimiter = " "
        elif delim_arg == "colon":
            delimiter = ":"
    
    app = LBKICSVApp(root, file_path, delimiter)
    root.mainloop()
