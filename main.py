import os
import requests
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv


LANGUAGES = ['Rust', 'GO', 'Javascript', 'Python', 'C++', 'C#', 'Ruby']


def get_vacancies_hh(lang):
    url = 'https://api.hh.ru/vacancies'
    moscow_id = 1
    params = {
        'text' : lang,
        'area' : moscow_id,
        'period' : 30,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    vacancies = response.json()
    return vacancies


def predict_rub_salary(from_salary=None, to_salary=None):
    if from_salary and to_salary:
        return int((from_salary + to_salary)/2)
    elif from_salary:
        return int(from_salary*0.8)
    elif to_salary:
        return int(to_salary*1.2)
    else:
        return None


def averageing_salaries_hh():
    results_hh = {}
    language_salaries = []
    for lang in LANGUAGES:
        for page in count(0):
            vacancies = get_vacancies_hh(lang)
            if page >= vacancies['pages']-1:
                break
            for vacancy in vacancies['items']:
                salary = vacancy.get('salary')
                if salary and salary['currency'] == 'RUR':
                    predicted_salary = predict_rub_salary(vacancy['salary'].get('from'), vacancy['salary'].get('to'))
                    if predicted_salary:
                        language_salaries.append(predicted_salary)
        vacancyes_found = vacancies['found']
        avg_salary = None
        if language_salaries:
            avg_salary = int(sum(language_salaries)/len(language_salaries))
        results_hh[lang] = {
            'vacancyes_found' : vacancyes_found,
            'vacancies_processed' : len(language_salaries),
            'average_salary' : int(avg_salary),
        }
    return results_hh
        

def get_vacancies_sj(lang, page, token):
    url = 'https://api.superjob.ru/2.0/vacancies'
    moscow_id = 4
    params = {
        'town' : moscow_id,
        'keyword' : lang,
        'count' : 100,
        'page' : page,
    }
    headers = {
        'X-Api-App-Id' : token
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status
    vacancies = response.json()
    return vacancies
        

def averageing_salaries_sj(token):
    results_sj = {}
    language_salaries = []
    for lang in LANGUAGES:
        for page in count(0):
            vacancies = get_vacancies_sj(lang, page, token)
            if not vacancies['objects']:
                break            
            for vacancy in vacancies['objects']:
                predicted_salary = predict_rub_salary(vacancy['payment_from'], vacancy['payment_to'])
                if predicted_salary:
                        language_salaries.append(predicted_salary)
        vacancyes_found = vacancies['total']
        avg_salary = None
        if language_salaries:
            avg_salary = int(sum(language_salaries)/len(language_salaries))
        results_sj[lang] = {
            'vacancyes_found' : vacancyes_found,
            'vacancies_processed' : len(language_salaries),
            'average_salary' : avg_salary,
        }
    return results_sj
        

def create_table(stats):
    vacancy_table= [
        ['Язык программирования', 'Вакансий найдено', 'Вакансий обработанно', 'Средняя зарплата'],
    ]
    for language, vacancy in stats.items():
        vacancy_table.append([language, vacancy['vacancyes_found'], vacancy['vacancies_processed'], vacancy['average_salary']])
    table = AsciiTable(vacancy_table)
    return table.table


def main():
    load_dotenv()
    token = os.environ['SJ_TOKEN']
    sj_salaries = averageing_salaries_sj(token)
    hh_salaries = averageing_salaries_hh()
    print(create_table(sj_salaries))
    print(create_table(hh_salaries))


if __name__ == '__main__':
    main()