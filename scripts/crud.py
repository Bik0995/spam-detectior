"""
CRUD windows for senders and messages dictionaries (Russian interface).
Author: A. B. Pascal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from library.helpers import load_pickle, save_pickle, load_config, apply_styles, get_data_path

current_df = None
tree = None
filepath = None


def refresh_tree():
    """Clear and repopulate the Treeview with current_df."""
    for item in tree.get_children():
        tree.delete(item)
    if current_df is not None:
        for _, row in current_df.iterrows():
            tree.insert('', 'end', values=list(row))


def load_dataframe(path: str):
    """Load a pickle file into current_df and display it (uses absolute path)."""
    global current_df, filepath
    # The path is something like "data/senders.pkl" – extract filename and get absolute path
    filename = os.path.basename(path)
    filepath = get_data_path(filename)
    current_df = load_pickle(filepath)
    refresh_tree()


def save_dataframe():
    """Save current_df back to its pickle file."""
    if filepath and current_df is not None:
        save_pickle(current_df, filepath)
        messagebox.showinfo("Сохранено", f"Данные сохранены в {filepath}")
    else:
        messagebox.showerror("Ошибка", "Нет данных для сохранения")


def add_record():
    """Open a dialog to add a new record."""
    global current_df
    if current_df is None:
        return
    if 'sender_id' in current_df.columns:
        fields = ['sender_id', 'sender_type', 'country', 'trusted', 'activity']
    else:
        fields = ['message_id', 'sender_id', 'text', 'length', 'word_count',
                  'has_link', 'has_phone', 'has_exclamation', 'all_caps',
                  'keyword_count', 'spam_score', 'category']

    dialog = tk.Toplevel()
    dialog.title("Добавить запись")
    dialog.geometry("400x400")
    config = load_config()
    apply_styles(dialog, config)

    entries = {}
    for i, field in enumerate(fields):
        ttk.Label(dialog, text=field).grid(row=i, column=0, padx=5, pady=5, sticky='e')
        var = tk.StringVar()
        ttk.Entry(dialog, textvariable=var).grid(row=i, column=1, padx=5, pady=5)
        entries[field] = var

    def submit():
        global current_df
        new_row = {field: var.get() for field, var in entries.items()}
        id_field = fields[0]
        if new_row[id_field] in current_df[id_field].values:
            messagebox.showerror("Ошибка", f"Запись с таким {id_field} уже существует!")
            return
        new_df = pd.DataFrame([new_row])
        for col in ['activity', 'length', 'word_count', 'keyword_count', 'spam_score']:
            if col in new_df.columns:
                new_df[col] = pd.to_numeric(new_df[col], errors='coerce').fillna(0).astype(int)
        current_df = pd.concat([current_df, new_df], ignore_index=True)
        refresh_tree()
        dialog.destroy()

    ttk.Button(dialog, text="Добавить", command=submit).grid(row=len(fields), columnspan=2, pady=15)


def edit_record():
    """Open a dialog to edit the selected record."""
    global current_df
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Предупреждение", "Выберите запись для редактирования")
        return
    item = tree.item(selected[0])
    values = item['values']
    id_col = current_df.columns[0]
    idx = current_df[current_df[id_col] == values[0]].index[0]
    row = current_df.iloc[idx]
    fields = list(current_df.columns)

    dialog = tk.Toplevel()
    dialog.title("Редактировать запись")
    dialog.geometry("400x400")
    config = load_config()
    apply_styles(dialog, config)

    entries = {}
    for i, field in enumerate(fields):
        ttk.Label(dialog, text=field).grid(row=i, column=0, padx=5, pady=5, sticky='e')
        var = tk.StringVar(value=str(row[field]))
        ttk.Entry(dialog, textvariable=var).grid(row=i, column=1, padx=5, pady=5)
        entries[field] = var

    def submit():
        new_vals = {field: var.get() for field, var in entries.items()}
        for col in ['activity', 'length', 'word_count', 'keyword_count', 'spam_score']:
            if col in current_df.columns:
                try:
                    new_vals[col] = int(new_vals[col])
                except ValueError:
                    new_vals[col] = 0
        current_df.loc[idx] = new_vals
        refresh_tree()
        dialog.destroy()

    ttk.Button(dialog, text="Сохранить", command=submit).grid(row=len(fields), columnspan=2, pady=15)


def delete_record():
    """Delete the selected record."""
    global current_df
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
        return
    item = tree.item(selected[0])
    id_val = item['values'][0]
    id_col = current_df.columns[0]
    current_df = current_df[current_df[id_col] != id_val]
    refresh_tree()
    messagebox.showinfo("Удалено", "Запись удалена.")


def create_crud_window(root, title, path):
    """
    Create a Toplevel window for viewing/editing a dictionary.
    """
    global current_df, tree, filepath
    window = tk.Toplevel(root)
    window.title(title)
    window.geometry("900x500")
    config = load_config()
    apply_styles(window, config)

    # Build the Treeview and assign to global tree FIRST
    tree_frame = ttk.Frame(window)
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree = ttk.Treeview(tree_frame)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    # Now load data using the provided path
    load_dataframe(path)

    # Buttons frame
    btn_frame = ttk.Frame(window)
    btn_frame.pack(side=tk.TOP, fill=tk.X, pady=5, padx=10)

    ttk.Button(btn_frame, text="Добавить", command=add_record).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Редактировать", command=edit_record).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Удалить", command=delete_record).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Сохранить в файл", command=save_dataframe).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Обновить", command=refresh_tree).pack(side=tk.LEFT, padx=5)

    # Configure columns after data is loaded
    if current_df is not None:
        tree["columns"] = list(current_df.columns)
        tree["show"] = "headings"
        for col in current_df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

    refresh_tree()