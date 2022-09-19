from dotenv import load_dotenv
import os
import requests
from terminaltables import AsciiTable


def get_count_vacancies_hh(search_text):
    url = 'https://api.hh.ru/vacancies'
    period_days = 30
    town_id = 1
    payload = {
        'text': f'программист {search_text}',
        'area': town_id,
        'period': period_days
    }
    response = requests.get(url, params=payload)
    response.raise_for_status()

    return response.json()['found']

def get_vacancies_hh(search_text):
    url = 'https://api.hh.ru/vacancies'
    page = 0
    pages_number = 10
    period_days = 30
    town_id = 1
    vacancies = []
    while page < pages_number:
        payload = {
            'text': f'программист {search_text}',
            'area': town_id,
            'period': period_days,
            'only_with_salary': 'true',
            'page': page,
            'per_page': 100
        }
        response = requests.get(url, params=payload)
        response.raise_for_status()
        vacancies += response.json()['items']
        page += 1
    return vacancies

def get_count_vacancies_sj(search_text, SJ_KEY):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': SJ_KEY
    }
    category_id = 48
    town_id = 4
    payload = {
        'catalogues': category_id,
        'keyword': search_text,
        'town': town_id,
        'page': 5,
        'count': 100
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()

    return response.json()['total']

def get_vacancies_sj(search_text, SJ_KEY):
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {
        'X-Api-App-Id': SJ_KEY
    }
    category_id = 48
    town_id = 4
    payload = {
        'catalogues': category_id,
        'keyword': search_text,
        'town': town_id
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()

    return response.json()['objects']

def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        return salary_from * 1.2
    if salary_to:
        return salary_to * 0.8

def predict_rub_salary_hh(vacancy):
    if vacancy['salary']['currency'] != 'RUR':
        return None
    salary_from = vacancy['salary']['from']
    salary_to = vacancy['salary']['to']
    return predict_salary(salary_from, salary_to)

def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    return predict_salary(salary_from, salary_to)

def print_vacancies_statistic(title, popular_langs):
    table_statistic = [
        (
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        )
    ]
    for lang,count in popular_langs.items():
        table_statistic.append((
            lang,
            popular_langs[lang]['vacancies_found'],
            popular_langs[lang]['vacancies_processed'],
            popular_langs[lang]['average_salary']
        ))
    table_statistic = tuple(table_statistic)
    table_instance = AsciiTable(table_statistic, title)
    print(table_instance.table)


if __name__ == "__main__":
    load_dotenv()
    SJ_KEY = os.environ['SJ_KEY']

    popular_langs = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Scala',
        'Go',
        'Swift'
    ]
    popular_langs_salaries = {}

    # HeadHunter:
    for lang in popular_langs:
        vacancies = get_vacancies_hh(lang)
        lang_salaries = []
        for vacancy in vacancies:
            salary = predict_rub_salary_hh(vacancy)
            if salary:
                lang_salaries.append(salary)

        if lang_salaries:
            average_salary = sum(lang_salaries) / len(lang_salaries)

        popular_langs_salaries[lang] = {
            'vacancies_found': len(vacancies),
            'vacancies_processed': len(lang_salaries),
            'average_salary': int(average_salary)
        }
    print_vacancies_statistic('HeadHunter Moscow', popular_langs_salaries)


    # SuperJob:
    for lang in popular_langs:
        vacancies = get_vacancies_sj(lang, SJ_KEY)
        lang_salaries = []
        for vacancy in vacancies:
            salary = predict_rub_salary_sj(vacancy)
            if salary:
                lang_salaries.append(salary)

        if lang_salaries:
            average_salary = sum(lang_salaries) / len(lang_salaries)

        popular_langs_salaries[lang] = {
            'vacancies_found': len(vacancies),
            'vacancies_processed': len(lang_salaries),
            'average_salary': int(average_salary)
        }
    print_vacancies_statistic('SuperJob Moscow', popular_langs_salaries)
