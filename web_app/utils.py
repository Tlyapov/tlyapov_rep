import datetime
import os
import traceback
from django.utils import timezone
import pandas as pd
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect

from CustomSurvey.models import FakeClientAnsers, DeferredSurvey, ClientAnswersToCustomSurvey, CustomSurvey, \
    CustomQuestion, CustomAnswers, TimeRunSurvey
from clients.models import Clients
from employees.models import Employees
from light_admin.settings import BASE_DIR
from traffic_light.models import FeedBack
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_error(message):
    api_token = BOT_TOKEN
    r = requests.get('https://api.telegram.org/bot{}/sendMessage'.format(api_token), params=dict(chat_id=CHAT_ID, text=message))
    if r.status_code != 200:
        print(f"ERROR - send telegram {r.status_code}")

def get_employee_clients(employ_id):
    try:
        employee = Employees.objects.get(id=employ_id)
        if Clients.objects.all().exists() and Clients.objects.all().filter(employee=employee).exists():
            return int(Clients.objects.all().filter(employee=employee).count())
        else:
            return 0
    except  BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in get_employee_clients {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in get_employee_clients {e}")
        print(traceback.print_exc(limit=5))




def get_default_servery():
    try:
        survey_obj = None
        for i in CustomSurvey.objects.all():
            if i.is_light == True:
                survey_obj = i
                break
        if survey_obj is None:
            survey = CustomSurvey.objects.create(
                name="Опрос светофор",
                is_light=True
            )
            question = CustomQuestion.objects.create(
                question="Здравствуйте, {{name}}!\n\nНасколько Вам комфортно работать с Командой АНП ЗЕНИТ?\n\nВыберите, пожалуйста, соответствующую кнопку:"
            )
            answer1 = CustomAnswers.objects.create(
                value="🟢 Все нравится!"
            )
            answer2 = CustomAnswers.objects.create(
                value="🟡 Есть вопросы."
            )
            answer3 = CustomAnswers.objects.create(
                value="🔴 Очень плохо ("
            )
            question.answer_variants.add(answer1)
            question.answer_variants.add(answer2)
            question.answer_variants.add(answer3)
            question.save()
            survey.questions.add(question)
            survey.save()
            return survey.id
        else:
            return survey_obj.id
    except  BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in get_default_servery {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in get_default_servery {e}")
        print(traceback.print_exc(limit=5))




def get_lust_rating_and_date(client_id):
    try:
        if FeedBack.objects.all().exists() and FeedBack.objects.filter(client=Clients.objects.get(id=client_id), feedback_type='light').exists():
            fb_obj = \
            FeedBack.objects.filter(client=Clients.objects.get(id=client_id), feedback_type='light').order_by('-id')[0]
        else:
            return '-','-'
        fb_obj_date = fb_obj.data_time.split()[0]
        data = f"{str(fb_obj_date).split('-')[2]}.{str(fb_obj_date).split('-')[1]}.{str(fb_obj_date).split('-')[0]}"
        return fb_obj.answer, data
    except  BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in get_lust_rating_and_date {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in get_lust_rating_and_date {e}")
        print(traceback.print_exc(limit=5))

def get_all_surveys_count():
    try:
        not_passed_survey = 0
        for i in DeferredSurvey.objects.all():
            if i.status == False:
                not_passed_survey += 1
        passed_survey = 0
        for i in DeferredSurvey.objects.all():
            if i.status == True:
                passed_survey += 1
        return passed_survey, not_passed_survey
    except  BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in get_all_surveys_count {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in get_all_surveys_count {e}")
        print(traceback.print_exc(limit=5))



def get_average_rating():
    try:
        sum_rate = 0
        count_rate = 0
        for i in FeedBack.objects.all():
            if i.is_light == True:
                if i.answer == "🟢 Все нравится!":
                    sum_rate += 3
                    count_rate += 1
                if i.answer == "🟡 Есть вопросы.":
                    sum_rate += 2
                    count_rate += 1
                if i.answer == "🔴 Очень плохо (":
                    sum_rate += 1
                    count_rate += 1
        if count_rate != 0:
            if sum_rate/count_rate > 2.5:
                average_rating = 'Превосходно'
            elif sum_rate/count_rate > 1.5:
                average_rating = 'Нормально'
            else:
                average_rating = 'Плохо'
            return average_rating
        else:
            return '-'
    except  BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in get_average_rating {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in get_average_rating {e}")
        print(traceback.print_exc(limit=5))




def get_task_count(client_id):
    try:
        all_fb = FeedBack.objects.filter(client=Clients.objects.get(id=client_id)).count()
        done_fb = FeedBack.objects.filter(client=Clients.objects.get(id=client_id), progress_status='done').count()
        return f'{done_fb}/{all_fb}'
    except  BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in get_task_count {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in get_task_count {e}")
        print(traceback.print_exc(limit=5))


def get_all_tasks_count():
    try:
        tasks_count = FeedBack.objects.all().count
        return tasks_count
    except  BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in get_all_tasks_count {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in get_all_tasks_count {e}")
        print(traceback.print_exc(limit=5))

def get_rates_of_employee_count(employee_id):
    try:
        perf_count = 0
        good_count = 0
        bad_count = 0
        feedback_count = 0
        for i in FeedBack.objects.all().filter(feedback_type='light', supervisor=str(employee_id)):
            if i.answer == "🟢 Все нравится!":
                perf_count +=1
            if i.answer == "🟡 Есть вопросы.":
                good_count +=1
            if i.answer == "🔴 Очень плохо (":
                bad_count +=1
        feedback_count = FeedBack.objects.all().filter(feedback_type='light', supervisor=str(employee_id)).count()
        if feedback_count == 0:
            average_rating_by_empl = '-'
        else:
            average_rating_by_empl = (perf_count * 3 + good_count * 2 + bad_count) / int(feedback_count)
            if average_rating_by_empl > 2.5:
                average_rating_by_empl = 'Превосходно'
            elif average_rating_by_empl > 1.5:
                average_rating_by_empl = 'Нормально'
            elif average_rating_by_empl > 0.5:
                average_rating_by_empl = 'Плохо'
        return perf_count, good_count, bad_count, feedback_count, average_rating_by_empl
    except  BaseException as e:
        send_telegram_error(str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in get_rates_of_employee_count {e}")
        print(traceback.print_exc(limit=5))


def get_task_date(task_id):
    try:
        for i in FeedBack.objects.all():
            if i.id == task_id:
                date = str(i.data_time).split(' ')[0]
        date = f"{str(date).split('-')[2]}.{str(date).split('-')[1]}.{str(date).split('-')[0]}"
        return date
    except  BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in get_task_date {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in get_task_date {e}")
        print(traceback.print_exc(limit=5))


def check_expired_date(task_id):
    try:
        fb = FeedBack.objects.get(id=task_id)
        fb_date = fb.data_time.split()[0]
        if fb.is_light == True:
            date = datetime.datetime.strptime(
                f"{int(str(fb_date).split('-')[2])}.{str(fb_date).split('-')[1]}.{str(fb_date).split('-')[0]}",
                '%d.%m.%Y')
            date = date + datetime.timedelta(days=1)
        else:
            date = datetime.datetime.strptime(
                f"{int(str(fb_date).split('-')[2])}.{str(fb_date).split('-')[1]}.{str(fb_date).split('-')[0]}",
                '%d.%m.%Y')
            date = date + datetime.timedelta(days=5)
        date_now = datetime.datetime.now()
        if date.date() < date_now.date() and (fb.progress_status == 'not_taken' or fb.progress_status == 'in_progress'):
            return True
        elif fb.progress_status == 'done':
            return False
        else:
            return False
    except BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in check_expired_date {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in check_expired_date {e}")
        print(traceback.print_exc(limit=5))


def clients_excel():
    try:
        filename = 'clients.xlsx'
        filepath = str(BASE_DIR).replace('\\', "/") + '/light_admin/filedownload/'
        if os.path.isdir(filepath):
            if os.path.isfile(filepath + filename):
                pass
            else:
                path = open(filepath + filename, "w+")
                path.close()
        else:
            os.mkdir(filepath)
            path = open(filepath + filename, "w+")
            path.close()
        clients = Clients.objects.all()
        clients_excel_name = []
        clients_excel_status = []
        clients_excel_company_name = []
        clients_excel_client_code = []
        clients_excel_job_title = []
        clients_excel_employee = []
        clients_excel_phone = []
        dic_rating = []
        dic_rating_date = []
        dic_task_count = []
        for i in clients:
            rating, date = get_lust_rating_and_date(i.id)
            task_count = get_task_count(i.id)
            clients_excel_phone.append(i.phone)
            clients_excel_name.append(i.name)
            clients_excel_status.append('Активен')
            clients_excel_company_name.append(i.company_name)
            clients_excel_client_code.append(i.client_code)
            clients_excel_job_title.append(i.job_title)
            if i.employee != None:
                clients_excel_employee.append(f"{i.employee.name} {i.employee.surname}")
            else:
                clients_excel_employee.append(f"")
            dic_rating.append(rating)
            dic_rating_date.append(date)
            dic_task_count.append(task_count)
        client_table_list = zip(clients_excel_name, clients_excel_status, clients_excel_company_name,
                                clients_excel_client_code, clients_excel_job_title, clients_excel_employee,
                                clients_excel_phone,
                                dic_rating, dic_rating_date, dic_task_count)
        df = pd.DataFrame(client_table_list)
        if df.empty:
            return redirect('clients', pg=1)
        else:
            df.columns = ['ФИО', "Статус", "Компания", "Код клиента", "Должность", "Ответственный руководитель",
                          "Телефон", "Последняя оценка",
                          "Дата", "Количество обратной связи"]
            df.to_excel(filepath + filename)
            path = open(filepath + filename, 'rb')
            response = HttpResponse(path.read(), content_type='application/vnd.ms-excel', charset='utf-8')
            response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    except BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in clients_excel {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in clients_excel {e}")
        print(traceback.print_exc(limit=5))


def employees_excel():
    try:
        filename = 'employees.xlsx'
        filepath = str(BASE_DIR).replace('\\', "/") + '/light_admin/filedownload/'
        if os.path.isdir(filepath):
            if os.path.isfile(filepath + filename):
                pass
            else:
                path = open(filepath + filename, "w+")
                path.close()
        else:
            os.mkdir(filepath)
            path = open(filepath + filename, "w+")
            path.close()
        employees = Employees.objects.all()
        dic_empl_clients_count = []
        dic_empl_perf_rate = []
        dic_empl_good_rate = []
        dic_empl_bad_rate = []
        dic_empl_feedback_count = []
        empl_surname = []
        empl_name = []
        empl_job_title = []
        empl_phone = []
        empl_role = []
        for i in employees:
            if i.role == 'employee':
                empl_surname.append(i.surname)
                empl_name.append(i.name)
                empl_job_title.append(i.job_title)
                empl_phone.append(i.phone)
                empl_role.append(i.role)
                empl_perf_rate, empl_good_rate, empl_bad_rate, feedback_count = get_rates_of_employee_count(i.id)
                empl_clients_count = get_employee_clients(i.id)
                dic_empl_clients_count.append(empl_clients_count)
                dic_empl_perf_rate.append(empl_perf_rate)
                dic_empl_good_rate.append(empl_good_rate)
                dic_empl_bad_rate.append(empl_bad_rate)
                dic_empl_feedback_count.append(feedback_count)
        employee_table_list = zip(empl_surname, empl_name, empl_job_title, empl_phone, dic_empl_clients_count,
                                  dic_empl_perf_rate, dic_empl_good_rate,
                                  dic_empl_bad_rate, dic_empl_feedback_count, empl_role)
        df = pd.DataFrame(employee_table_list)
        if df.empty:
            return redirect('employees', pg=1)
        else:
            df.columns = ['Фамилия', "Имя", "Должность", "Телефон", "Количество клиентов", "Превосходно", "Нормально",
                          "Плохо", "Количество обратной связи", "Роль"]
            df.to_excel(filepath + filename)
            path = open(filepath + filename, 'rb')
            response = HttpResponse(path.read(), content_type='application/vnd.ms-excel', charset='utf-8')
            response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    except BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in employees_excel {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in employees_excel {e}")
        print(traceback.print_exc(limit=5))


def users_excel():
    try:
        filename = 'users.xlsx'
        filepath = str(BASE_DIR).replace('\\', "/") + '/light_admin/filedownload/'
        if os.path.isdir(filepath):
            if os.path.isfile(filepath + filename):
                pass
            else:
                path = open(filepath + filename, "w+")
                path.close()
        else:
            os.mkdir(filepath)
            path = open(filepath + filename, "w+")
            path.close()
        employees = Employees.objects.all()
        dic_empl_clients_count = []
        dic_empl_perf_rate = []
        dic_empl_good_rate = []
        dic_empl_bad_rate = []
        dic_empl_feedback_count = []
        empl_surname = []
        empl_name = []
        empl_job_title = []
        empl_phone = []
        empl_role = []
        for i in employees:
            if i.role == 'user':
                empl_surname.append(i.surname)
                empl_name.append(i.name)
                empl_job_title.append(i.job_title)
                empl_phone.append(i.phone)
                empl_role.append(i.role)
                empl_perf_rate, empl_good_rate, empl_bad_rate, feedback_count = get_rates_of_employee_count(i.id)
                empl_clients_count = get_employee_clients(i.id)
                dic_empl_clients_count.append(empl_clients_count)
                dic_empl_perf_rate.append(empl_perf_rate)
                dic_empl_good_rate.append(empl_good_rate)
                dic_empl_bad_rate.append(empl_bad_rate)
                dic_empl_feedback_count.append(feedback_count)
        employee_table_list = zip(empl_surname, empl_name, empl_job_title, empl_phone, dic_empl_clients_count,
                                  dic_empl_perf_rate, dic_empl_good_rate,
                                  dic_empl_bad_rate, dic_empl_feedback_count, empl_role)
        df = pd.DataFrame(employee_table_list)
        if df.empty:
            return redirect('users', pg=1)
        else:
            df.columns = ['Фамилия', "Имя", "Должность", "Телефон", "Количество клиентов", "Превосходно", "Нормально",
                          "Плохо", "Количество обратной связи", "Роль"]
            df.to_excel(filepath + filename)
            path = open(filepath + filename, 'rb')
            response = HttpResponse(path.read(), content_type='application/vnd.ms-excel', charset='utf-8')
            response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    except BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in users_excel {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in users_excel {e}")
        print(traceback.print_exc(limit=5))


def surveys_and_reviews_excel(date):
    try:
        filename = 'surveys_and_reviews.xlsx'
        filepath = str(BASE_DIR).replace('\\', "/") + '/light_admin/filedownload/'
        if os.path.isdir(filepath):
            if os.path.isfile(filepath + filename):
                pass
            else:
                path = open(filepath + filename, "w+")
                path.close()
        else:
            os.mkdir(filepath)
            path = open(filepath + filename, "w+")
            path.close()
        surveys_and_reviews = FeedBack.objects.all()
        if date != '0':
            select_date = datetime.datetime.strptime(date['select_date'], '%Y-%m-%d')
            if date['select_date_2']:
                select_date_2 = datetime.datetime.strptime(date['select_date_2'], '%Y-%m-%d')
                sr_ids = []
                for fb in surveys_and_reviews:
                    fb_date = datetime.datetime.strptime(fb.data_time.split(' ')[0], '%Y-%m-%d')
                    if select_date_2 >= fb_date >= select_date:
                        sr_ids.append(fb.id)
                surveys_and_reviews = FeedBack.objects.filter(id__in=sr_ids)
            else:
                surveys_and_reviews = FeedBack.objects.filter(data_time__startswith=select_date)
        dic_task_date = []
        clients_excel_name = []
        clients_excel_company_name = []
        clients_excel_client_code = []
        clients_excel_job_title = []
        clients_excel_employee = []
        task_employee = []
        task_rate = []
        task_answer = []
        task_status = []
        for i in surveys_and_reviews:
            clients_excel_name.append(i.client.name)
            clients_excel_company_name.append(i.client.company_name)
            clients_excel_client_code.append(i.client.client_code)
            clients_excel_job_title.append(i.client.job_title)
            dic_task_date.append(get_task_date(i.id))
            if i.client.employee is not None:
                clients_excel_employee.append(f"{i.client.employee.name} {i.client.employee.surname}")
            else:
                clients_excel_employee.append(f"")
            if i.employee is not None:
                task_employee.append(f"{i.employee.name} {i.employee.surname}")
            else:
                task_employee.append(f"")
            task_rate.append(i.light_answer)
            task_answer.append(i.answer)
            task_status.append(i.progress_status)
        tasks_table_list = zip(dic_task_date, clients_excel_name, clients_excel_company_name, clients_excel_client_code,
                               clients_excel_job_title, task_rate, task_answer, task_status, task_employee,
                               clients_excel_employee)
        df = pd.DataFrame(tasks_table_list)
        if df.empty:
            return redirect('surveys_and_reviews', pg=1)
        else:
            df.columns = ['Дата оценки', "ФИО", "Компания", "Код клиента", "Должность", "Оценка", "Комментарий",
                          "Статус выполнения", "Исполнитель", "Ответственный руководитель"]
            df.to_excel(filepath + filename)
            path = open(filepath + filename, 'rb')
            response = HttpResponse(path.read(), content_type='application/vnd.ms-excel', charset='utf-8')
            response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    except BaseException as e:
        send_telegram_error(f"ERROR web_app/utils.py in surveys_and_reviews_excel {e}\n" + str(traceback.print_exc(limit=5)))
        print(f"ERROR web_app/utils.py in surveys_and_reviews_excel {e}")
        print(traceback.print_exc(limit=5))


def get_clients_by_filter_data(pg, filter_data=None):
    if filter_data:
        date = f"{filter_data.split('-')[2]}.{filter_data.split('-')[1]}.{filter_data.split('-')[0]}"
        list_id = []
        clients = Clients.objects.all()
        for client in clients:
            rating, rating_date = get_lust_rating_and_date(client.id)
            if rating_date == date:
                list_id.append(client.id)
        return Clients.objects.filter(id__in=list_id)[10 * (pg - 1): 10 * pg]
    else:
        return Clients.objects.all()[10 * (pg - 1): 10 * pg]



def get_clients_table(pg, filter_data=None):
    client_dict = {}
    clients = get_clients_by_filter_data(pg, filter_data)
    for i in clients:
        rating, date = get_lust_rating_and_date(i.id)
        client_dict[i.id] = {
            'id': i.id,
            'client_code': i.client_code,
            'company_name': i.company_name,
            'name': i.name,
            'chat_id': i.chat_id,
            'job_title': i.job_title,
            'employee': f"{i.employee.name} {i.employee.surname}",
            'phone': i.phone,
            'rating': rating,
            'date': date,
            'tasks': get_task_count(i.id),
            'automation': get_client_automation(i.id)
        }
    return client_dict


def get_client_automation(client_id):
    client = Clients.objects.get(id=client_id)
    if TimeRunSurvey.objects.filter().exists():
        for i in TimeRunSurvey.objects.filter().order_by('-id'):
             if client in i.clients.all():
                 start_time = f"{str(i.start_time).split('-')[2]}.{str(i.start_time).split('-')[1]}.{str(i.start_time).split('-')[0]}"
                 end_time = f"{str(i.end_time).split('-')[2]}.{str(i.end_time).split('-')[1]}.{str(i.end_time).split('-')[0]}"
                 return f'{start_time}-\n{end_time}\n{i.send_time}'
        return '-'
    else:
        return '-'

def get_clients_table_filters(pg,filter_data):
    list_id = []
    clients = Clients.objects.all()
    if ('status_filter' in filter_data) and (filter_data['status_filter'][0] != 'all'):
        for client in clients:
            if client.chat_id:
                list_id.append(client.id)
        if filter_data['status_filter'][0] == 'active':
            clients = clients.filter(id__in=list_id)
        else:
            clients = clients.exclude(id__in=list_id)
    if ('employee_filter' in filter_data) and (filter_data['employee_filter'][0] != 'all'):
        employee = str(filter_data['employee_filter'][0])
        clients = clients.filter(employee=employee)

    client_dict = {}
    for i in clients:
        rating, date = get_lust_rating_and_date(i.id)
        client_dict[i.id] = {
            'client_code': i.client_code,
            'company_name': i.company_name,
            'name': i.name,
            'chat_id': i.chat_id,
            'job_title': i.job_title,
            'employee': f"{i.employee.name} {i.employee.surname}",
            'phone': i.phone,
            'rating': rating,
            'date': date,
            'tasks': get_task_count(i.id)
        }
    return client_dict

def surveys_and_reviews_filter(pg, filter_data):
    surveys_and_reviews = FeedBack.objects.filter().order_by("-id")
    if 'select_date' in filter_data:
        select_date = datetime.datetime.strptime(str(filter_data['select_date'][0]), '%Y-%m-%d')
        if ('select_date_2' in filter_data) and str(filter_data['select_date_2'][0]) != '':
            select_date_2 = datetime.datetime.strptime(str(filter_data['select_date_2'][0]), '%Y-%m-%d')
            sr_ids = []
            for fb in surveys_and_reviews:
                fb_date = datetime.datetime.strptime(fb.data_time.split(' ')[0], '%Y-%m-%d')
                if select_date_2 >= fb_date >= select_date:
                    sr_ids.append(fb.id)
            surveys_and_reviews = FeedBack.objects.filter(id__in=sr_ids)
        else:
            date = str(filter_data['select_date'][0])
            surveys_and_reviews = surveys_and_reviews.filter(data_time__startswith=date)
    if 'light_answer' in filter_data:
        if str(filter_data['light_answer'][0]) == 'perf':
            surveys_and_reviews = surveys_and_reviews.filter(answer='🟢 Все нравится!')
        if str(filter_data['light_answer'][0]) == 'good':
            surveys_and_reviews = surveys_and_reviews.filter(answer='🟡 Есть вопросы.')
        if str(filter_data['light_answer'][0]) == 'bad':
            surveys_and_reviews = surveys_and_reviews.filter(answer='🔴 Очень плохо (')
    if 'client_code' in filter_data:
        surveys_and_reviews = surveys_and_reviews.filter(client=str(filter_data['client_code'][0]))
    if 'pr_status' in filter_data:
        surveys_and_reviews = surveys_and_reviews.filter(progress_status=str(filter_data['pr_status'][0]))
    if 'employee' in filter_data:
        surveys_and_reviews = surveys_and_reviews.filter(employee=str(filter_data['employee'][0]))
    if 'supervisor' in filter_data:
        surveys_and_reviews = surveys_and_reviews.filter(supervisor=str(filter_data['supervisor'][0]))
    if 'fb_types' in filter_data:
        surveys_and_reviews = surveys_and_reviews.filter(feedback_type=str(filter_data['fb_types'][0]))
    return surveys_and_reviews[10 * (pg - 1): 10 * pg]


def get_count_surveys(start_time, end_time, survey_id, periodicity, client_id, send_time, last_send_date):
    try:
        send_surveys, done_surveys, conversion = 0, 0, 0
        start_time_count = datetime.datetime.combine(start_time, send_time)
        last_send_date = last_send_date.astimezone(timezone.utc).replace(tzinfo=None)
        if last_send_date > datetime.datetime.now():
            return 0, 0, 0
        elif periodicity != 0 and (last_send_date - start_time_count).days != 0:
            send_surveys = (last_send_date - start_time_count).days//periodicity + 1
        else:
            send_surveys = 1
        if survey_id == get_default_servery():
            if FeedBack.objects.filter(client__id=client_id, feedback_type='light').exists():
                fb_obj = FeedBack.objects.filter(client__id=client_id, feedback_type='light')
                start_time_count = datetime.datetime.combine(start_time, send_time)
                for fb in fb_obj:
                    fb_data_time = datetime.datetime.strptime(fb.data_time.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    if periodicity != 0:
                        if fb_data_time <= start_time_count:
                            continue
                        elif (start_time_count <= fb_data_time <= (start_time_count +
                                                                 datetime.timedelta(
                                                                     days=periodicity))):
                            done_surveys += 1
                            conversion = (done_surveys * 100) // send_surveys
                            start_time_count += datetime.timedelta(days=periodicity)
                        elif (last_send_date+datetime.timedelta(days=1)) >= fb_data_time >= (start_time_count +
                                                                 datetime.timedelta(
                                                                     days=periodicity)):
                            dif_days = (fb_data_time - start_time_count).days
                            if dif_days != 0 and (dif_days % periodicity) == 0:
                                done_surveys += 1
                                conversion = (done_surveys * 100) // send_surveys
                                start_time_count += datetime.timedelta(days=dif_days + periodicity)
                            else:
                                continue
                        else:
                            continue
                    else:
                        if datetime.datetime.combine(end_time, send_time) >= fb_data_time >= start_time_count:
                            return 1, 1, 100
                        else:
                            continue
                return send_surveys, done_surveys, conversion
            else:
                return send_surveys, 0, 0
        else:
            if FeedBack.objects.filter(client__id=client_id, feedback_type=f'{survey_id}').exists():
                fb_obj = FeedBack.objects.filter(client__id=client_id, feedback_type=f'{survey_id}')
                start_time_count = datetime.datetime.combine(start_time, send_time)
                for fb in fb_obj:
                    fb_data_time = datetime.datetime.strptime(fb.data_time.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    if periodicity != 0:
                        if fb_data_time <= start_time_count:
                            continue
                        elif (start_time_count <= fb_data_time <= (start_time_count +
                                                                   datetime.timedelta(
                                                                       days=periodicity))):
                            done_surveys += 1
                            conversion = (done_surveys * 100) // send_surveys
                            start_time_count += datetime.timedelta(days=periodicity)
                        elif (last_send_date + datetime.timedelta(days=1)) >= fb_data_time >= (start_time_count +
                                                                                               datetime.timedelta(
                                                                                                   days=periodicity)):
                            dif_days = (fb_data_time - start_time_count).days
                            if dif_days != 0 and (dif_days % periodicity) == 0:
                                done_surveys += 1
                                conversion = (done_surveys * 100) // send_surveys
                                start_time_count += datetime.timedelta(days=dif_days + periodicity)
                            else:
                                continue
                        else:
                            continue
                    else:
                        if datetime.datetime.combine(end_time, send_time) >= fb_data_time >= start_time_count:
                            return 1, 1, 100
                        else:
                            continue
                return send_surveys, done_surveys, conversion
            else:
                return send_surveys, 0, 0
    except:
        return 0, 0, 0


def get_auto_survey_table(filter_data=None):
    timerun_survey = TimeRunSurvey.objects.filter().order_by("-id")
    clients = Clients.objects.all()
    filter_client, filter_client_code, status = None, None, None
    if filter_data:
        if 'auto_client_name' in filter_data:
            filter_client_name = Clients.objects.get(id=int(filter_data['auto_client_name'][0])).name
            clients = clients.filter(name=filter_client_name)
        if 'auto_client_code' in filter_data:
            filter_client_code = Clients.objects.get(id=int(filter_data['auto_client_code'][0])).client_code
            clients = clients.filter(client_code=filter_client_code)
        if 'servey_type' in filter_data:
            servey_type = CustomSurvey.objects.get(id=int(filter_data['servey_type'][0]))
            if timerun_survey.filter(survey=servey_type).exists():
                timerun_survey = timerun_survey.filter(survey=servey_type)
        if 'servey_status' in filter_data:
                status = str(filter_data['servey_status'][0])

    time_run_survey = {}
    for survey in timerun_survey:
        if status != None:
            if get_status(survey.end_time, survey.send_time, survey.periodicity, survey.last_send_date,
                          survey.is_active) == status:
                for client in clients:
                    if client in survey.clients.all():
                            send_surveys, done_surveys, conversion = get_count_surveys(survey.start_time, survey.end_time,
                                                                                       survey.survey.id, survey.periodicity,
                                                                                       client.id, survey.send_time,
                                                                                       survey.last_send_date)
                            time_run_survey[f"{survey.id},{client.id}"] = {"client": client,
                                                                           "survey": survey,
                                                                           "send_surveys": send_surveys,
                                                                           'done_surveys': done_surveys,
                                                                           'conversion': conversion,
                                                                           'status': get_status(survey.end_time,
                                                                                                survey.send_time,
                                                                                                survey.periodicity,
                                                                                                survey.last_send_date,
                                                                                                survey.is_active)}
        else:
            for client in clients:
                if client in survey.clients.all():
                        send_surveys, done_surveys, conversion = get_count_surveys(survey.start_time, survey.end_time,
                                                                                   survey.survey.id, survey.periodicity,
                                                                                   client.id, survey.send_time,
                                                                                   survey.last_send_date)
                        time_run_survey[f"{survey.id},{client.id}"] = {"client": client,
                                                                       "survey": survey,
                                                                       "send_surveys": send_surveys,
                                                                       'done_surveys': done_surveys,
                                                                       'conversion': conversion,
                                                                       'status': get_status(survey.end_time,
                                                                                            survey.send_time,
                                                                                            survey.periodicity,
                                                                                            survey.last_send_date,
                                                                                            survey.is_active)}
    return time_run_survey


def get_status(end_date, send_time, periodicity, last_send_date, is_active):
    end_time_count = datetime.datetime.combine(end_date, send_time)
    last_send_date = last_send_date.astimezone(timezone.utc).replace(tzinfo=None)
    if is_active:
        return 'active'
    else:
        if last_send_date >= (end_time_count - datetime.timedelta(days=(periodicity/2))):
            return 'not_active'
        else:
            return 'stopped'
