"""
Main GUI for the Spam Detection application (Russian interface).
Author: A. B. Pascal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
from library.helpers import load_config, save_config, apply_styles, get_font
from scripts.reports import generate_all_reports
from scripts.crud import create_crud_window
from scripts.classifier import score_message


def classify_single_message():
    """Open window to classify a user-provided message."""
    config = load_config()
    keywords = [kw.strip() for kw in config['Classifier']['keywords'].split(',')]
    threshold = config.getint('Classifier', 'threshold')
    font = get_font(config)

    win = tk.Toplevel()
    win.title("Классификация сообщения")
    win.geometry("600x400")
    apply_styles(win, config)

    def check():
        text = entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Пустое сообщение", "Введите текст сообщения.")
            return
        score = score_message(text, keywords)
        result = "СПАМ" if score >= threshold else "НЕ СПАМ"
        label_result.config(text=f"Оценка: {score}\nРезультат: {result}")

    ttk.Label(win, text="Введите текст сообщения:").pack(pady=10)
    entry = tk.Text(win, height=10, width=50, font=font)
    entry.pack(pady=5, padx=20, fill=tk.BOTH, expand=True)
    ttk.Button(win, text="Проверить", command=check).pack(pady=10)
    label_result = ttk.Label(win, text="", font=(font[0], 12))
    label_result.pack(pady=10)


def settings_window():
    """Settings dialog for threshold and keywords."""
    config = load_config()
    win = tk.Toplevel()
    win.title("Настройки")
    win.geometry("500x200")
    apply_styles(win, config)

    row = 0
    ttk.Label(win, text="Порог классификации").grid(row=row, column=0, sticky='e', padx=5, pady=10)
    threshold_var = tk.StringVar(value=config['Classifier']['threshold'])
    ttk.Entry(win, textvariable=threshold_var, width=10).grid(row=row, column=1, padx=5, pady=10)
    row += 1
    ttk.Label(win, text="Ключевые слова (через запятую)").grid(row=row, column=0, sticky='e', padx=5, pady=10)
    keywords_var = tk.StringVar(value=config['Classifier']['keywords'])
    ttk.Entry(win, textvariable=keywords_var, width=40).grid(row=row, column=1, padx=5, pady=10)
    row += 1

    def save():
        config['Classifier']['threshold'] = threshold_var.get()
        config['Classifier']['keywords'] = keywords_var.get()
        save_config(config)
        messagebox.showinfo("Сохранено", "Настройки сохранены.")
        win.destroy()

    ttk.Button(win, text="Сохранить", command=save).grid(row=row, columnspan=2, pady=20)


def generate_reports_with_feedback():
    """Generate reports and show a confirmation or error message."""
    try:
        generate_all_reports()
        messagebox.showinfo("Готово", "Все отчёты сформированы.\nПроверьте папки output/ и graphics/.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сформировать отчёты:\n{str(e)}")


def main_gui():
    """Create the main application window."""
    config = load_config()
    root = tk.Tk()
    root.title("Обнаружение спам-сообщений")
    try:
        w, h = config['Interface']['window_size'].split('x')
        root.geometry(f"{w}x{h}")
    except Exception:
        root.geometry("900x700")

    apply_styles(root, config)
    font = get_font(config)
    big_font = (font[0], 16, 'bold')
    small_font = (font[0], 11)

    # Menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    dict_menu = tk.Menu(menubar, tearoff=0)
    dict_menu.add_command(label="Отправители",
                          command=lambda: create_crud_window(root, "Справочник отправителей", "data/senders.pkl"))
    dict_menu.add_command(label="Сообщения",
                          command=lambda: create_crud_window(root, "Справочник сообщений", "data/messages.pkl"))
    menubar.add_cascade(label="Справочники", menu=dict_menu)

    report_menu = tk.Menu(menubar, tearoff=0)
    report_menu.add_command(label="Сформировать все отчёты", command=generate_reports_with_feedback)
    menubar.add_cascade(label="Отчёты", menu=report_menu)

    class_menu = tk.Menu(menubar, tearoff=0)
    class_menu.add_command(label="Проверить сообщение", command=classify_single_message)
    menubar.add_cascade(label="Классификатор", menu=class_menu)

    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(label="Настройки", command=settings_window)
    menubar.add_cascade(label="Настройки", menu=settings_menu)

    # Main frame with welcome text
    main_frame = ttk.Frame(root, padding=30)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame,
              text="Информационно-аналитическое приложение «Обнаружение спам-сообщений»",
              font=big_font).pack(pady=30)

    ttk.Label(main_frame,
              text="Группа: БИВ255\nРазработчики: Амана Бикиливе Паскаль, Мохамед Мохамед Нурхуссен",
              font=small_font).pack(pady=20)

    # Quick actions frame
    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=40)

    ttk.Button(btn_frame, text="📊 Сформировать все отчёты",
               command=generate_reports_with_feedback).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="🔍 Проверить сообщение",
               command=classify_single_message).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="⚙️ Настройки",
               command=settings_window).pack(side=tk.LEFT, padx=10)

    root.mainloop()


if __name__ == "__main__":
    main_gui()