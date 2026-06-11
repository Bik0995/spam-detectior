# Spam Detection Application

A desktop application for detecting spam messages using heuristic rules.  
Built with Python, Pandas, and Tkinter.  
Developed as part of the "Project Seminar: Python for Data Science" course.  
**Group БИВ255**.

---

## What does this app do?

- Classifies SMS/messenger messages as **SPAM** or **NOT SPAM** using a scoring system based on keywords, URLs, phone numbers, exclamation marks, and capitalization.
- Provides a graphical interface (Russian language) to manage sender and message dictionaries (CRUD operations).
- Generates seven analytical reports: three text-based (CSV/TXT) and four graphical (bar chart, histogram, box plot, scatter plot).
- The classification threshold is automatically tuned on the SMS Spam Collection dataset (94% accuracy) and can be adjusted by the user.

---

## Requirements

- Python 3.8 or higher (Anaconda recommended)
- Libraries: pandas, numpy, matplotlib, tkinter (all included in standard Anaconda distribution)


## How to run

1. Download the **SMS Spam Collection Dataset** from the UCI Machine Learning Repository and place the file `SMSSpamCollection` into the `data/` folder.

2. Prepare the data (generates `senders.pkl` and `messages.pkl`):
   ```bash
   python scripts/data_preparation.py
