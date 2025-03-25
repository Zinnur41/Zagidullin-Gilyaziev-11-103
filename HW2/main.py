import os
import re
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from pymorphy3 import MorphAnalyzer
from collections import defaultdict

# Загрузка необходимых данных NLTK
import nltk
nltk.download('stopwords')

# Установка стоп-слов для русского языка
STOP_WORDS = set(stopwords.words('russian'))
INPUT_DIRECTORY = "HW1/pages"
OUTPUT_DIRECTORY = "results"


def extract_text_from_html(file_path):
    # Извлекает текст из HTML-файла, убирая теги и оставляя только содержимое
    with open(file_path, encoding="utf-8") as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, "html.parser")
    text = ' '.join(soup.stripped_strings)
    return text


def tokenize_text(text):
    # Разбивает текст на токены, убирает стоп-слова и дубликаты
    tokenizer = RegexpTokenizer(r'[А-Яа-яёЁ]+')
    tokens = tokenizer.tokenize(text.lower())
    filtered_tokens = {token for token in tokens if token not in STOP_WORDS}
    return filtered_tokens


def lemmatize_tokens(tokens):
    # Лемматизирует токены с помощью pymorphy3
    morph = MorphAnalyzer()
    lemmas = defaultdict(set)
    for token in tokens:
        lemma = morph.parse(token)[0].normal_form
        lemmas[lemma].add(token)
    return lemmas


def process_files_common(input_dir, output_tokens_file, output_lemmas_file):
    # Обрабатывает все файлы из директории и записывает общие токены и леммы
    all_tokens = set()

    for root, _, files in os.walk(input_dir):
        for file_name in files:
            if file_name.endswith(".txt"):
                file_path = os.path.join(root, file_name)
                text = extract_text_from_html(file_path)
                tokens = tokenize_text(text)
                all_tokens.update(tokens)

    # Записываем токены в файл
    os.makedirs(os.path.dirname(output_tokens_file), exist_ok=True)
    with open(output_tokens_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(all_tokens)))

    # Лемматизация токенов и запись в файл
    lemmas = lemmatize_tokens(all_tokens)
    with open(output_lemmas_file, "w", encoding="utf-8") as f:
        for lemma, words in sorted(lemmas.items()):
            f.write(f"{lemma}: {' '.join(sorted(words))}\n")


def process_files_individual(input_dir, output_dir):
    # Обрабатывает каждый файл отдельно и сохраняет токены и леммы для каждого файла
    for root, _, files in os.walk(input_dir):
        for file_name in files:
            if file_name.endswith(".txt"):
                file_path = os.path.join(root, file_name)
                text = extract_text_from_html(file_path)

                # Токенизация
                tokens = tokenize_text(text)
                tokens_output_path = os.path.join(output_dir, f"tokens_{file_name}")
                os.makedirs(os.path.dirname(tokens_output_path), exist_ok=True)
                with open(tokens_output_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(sorted(tokens)))

                # Лемматизация
                lemmas = lemmatize_tokens(tokens)
                lemmas_output_path = os.path.join(output_dir, f"lemmas_{file_name}")
                with open(lemmas_output_path, "w", encoding="utf-8") as f:
                    for lemma, words in sorted(lemmas.items()):
                        f.write(f"{lemma}: {' '.join(sorted(words))}\n")


if __name__ == "__main__":
    # Обработка всех файлов и запись общих результатов
    common_tokens_file = os.path.join(OUTPUT_DIRECTORY, "tokens.txt")
    common_lemmas_file = os.path.join(OUTPUT_DIRECTORY, "lemmas.txt")
    process_files_common(INPUT_DIRECTORY, common_tokens_file, common_lemmas_file)

    # Обработка каждого файла отдельно
    individual_output_dir = os.path.join(OUTPUT_DIRECTORY, "individual")
    process_files_individual(INPUT_DIRECTORY, individual_output_dir)
