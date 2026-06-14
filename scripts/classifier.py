"""
Heuristic spam classifier and threshold optimization.
Author: M. M. Nurhussein
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import pandas as pd
from library.helpers import (
    load_config, load_pickle, save_pickle, save_config,
    has_url, has_phone, is_all_caps
)


def score_message(text: str, keywords: list) -> int:
    """
    Compute spam score for a single message using the heuristic rules.
    """
    score = 0
    text_lower = text.lower()
    # Each keyword occurrence adds 1 point
    for kw in keywords:
        matches = re.findall(r'\b' + re.escape(kw) + r'\b', text_lower)
        score += len(matches)
    # Additional criteria
    if has_url(text):
        score += 2
    if has_phone(text):
        score += 1
    if '!' in text:
        score += 1
    if is_all_caps(text):
        score += 2
    return score


def compute_scores(messages_df: pd.DataFrame, keywords: list) -> pd.DataFrame:
    """
    Add spam_score and keyword_count columns to the messages DataFrame.
    """
    df = messages_df.copy()
    df['spam_score'] = df['text'].apply(lambda x: score_message(x, keywords))

    def count_keywords(text):
        text_lower = text.lower()
        return sum(len(re.findall(r'\b' + re.escape(kw) + r'\b', text_lower))
                   for kw in keywords)

    df['keyword_count'] = df['text'].apply(count_keywords)
    return df


def find_best_threshold(messages_df: pd.DataFrame, keywords: list) -> int:
    """
    Find the threshold that maximizes classification accuracy on the dataset.
    """
    df = compute_scores(messages_df, keywords)
    y_true = (df['category'] == 'спам').astype(int)
    scores = df['spam_score']
    best_thr = 0
    best_acc = 0.0
    for thr in range(scores.min(), scores.max() + 1):
        y_pred = (scores >= thr).astype(int)
        acc = (y_true == y_pred).mean()
        if acc > best_acc:
            best_acc = acc
            best_thr = thr
        elif acc == best_acc:
            mid = (scores.min() + scores.max()) / 2
            if abs(thr - mid) < abs(best_thr - mid):
                best_thr = thr
    print(f"Оптимальный порог: {best_thr}, точность: {best_acc:.2f}")
    return best_thr


if __name__ == "__main__":
    config = load_config()
    keywords = [kw.strip() for kw in config['Classifier']['keywords'].split(',')]
    messages_df = load_pickle("data/messages.pkl")
    best_thr = find_best_threshold(messages_df, keywords)
    # Update config.ini
    config['Classifier']['threshold'] = str(best_thr)
    save_config(config)
    # Recompute with optimal threshold and save
    messages_df = compute_scores(messages_df, keywords)
    save_pickle(messages_df, "data/messages.pkl")
    print("Порог обновлён, сообщения пересчитаны.")