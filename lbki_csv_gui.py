# -*- coding: utf-8 -*-
"""
GUI версия LBKI CSV: Графический интерфейсв окне.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, END, simpledialog
from lbki_csv import *

class CSVToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LBKI CSV — GUI")
        self.root.geometry("700x500")

        self.file_path = None
        self.headers = None
        self.rows = None

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="LBKI CSV", font=("Arial", 16, "bold")).pack(pady=10)
        tk.Button(self.root, text="📂 Открыть CSV", command=self.load_file,
                  bg="#4CAF50", fg="white", width=30).pack(pady=5)

        self.info = tk.Label(self.root, text="Файл не загружен", fg="gray")
        self.info.pack(pady=5)

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = Listbox(frame, yscrollcommand=scrollbar.set, selectmode=tk.MULTIPLE, height=10)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        funcs = [
            "1. Подсчитать строки",
            "2. Показать первые N",
            "3. Поиск по тексту",
            "4. Выбрать столбцы",
            "5. Удалить дубли",
            "6. Свод по столбцу",
            "7. Разделить в ZIP"
        ]
        for f in funcs:
            self.listbox.insert(END, f)

        tk.Button(self.root, text="▶ Выполнить", command=self.run_selected,
                  bg="#2196F3", fg="white").pack(pady=10)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path: return
        self.file_path = path
        self.headers, self.rows, _ = read_csv(path)
        if self.headers is None:
            messagebox.showerror("Ошибка", "Не удалось прочитать файл")
            return
        self.info.config(text=f"Загружено: {len(self.headers)} колонок, {len(self.rows)} строк")
        self.listbox.config(state=tk.NORMAL)

    def run_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("!", "Выберите действие")
            return

        for i in sel:
            if i == 0:
                cnt, cols = count_rows(self.headers, self.rows)
                messagebox.showinfo("Результат", f"Строк: {cnt}\nСтолбцов: {cols}")
            elif i == 1:
                n = simpledialog.askinteger("N", "Сколько строк?")
                if n:
                    h, r = get_first_n(self.headers, self.rows, n)
                    top = tk.Toplevel()
                    txt = tk.Text(top, height=15)
                    txt.pack()
                    txt.insert(tk.END, "\t".join(h) + "\n")
                    for row in r: txt.insert(tk.END, "\t".join(row) + "\n")
            elif i == 2:
                q = simpledialog.askstring("Поиск", "Текст:")
                if q:
                    h, matches = search_in_rows(self.headers, self.rows, q)
                    top = tk.Toplevel()
                    txt = tk.Text(top, height=15)
                    txt.pack()
                    txt.insert(tk.END, f"Найдено: {len(matches)}\n")
                    txt.insert(tk.END, "\t".join(h) + "\n")
                    for m in matches: txt.insert(tk.END, "\t".join(m) + "\n")
            elif i == 3:
                cols = simpledialog.askstring("Столбцы", f"Через запятую:\n{', '.join(self.headers)}")
                if cols:
                    names = [c.strip() for c in cols.split(',')]
                    h, r = select_columns(self.headers, self.rows, names)
                    if h: file = filedialog.asksaveasfilename(defaultextension=".csv"); write_csv(file, h, r); messagebox.showinfo("Готово", f"Сохранено")
            elif i == 4:
                self.headers, self.rows = remove_duplicates(self.headers, self.rows)
                messagebox.showinfo("Готово", "Дубли удалены")
            elif i == 5:
                col = simpledialog.askstring("Свод", f"Столбец?\n{', '.join(self.headers)}")
                if col:
                    h, r = group_by_column(self.headers, self.rows, col)
                    if h: file = filedialog.asksaveasfilename(defaultextension=".csv"); write_csv(file, h, r); messagebox.showinfo("Готово", "Свод сохранён")
            elif i == 6:
                n = simpledialog.askinteger("Разделение", "Строк в части?")
                if n:
                    base = simpledialog.askstring("Имя", "Базовое имя?", initialvalue="part")
                    zip_name = filedialog.asksaveasfilename(defaultextension=".zip")
                    if zip_name:
                        h, chunks = split_into_chunks(self.headers, self.rows, n)
                        if zip_chunks(chunks, h, base, zip_name):
                            messagebox.showinfo("Готово", f"ZIP создан: {zip_name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVToolApp(root)
    root.mainloop()