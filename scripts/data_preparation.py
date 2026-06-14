"""
Load SMS Spam Collection, create senders and messages dictionaries in 3NF.
Author: M. M. Nurhussein
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import numpy as np
import pandas as pd
from library.helpers import (
    count_words, has_url, has_phone, has_exclamation, is_all_caps, save_pickle
)


def generate_senders(messages_count: int, seed: int = 42) -> pd.DataFrame:
    """
    Create synthetic sender DataFrame with activity field.
    """
    random.seed(seed)
    np.random.seed(seed)
    num_senders = random.randint(150, 200)
    sender_ids = [f"S{i:04d}" for i in range(1, num_senders + 1)]
    sender_types = ['личный', 'служебный', 'рекламный', 'неизвестный']
    countries = ['Россия', 'США', 'Китай', 'другая']
    trusted_opts = ['да', 'нет']

    data = {
        'sender_id': sender_ids,
        'sender_type': np.random.choice(sender_types, size=num_senders, p=[0.6, 0.2, 0.1, 0.1]),
        'country': np.random.choice(countries, size=num_senders, p=[0.5, 0.2, 0.1, 0.2]),
        'trusted': np.random.choice(trusted_opts, size=num_senders, p=[0.8, 0.2]),
        'activity': 0
    }
    return pd.DataFrame(data)


def load_and_prepare_data(dataset_path: str = "data/SMSSpamCollection"):
    """
    Load the dataset and create two dictionaries.

    Returns:
        senders_df (pd.DataFrame), messages_df (pd.DataFrame)
    """
    # The file has tab-separated values: label\tmessage
    df = pd.read_csv(dataset_path, sep='\t', header=None, names=['label', 'text'])
    # Map to Russian labels as required by the domain description
    df['label'] = df['label'].map({'spam': 'спам', 'ham': 'не спам'})

    senders_df = generate_senders(len(df))

    # Assign each message to a random sender
    sender_ids = senders_df['sender_id'].tolist()
    df['sender_id'] = np.random.choice(sender_ids, size=len(df))

    # Update activity (number of messages per sender)
    activity = df.groupby('sender_id').size()
    senders_df['activity'] = senders_df['sender_id'].map(activity).fillna(0).astype(int)

    # Build messages DataFrame with all required attributes
    messages_data = {
        'message_id': [f"M{i:05d}" for i in range(1, len(df) + 1)],
        'sender_id': df['sender_id'],
        'text': df['text'],
        'length': df['text'].apply(len),
        'word_count': df['text'].apply(count_words),
        'has_link': df['text'].apply(has_url).map({True: 'да', False: 'нет'}),
        'has_phone': df['text'].apply(has_phone).map({True: 'да', False: 'нет'}),
        'has_exclamation': df['text'].apply(has_exclamation).map({True: 'да', False: 'нет'}),
        'all_caps': df['text'].apply(is_all_caps).map({True: 'да', False: 'нет'}),
        'keyword_count': 0,     # will be computed by classifier
        'spam_score': 0,        # will be computed by classifier
        'category': df['label'] # спам / не спам
    }
    messages_df = pd.DataFrame(messages_data)

    return senders_df, messages_df


if __name__ == "__main__":
    snd, msg = load_and_prepare_data()
    save_pickle(snd, "data/senders.pkl")
    save_pickle(msg, "data/messages.pkl")
    print("Справочники созданы и сохранены в data/senders.pkl и data/messages.pkl")