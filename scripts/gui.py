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
from scripts.reports import generate_all_reports, get_data
from scripts.crud import create_crud_window
from scripts.classifier import score_message

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


def classify_single_message():
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
    try:
        generate_all_reports()
        messagebox.showinfo("Готово", "Все отчёты сформированы.\nПроверьте папки output/ и graphics/.")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось сформировать отчёты:\n{str(e)}")


def show_graphs_window():
    config = load_config()
    win = tk.Toplevel()
    win.title("Графические отчёты")
    win.geometry("900x700")
    apply_styles(win, config)

    df = get_data()

    notebook = ttk.Notebook(win)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # 1. Bar chart
    fig1 = Figure(figsize=(8, 5), dpi=100)
    ax1 = fig1.add_subplot(111)
    spam_df = df[df['category'] == 'спам']
    counts = spam_df.groupby('sender_type').size()
    types = ['личный', 'служебный', 'рекламный', 'неизвестный']
    counts = counts.reindex(types, fill_value=0)
    counts.plot(kind='bar', color='salmon', ax=ax1)
    ax1.set_title('Количество спама по типам отправителей')
    ax1.set_xlabel('Тип отправителя')
    ax1.set_ylabel('Количество')
    fig1.tight_layout()
    canvas1 = FigureCanvasTkAgg(fig1, master=notebook)
    canvas1.draw()
    notebook.add(canvas1.get_tk_widget(), text="Столбчатая диаграмма")

    # 2. Histogram
    fig2 = Figure(figsize=(8, 5), dpi=100)
    ax2 = fig2.add_subplot(111)
    spam_lengths = df[df['category'] == 'спам']['length']
    ham_lengths = df[df['category'] == 'не спам']['length']
    ax2.hist(spam_lengths, bins=30, alpha=0.7, label='Спам', color='red')
    ax2.hist(ham_lengths, bins=30, alpha=0.7, label='Не спам', color='blue')
    ax2.set_title('Распределение длины сообщений')
    ax2.set_xlabel('Длина (символы)')
    ax2.set_ylabel('Частота')
    ax2.legend()
    fig2.tight_layout()
    canvas2 = FigureCanvasTkAgg(fig2, master=notebook)
    canvas2.draw()
    notebook.add(canvas2.get_tk_widget(), text="Гистограмма")

    # 3. Box plot
    fig3 = Figure(figsize=(8, 5), dpi=100)
    ax3 = fig3.add_subplot(111)
    data = [df[df['category'] == 'спам']['keyword_count'],
            df[df['category'] == 'не спам']['keyword_count']]
    ax3.boxplot(data, tick_labels=['Спам', 'Не спам'])
    ax3.set_title('Количество ключевых слов по категориям')
    ax3.set_ylabel('Количество ключевых слов')
    fig3.tight_layout()
    canvas3 = FigureCanvasTkAgg(fig3, master=notebook)
    canvas3.draw()
    notebook.add(canvas3.get_tk_widget(), text="Ящик с усами")

    # 4. Scatter plot
    fig4 = Figure(figsize=(8, 5), dpi=100)
    ax4 = fig4.add_subplot(111)
    spam = df[df['category'] == 'спам']
    ham = df[df['category'] == 'не спам']
    ax4.scatter(spam['length'], spam['keyword_count'], c='red', alpha=0.6, label='Спам')
    ax4.scatter(ham['length'], ham['keyword_count'], c='blue', alpha=0.6, label='Не спам')
    ax4.set_title('Длина сообщения vs количество ключевых слов')
    ax4.set_xlabel('Длина')
    ax4.set_ylabel('Ключевых слов')
    ax4.legend()
    fig4.tight_layout()
    canvas4 = FigureCanvasTkAgg(fig4, master=notebook)
    canvas4.draw()
    notebook.add(canvas4.get_tk_widget(), text="Диаграмма рассеяния")

    ttk.Button(win, text="Закрыть", command=win.destroy).pack(pady=10)


def main_gui():
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
    report_menu.add_command(label="Показать графики", command=show_graphs_window)
    menubar.add_cascade(label="Отчёты", menu=report_menu)

    class_menu = tk.Menu(menubar, tearoff=0)
    class_menu.add_command(label="Проверить сообщение", command=classify_single_message)
    menubar.add_cascade(label="Классификатор", menu=class_menu)

    settings_menu = tk.Menu(menubar, tearoff=0)
    settings_menu.add_command(label="Настройки", command=settings_window)
    menubar.add_cascade(label="Настройки", menu=settings_menu)

    main_frame = ttk.Frame(root, padding=30)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame,
              text="Информационно-аналитическое приложение «Обнаружение спам-сообщений»",
              font=big_font).pack(pady=30)

    ttk.Label(main_frame,
              text="Группа: БИВ255\nРазработчики: Амана Бикиливе Паскаль, Мохамед Мохамед Нурхуссен",
              font=small_font).pack(pady=20)

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(pady=40)

    ttk.Button(btn_frame, text="📊 Сформировать все отчёты",
               command=generate_reports_with_feedback).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="📈 Показать графики",
               command=show_graphs_window).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="🔍 Проверить сообщение",
               command=classify_single_message).pack(side=tk.LEFT, padx=10)
    ttk.Button(btn_frame, text="⚙️ Настройки",
               command=settings_window).pack(side=tk.LEFT, padx=10)

    root.mainloop()


if __name__ == "__main__":
    main_gui()