"""
Generation of 7 analytical reports (Russian titles).
Author: M. M. Nurhussein
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from library.helpers import load_config, load_pickle

plt.rcParams['font.family'] = 'DejaVu Sans'


def get_data():
    """Merge messages and senders into one DataFrame."""
    messages = load_pickle("data/messages.pkl")
    senders = load_pickle("data/senders.pkl")
    return messages.merge(senders, on='sender_id', how='left')


def report1_high_spam_list(output_dir: str, threshold: int):
    df = get_data()
    high = df[df['spam_score'] > threshold][['message_id', 'text', 'spam_score']]
    path = os.path.join(output_dir, "report1_high_spam.csv")
    high.to_csv(path, index=False)


def report2_statistics(output_dir: str):
    df = get_data()
    qual_cols = ['sender_type', 'country', 'trusted', 'has_link', 'has_phone',
                 'has_exclamation', 'all_caps']
    quant_cols = ['length', 'word_count', 'keyword_count', 'spam_score']
    with open(os.path.join(output_dir, "report2_statistics.txt"), 'w', encoding='utf-8') as f:
        f.write("Статистический отчёт\n\nКачественные атрибуты:\n")
        for col in qual_cols:
            f.write(f"\n{col}:\n{df[col].value_counts().to_string()}\n")
        f.write("\nКоличественные атрибуты:\n")
        f.write(df[quant_cols].describe().to_string())


def report3_pivot_links(output_dir: str):
    df = get_data()
    crosstab = pd.crosstab(df['has_link'], df['category'], margins=True)
    crosstab.to_csv(os.path.join(output_dir, "report3_pivot.csv"))


def report4_bar_chart(graphics_dir: str):
    df = get_data()
    spam_df = df[df['category'] == 'спам']
    counts = spam_df.groupby('sender_type').size()
    types = ['личный', 'служебный', 'рекламный', 'неизвестный']
    counts = counts.reindex(types, fill_value=0)
    plt.figure()
    counts.plot(kind='bar', color='salmon')
    plt.title('Количество спама по типам отправителей')
    plt.xlabel('Тип отправителя')
    plt.ylabel('Количество')
    plt.tight_layout()
    plt.savefig(os.path.join(graphics_dir, "report4_bar.png"))
    plt.close()


def report5_histogram(graphics_dir: str):
    df = get_data()
    spam_lengths = df[df['category'] == 'спам']['length']
    ham_lengths = df[df['category'] == 'не спам']['length']
    plt.figure()
    plt.hist(spam_lengths, bins=30, alpha=0.7, label='Спам', color='red')
    plt.hist(ham_lengths, bins=30, alpha=0.7, label='Не спам', color='blue')
    plt.title('Распределение длины сообщений')
    plt.xlabel('Длина (символы)')
    plt.ylabel('Частота')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(graphics_dir, "report5_histogram.png"))
    plt.close()


def report6_boxplot(graphics_dir: str):
    df = get_data()
    data = [df[df['category'] == 'спам']['keyword_count'],
            df[df['category'] == 'не спам']['keyword_count']]
    plt.figure()
    plt.boxplot(data, tick_labels=['Спам', 'Не спам'])
    plt.title('Количество ключевых слов по категориям')
    plt.ylabel('Количество ключевых слов')
    plt.tight_layout()
    plt.savefig(os.path.join(graphics_dir, "report6_boxplot.png"))
    plt.close()


def report7_scatter(graphics_dir: str):
    df = get_data()
    spam = df[df['category'] == 'спам']
    ham = df[df['category'] == 'не спам']
    plt.figure()
    plt.scatter(spam['length'], spam['keyword_count'], c='red', alpha=0.6, label='Спам')
    plt.scatter(ham['length'], ham['keyword_count'], c='blue', alpha=0.6, label='Не спам')
    plt.title('Длина сообщения vs количество ключевых слов')
    plt.xlabel('Длина')
    plt.ylabel('Ключевых слов')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(graphics_dir, "report7_scatter.png"))
    plt.close()


def generate_all_reports():
    config = load_config()
    threshold = config.getint('Classifier', 'threshold')
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, config.get('Paths', 'output_dir', fallback='output'))
    graph_dir = os.path.join(base_dir, config.get('Paths', 'graphics_dir', fallback='graphics'))
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(graph_dir, exist_ok=True)

    report1_high_spam_list(out_dir, threshold)
    report2_statistics(out_dir)
    report3_pivot_links(out_dir)
    report4_bar_chart(graph_dir)
    report5_histogram(graph_dir)
    report6_boxplot(graph_dir)
    report7_scatter(graph_dir)
    print("Все отчёты сформированы.")


if __name__ == "__main__":
    generate_all_reports()