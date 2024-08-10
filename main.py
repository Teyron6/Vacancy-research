import os
import requests
from itertools import count
from terminaltables import AsciiTable
from dotenv import load_dotenv


LANGUAGES = ['Rust', 'GO', 'Javascript', 'Python', 'C++', 'C#', 'Ruby']


def get_vacancy_hh(lang):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'text' : lang,
        'area' : 1,
        'period' : 30,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    vacancy = response.json()
    return vacancy


def predict_rub_salary(from_salary=None, to_salary=None):
    if from_salary and to_salary:
        return int((from_salary + to_salary)/2)
    elif from_salary:
        return int(from_salary*0.8)
    elif to_salary:
        return int(to_salary*1.2)
    else:
        return None


def salary_averaging_hh():
    results_hh = {}
    salary_sum = []
    sum_of_processed_salaries = 0
    for lang in LANGUAGES:
        for page in count(0):
            vacancyes = get_vacancy_hh(lang)
            if page >= vacancyes['pages']-1:
                break
            for vacancy in vacancyes['items']:
                salary = vacancy.get('salary')
                if salary and salary['currency'] == 'RUR':
                    predicted_salary = predict_rub_salary(vacancy['salary'].get('from'), vacancy['salary'].get('to'))
                    if predicted_salary:
                        salary_sum.append(predicted_salary)
                        sum_of_processed_salaries += 1
        vacancyes_found = vacancyes['found']
        avg_salary = None
        if salary_sum:
            avg_salary = int(sum(salary_sum)/len(salary_sum))
        results_hh[lang] = {
            'vacancyes_found' : vacancyes_found,
            'vacancies_processed' : sum_of_processed_salaries,
            'average_salary' : int(avg_salary),
            }
    return results_hh
        

def get_vacancy_sj(lang, page, token):
    url = 'https://api.superjob.ru/2.0/vacancies'
    params = {
        'town' : 4,
        'keyword' : lang,
        'count' : 100,
        'page' : page,
    }
    headers = {
        'X-Api-App-Id' : token
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status
    vacancy = response.json()
    return vacancy
        

def salary_averaging_sj(token):
    results_sj = {}
    salary_sum = []
    sum_of_processed_salaries = 0
    for lang in LANGUAGES:
        for page in count(0):
            vacancyes = get_vacancy_sj(lang, page, token)
            if not vacancyes['objects']:
                break            
            for vacancy in vacancyes['objects']:
                predicted_salary = predict_rub_salary(vacancy['payment_from'], vacancy['payment_to'])
                if predicted_salary:
                        salary_sum.append(predicted_salary)
                        sum_of_processed_salaries += 1
        vacancyes_found = vacancyes['total']
        avg_salary = None
        if salary_sum:
            avg_salary = int(sum(salary_sum)/len(salary_sum))
        results_sj[lang] = {
            'vacancyes_found' : vacancyes_found,
            'vacancies_processed' : sum_of_processed_salaries,
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
    sj_salaryes = salary_averaging_sj(token)
    hh_salaryes = salary_averaging_hh()
    print(create_table(sj_salaryes))
    print(create_table(hh_salaryes))


if __name__ == '__main__':
    main()