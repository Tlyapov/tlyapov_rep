import os
import traceback
import datetime
import pandas as pd
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout
import math
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages

from light_admin import settings
from web_app.utils import get_employee_clients, get_lust_rating_and_date, get_all_surveys_count, get_average_rating, \
    get_default_servery, get_rates_of_employee_count, get_task_date, get_task_count, get_all_tasks_count, clients_excel, \
    employees_excel, users_excel, surveys_and_reviews_excel, send_telegram_error, check_expired_date, get_clients_table, \
    get_clients_table_filters, surveys_and_reviews_filter, get_count_surveys, get_auto_survey_table
from clients.models import Clients
from CustomSurvey.models import CustomQuestion, CustomAnswers, CustomSurvey, TimeRunSurvey, FakeClientAnsers, \
    ClientAnswersToCustomSurvey, DeferredSurvey
from light_admin.settings import BASE_DIR
from traffic_light.models import FeedBack
from employees.models import Employees
from web_app.models import SurveyForm, SurveyFormAnswersAdded, SurveyFormAnswersCreated


def print_exception(e):
    stack = traceback.extract_stack()
    send_telegram_error(f"Error in '{stack[-2][2]}'. {e} \n" + str(traceback.print_exc(limit=5)))
    print(f"Error in '{stack[-2][2]}'. {e}")


def logout_user(request):
    try:
        logout(request)
        messages.success(request, "До свидания!")
        return redirect('clients/1')
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def clients_page(request, pg):
    try:
        media_url = settings.MEDIA_URL
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.role != 'employee' or user.is_superuser:
                    login(request, user)
                    messages.success(request, "Добро пожаловать!")
                    return redirect('clients', pg=1)
                else:
                    messages.error(request, "У вас нет доступа!")
            else:
                messages.error(request, "Что то пошло не так!")
                return redirect('clients', pg=1)

        passed_count, not_passed_count = get_all_surveys_count()
        filter_data = dict(request.GET)
        clients_table = get_clients_table(pg)
        answers={}
        client_rating = '-'
        done_surveys = 0
        exept_surveys = 0
        if len(filter_data) != 0:
            if 'select_date' in filter_data:
                clients_table = get_clients_table(pg, str(filter_data['select_date'][0]))
            if ('status_filter' in filter_data) or ('employee_filter' in filter_data):
                clients_table = get_clients_table_filters(pg, filter_data)
            if 'client' in filter_data:
                try:
                    client_obj = Clients.objects.get(id = int(filter_data['client'][0]))
                    for i in DeferredSurvey.objects.all().filter(client=client_obj):
                        if i.status == True:
                            done_surveys +=1
                        else:
                            exept_surveys +=1
                    answers_obj = FeedBack.objects.all().filter(answer__in=['🟢 Все нравится!','🟡 Есть вопросы.','🔴 Очень плохо ('],client=Clients.objects.get(id=int(filter_data['client'][0])))
                    answer_client = []
                    if 'fb_types' in filter_data:
                        feedbacks_obj = FeedBack.objects.all().filter(feedback_type=str(filter_data['fb_types'][0]),
                            client=Clients.objects.get(id=int(filter_data['client'][0]))).order_by("-id")
                    else:
                        feedbacks_obj = FeedBack.objects.all().filter(client=Clients.objects.get(id=int(filter_data['client'][0]))).order_by("-id")
                    for i in answers_obj:
                        answer_client.append(Clients.objects.get(id=int(filter_data['client'][0])))
                    rate = 0
                    count = 0
                    for i in answers_obj:
                        if i.answer == '🟢 Все нравится!':
                            rate +=3
                            count +=1
                        if i.answer == '🟡 Есть вопросы.':
                            rate += 2
                            count += 1
                        if i.answer == '🔴 Очень плохо (':
                            rate += 1
                            count += 1
                    if count != 0:
                        if rate/count > 2.5:
                            client_rating = 'Превосходно'
                        elif rate/count > 1.5:
                            client_rating = 'Нормально'
                        elif rate/count > 0:
                            client_rating = 'Плохо'
                    dic_task_date = []
                    for i in feedbacks_obj:
                        dic_task_date.append(get_task_date(i.id))
                    answers = zip(feedbacks_obj, dic_task_date)
                except:
                    answers = {}
        return render(request, 'clients.html',
                {"media_url": media_url,

                        "clients_table": clients_table,
                        "passed_count": passed_count,
                        "not_passed_count": not_passed_count,
                        "clients_count": Clients.objects.all().count,

                        "employees": Employees.objects.all(),
                        "answers": answers,
                        "done_surveys": done_surveys,
                        "exept_surveys": exept_surveys,
                        "client_rating": client_rating})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)



def employees_page(request, pg):
    try:
        tasks_count = get_all_tasks_count()
        average_rating = get_average_rating()
        employees = Employees.objects.all()[10 * (pg - 1): 10 * pg]
        dic_empl_clients_count = []
        dic_empl_perf_rate = []
        dic_empl_good_rate = []
        dic_empl_bad_rate = []
        dic_empl_feedback_count = []
        for i in employees:
            empl_perf_rate, empl_good_rate, empl_bad_rate, feedback_count, average_rating_by_empl = get_rates_of_employee_count(i.id)
            empl_clients_count = get_employee_clients(i.id)
            dic_empl_clients_count.append(empl_clients_count)
            dic_empl_perf_rate.append(empl_perf_rate)
            dic_empl_good_rate.append(empl_good_rate)
            dic_empl_bad_rate.append(empl_bad_rate)
            dic_empl_feedback_count.append(feedback_count)
        employee_table_list = zip(employees, dic_empl_clients_count, dic_empl_perf_rate, dic_empl_good_rate,
                                  dic_empl_bad_rate, dic_empl_feedback_count)
        filter_data = dict(request.GET)
        clients_employee = {}
        employee_clients_count = 0
        fb_by_employee = 0
        average_rating_by_empl = '-'
        if len(filter_data) != 0:
            if 'employee' in filter_data:
                try:
                    empl_perf_rate, empl_good_rate, empl_bad_rate, feedback_count , average_rating_by_empl= get_rates_of_employee_count(
                        int(filter_data['employee'][0]))
                    rate_count = empl_perf_rate + empl_good_rate + empl_bad_rate
                    if rate_count != 0:
                        average_rating_by_empl = (empl_perf_rate * 3 + empl_good_rate * 2 + empl_bad_rate) / rate_count
                        if average_rating_by_empl > 2.5:
                            average_rating_by_empl = 'Превосходно'
                        elif average_rating_by_empl > 1.5:
                            average_rating_by_empl = 'Нормально'
                        elif average_rating_by_empl > 0.5:
                            average_rating_by_empl = 'Плохо'
                    employee_obj = Employees.objects.get(id=int(filter_data['employee'][0]))
                    clients = Clients.objects.all().filter(employee=employee_obj)
                    dic_rating = []
                    dic_rating_date = []
                    dic_task_count = []

                    employee_clients_count = get_employee_clients(int(filter_data['employee'][0]))
                    for i in clients:
                        rating, date = get_lust_rating_and_date(i.id)
                        task_count = get_task_count(i.id)
                        fb_by_employee += task_count
                        dic_task_count.append(task_count)
                        dic_rating.append(rating)
                        dic_rating_date.append(date)
                    clients_employee = zip(clients, dic_rating, dic_rating_date, dic_task_count)
                except:
                    clients_employee = {}
        return render(request, 'employees.html',
                      {"employee_table_list": employee_table_list, "tasks_count": tasks_count,
                       "average_rating": average_rating, 'average_rating_by_empl':average_rating_by_empl, "employees_count": Employees.objects.filter(role='employee').count, "clients_employee":clients_employee, 'employee_clients_count':employee_clients_count, 'fb_by_employee':fb_by_employee})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def users_page(request, pg):
    try:
        tasks_count = get_all_tasks_count()
        average_rating = get_average_rating()
        employees = Employees.objects.all()[10 * (pg - 1): 10 * pg]
        dic_empl_clients_count = []
        dic_empl_perf_rate = []
        dic_empl_good_rate = []
        dic_empl_bad_rate = []
        dic_empl_feedback_count = []
        for i in employees:
            empl_perf_rate, empl_good_rate, empl_bad_rate, feedback_count, average_rating_by_empl = get_rates_of_employee_count(i.id)
            empl_clients_count = get_employee_clients(i.id)
            dic_empl_clients_count.append(empl_clients_count)
            dic_empl_perf_rate.append(empl_perf_rate)
            dic_empl_good_rate.append(empl_good_rate)
            dic_empl_bad_rate.append(empl_bad_rate)
            dic_empl_feedback_count.append(feedback_count)
        employee_table_list = zip(employees, dic_empl_clients_count, dic_empl_perf_rate, dic_empl_good_rate,
                                  dic_empl_bad_rate, dic_empl_feedback_count)
        filter_data = dict(request.GET)
        clients_employee = {}
        employee_clients_count = 0
        fb_by_employee = 0
        average_rating_by_empl = '-'
        if len(filter_data) != 0:
            if 'employee' in filter_data:
                try:
                    empl_perf_rate, empl_good_rate, empl_bad_rate, feedback_count, average_rating_by_empl = get_rates_of_employee_count(int(filter_data['employee'][0]))
                    employee_obj = Employees.objects.get(id=int(filter_data['employee'][0]))
                    clients = Clients.objects.all().filter(employee=employee_obj)
                    dic_rating = []
                    dic_rating_date = []
                    dic_task_count = []
                    employee_clients_count = get_employee_clients(int(filter_data['employee'][0]))
                    for i in clients:
                        rating, date = get_lust_rating_and_date(i.id)
                        task_count = get_task_count(i.id)
                        fb_by_employee += task_count
                        dic_task_count.append(task_count)
                        dic_rating.append(rating)
                        dic_rating_date.append(date)
                    clients_employee = zip(clients, dic_rating, dic_rating_date, dic_task_count)
                except:
                    clients_employee = {}
        return render(request, 'users.html', {"employee_table_list": employee_table_list, "tasks_count": tasks_count,
                                                  "average_rating": average_rating,'average_rating_by_empl':average_rating_by_empl, "employees_count": employees.count, 'clients_employee':clients_employee, 'employee_clients_count':employee_clients_count, 'fb_by_employee':fb_by_employee})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def surveys_and_reviews_page(request, pg):
    try:
        if request.user.is_authenticated:
            question_answers_added = []
            question_added = SurveyFormAnswersAdded.objects.filter(user=request.user)
            for question in question_added:
                answers = []
                for i in question.answer_variants.all():
                    answers.append(i.value)
                question_answers_added.append(answers)
            question_len_added = zip(question_added,question_answers_added)
            question_len_added_2 = zip(question_added,question_answers_added)
            if not (SurveyFormAnswersCreated.objects.filter(user=request.user).last()):
                SurveyFormAnswersCreated.objects.create(user=request.user)
            last_obj_created = SurveyFormAnswersCreated.objects.filter(user=request.user).last()
            question_created = SurveyFormAnswersCreated.objects.get(id=last_obj_created.id,user=request.user)
            answers = []
            for i in question_created.answer_variants.all():
                answers.append(i.value)
            surveys = CustomSurvey.objects.all()
            questions = CustomQuestion.objects.all()
            employees_to_filter = Employees.objects.all()
            add_guestions = CustomAnswers.objects.all()
            clients = Clients.objects.all()
            survey_clients = SurveyForm.objects.filter(user=request.user)
            survey_clients_2 = SurveyForm.objects.filter(user=request.user)
            filter_data = dict(request.GET)
            media_url = settings.MEDIA_URL
            if ('fb_types' in filter_data) and (str(filter_data['fb_types'][0]) == 'auto_survey'):
                time_run_survey = get_auto_survey_table(filter_data)
            else:
                time_run_survey = get_auto_survey_table()
            if len(filter_data) == 0:
                surveys_and_reviews = FeedBack.objects.filter().order_by("-id")[10 * (pg - 1): 10 * pg]
                h4_fb_type = "all"
            else:
                h4_fb_type = "all"
                if 'fb_types' in filter_data:
                    h4_fb_type = str(filter_data['fb_types'][0])
                surveys_and_reviews = surveys_and_reviews_filter(pg,filter_data)
            survey_clients_add = SurveyForm.objects.filter(user=request.user)
            dic_task_date = []
            for i in surveys_and_reviews:
                dic_task_date.append(get_task_date(i.id))
            surveys_and_reviews_table_list = zip(surveys_and_reviews, dic_task_date)
            surveys_and_reviews_table_list2 = zip(surveys_and_reviews, dic_task_date)
            return render(request, 'surveys_and_reviews.html', {'time_run_survey':time_run_survey, 'media_url':media_url,"surveys_and_reviews_table_list": surveys_and_reviews_table_list, 'question_created': question_created,'created_answers':answers, 'question_len_added': question_len_added, 'question_len_added_2': question_len_added_2, 'surveys_and_reviews_table_list2': surveys_and_reviews_table_list2, "surveys": surveys, 'clients': clients, 'survey_clients':survey_clients,  'questions':questions, 'add_guestions':add_guestions, 'survey_clients_add': survey_clients_add, 'h4_fb_type': h4_fb_type, 'survey_clients_2':survey_clients_2, 'employees_to_filter': employees_to_filter, 'employees_to_filter2': employees_to_filter})
        else:
            return redirect("clients", pg=1)
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)




def add_answer_to_new_survey(request):
    try:
        data = dict(request.POST)
        answer = data['answer'][0]
        last_obj = SurveyFormAnswersCreated.objects.filter(user=request.user).last()
        survey = SurveyFormAnswersCreated.objects.get(id=last_obj.id, user=request.user)
        answer = CustomAnswers.objects.get(id=int(answer))
        if not (answer in survey.answer_variants.all()):
            survey.answer_variants.add(answer)
        survey.save()
        messages.success(request, "Ответ добавлен!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def add_clients_to_survey(request):
    try:
        if request.method == "POST":
            SurveyForm.objects.filter(user=request.user).delete()
            data = request.POST.dict()
            clients_str = data['clients']
            clients = clients_str.split(",")
            if clients != ['']:
                for i in range(len(clients)):
                    clients[i] = int(clients[i])

                for i in clients:
                    try:
                        if not (SurveyForm.objects.all().filter(client=Clients.objects.get(id=i), user=request.user)):
                            SurveyForm.objects.create(client=Clients.objects.get(id=i), user=request.user)
                    except BaseException:
                            print(f"Ошибка добавления {i} пользователя")
            messages.success(request, "Пользователи добавлены!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def start_survey(request):
    try:
        data = dict(request.POST)
        survey = data['survey'][0]
        survey_obj = CustomSurvey.objects.get(id=survey)
        start_time = data['start_time'][0]
        end_time = data['end_time'][0]
        periodicity = data['periodicity'][0]
        is_active = data['is_active'][0]
        time_hour = data['time_hour'][0]
        run_survey = TimeRunSurvey.objects.create(
            survey=survey_obj,
            start_time=start_time,
            end_time=end_time,
            periodicity=periodicity,
            is_active=is_active,
            last_send_date = end_time,
            send_time = time_hour,
        )
        for i in SurveyForm.objects.filter(user=request.user):
            run_survey.clients.add(Clients.objects.get(id=i.client.id))
            SurveyForm.objects.filter(id=i.id,user=request.user).delete()
        messages.success(request, "Опрос инициирован!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)



def start_add_survey(request):
    try:
        data = dict(request.POST)
        survey_name = data['survey'][0]
        start_time = data['start_time'][0]
        end_time = data['end_time'][0]
        periodicity = data['periodicity'][0]
        is_active = data['is_active'][0]
        question_last = data['question'][0]
        time_hour = data['time_hour'][0]
        survey = CustomSurvey.objects.create(
            name=survey_name,
        )
        for i in SurveyFormAnswersAdded.objects.filter(user=request.user):
            question = CustomQuestion.objects.create(
                question=i.question
            )
            for j in i.answer_variants.all():
                question.answer_variants.add(j)
            survey.questions.add(question)
            survey.save()
            i.delete()
        for i in SurveyFormAnswersCreated.objects.filter(user=request.user):
            question = CustomQuestion.objects.create(
                question = question_last
            )
            for j in i.answer_variants.all():
                question.answer_variants.add(j)
            survey.questions.add(question)
            survey.save()
            i.delete()
        time_survey = TimeRunSurvey.objects.create(
            survey= survey,
            start_time=start_time,
            end_time=end_time,
            periodicity=periodicity,
            is_active=is_active,
            last_send_date = end_time,
            send_time = time_hour,
        )
        for i in SurveyForm.objects.filter(user=request.user):
            client = Clients.objects.get(id=i.client_id)
            time_survey.clients.add(client)
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def add_question(request):
    try:
        data = dict(request.POST)
        question = data['question'][0]
        last_obj_created = SurveyFormAnswersCreated.objects.filter(user=request.user).last()
        question_created = SurveyFormAnswersCreated.objects.get(id=last_obj_created.id, user=request.user)
        added_survey = SurveyFormAnswersAdded.objects.create(
            user=request.user,
            question=question,
        )
        for i in question_created.answer_variants.all():
            added_survey.answer_variants.add(i)
        question_created.delete()
        survey_obj = SurveyFormAnswersCreated.objects.create(user=request.user)
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)



def add_question_to_survey(request):
    try:
        if not SurveyFormAnswersCreated.objects.filter(user=request.user).last():
            data = dict(request.POST)
            survey_obj = SurveyFormAnswersCreated.objects.create(user=request.user)
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)



def delete_question(request):
    try:
        if SurveyFormAnswersAdded.objects.filter(user=request.user).last():
            last_obj = SurveyFormAnswersCreated.objects.filter(user=request.user).last()
            SurveyFormAnswersCreated.objects.get(id=last_obj.id,user=request.user).delete()
            last_add_obj = SurveyFormAnswersAdded.objects.filter(user=request.user).last()
            added_survey = SurveyFormAnswersAdded.objects.get(id=last_add_obj.id,user=request.user)
            created_survey = SurveyFormAnswersCreated.objects.create(
                user=request.user,
                question=str(last_add_obj.question),
            )
            for i in added_survey.answer_variants.all():
                created_survey.answer_variants.add(i)
            SurveyFormAnswersAdded.objects.get(id=last_add_obj.id,user=request.user).delete()
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)

def delete_question_all(request):
    try:
        SurveyFormAnswersCreated.objects.filter(user=request.user).delete()
        SurveyFormAnswersAdded.objects.filter(user=request.user).delete()
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def tasks(request, pg):
    try:
        clients = Clients.objects.all()
        employees = Employees.objects.all()
        filter_data = dict(request.GET)
        employees_to_filter = Employees.objects.all()
        if len(filter_data) == 0:
            tasks = FeedBack.objects.filter().order_by("-id")
        else:
            if 'is_expired' in filter_data:
                is_expired = []
                for i in FeedBack.objects.all():
                    if check_expired_date(i.id):
                        is_expired.append(i.id)
                tasks = FeedBack.objects.filter(id__in=is_expired).order_by("-id")
            else:
                tasks = FeedBack.objects.filter().order_by("-id")
            if 'pr_status' in filter_data:
                pr_status_data = str(filter_data['pr_status'][0])
                if 'employee' in filter_data:
                    employee_data = str(filter_data['employee'][0])
                    if 'supervisor' in filter_data:
                        supervisor_data = str(filter_data['supervisor'][0])
                        tasks = tasks.filter(progress_status=pr_status_data,
                                                                         employee=employee_data,
                                                                         supervisor=supervisor_data)
                    else:
                        tasks = tasks.filter(progress_status=pr_status_data,
                                            employee=employee_data)
                elif 'supervisor' in filter_data:
                    supervisor_data = str(filter_data['supervisor'][0])
                    tasks = tasks.filter(progress_status=pr_status_data,
                                        supervisor=supervisor_data)
                else:
                    tasks = tasks.filter(progress_status=pr_status_data)
            elif 'employee' in filter_data:
                employee_data = str(filter_data['employee'][0])
                if 'supervisor' in filter_data:
                    supervisor_data = str(filter_data['supervisor'][0])
                    tasks = tasks.filter(employee=employee_data,
                                        supervisor=supervisor_data)
                else:
                    tasks = tasks.filter(employee=employee_data)
            elif 'employee' in filter_data:
                supervisor_data = str(filter_data['supervisor'][0])
                tasks = tasks.filter(supervisor=supervisor_data)
        media_url = settings.MEDIA_URL
        dic_task_date = []
        dic_expired_date = []
        for i in tasks[10 * (pg - 1): 10 * pg]:
            dic_task_date.append(get_task_date(i.id))
            dic_expired_date.append(check_expired_date(i.id))
        tasks_table_list = zip(tasks, dic_task_date, dic_expired_date)
        return render(request, 'tasks.html', {'media_url':str(media_url),"tasks_table_list": tasks_table_list, "clients": clients, "employees": employees, 'employees_to_filter': employees_to_filter, 'employees_to_filter2':employees_to_filter})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)

def add_client(request):
    try:
        data = dict(request.POST)
        client_code = data['client_code'][0]
        full_name = data['full_name'][0]
        company_name = data['company_name'][0]
        job_title = data['job_title'][0]
        employee = data['employee'][0]
        employee_obj = Employees.objects.get(id=int(employee))
        phone = data['phone'][0]
        tg_id = data['tg_id'][0]
        tg_id = tg_id.replace('@','')
        client = Clients.objects.create(
            employee=employee_obj,
            phone=phone,
            client_code=client_code,
            job_title=job_title,
            company_name=company_name,
            name=full_name,
            tg_id=tg_id,
        )
        messages.success(request, "Клиент добавлен!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def get_one_client(request):
    try:
        pk = int(dict(request.GET)['pk'][0])
        client = Clients.objects.get(id=pk)
        client_dict = {}
        if client.client_code != None:
            client_dict['client_code'] = client.client_code
        else:
            client_dict['client_code'] = 0
        if client.name != None:
            client_dict['full_name'] = client.name
        else:
            client_dict['full_name'] = ''
        if client.company_name != None:
            client_dict['company_name'] = client.company_name
        else:
            client_dict['company_name'] = ''
        if client.employee != None:
            client_dict['employee'] = client.employee.id
        else:
            client_dict['employee'] = 0
        if client.job_title != None:
            client_dict['job_title'] = client.job_title
        else:
            client_dict['job_title'] = ''
        if client.phone != None:
            client_dict['phone'] = client.phone
        else:
            client_dict['phone'] = ''
        if client.tg_id != None:
            client_dict['tg_id'] = f"@{client.tg_id}"
        else:
            client_dict['tg_id'] = ''
        return JsonResponse(client_dict)
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def update_client_view(request):
    try:
        data = dict(request.POST)
        pk = int(data['pk'][0])
        client_code = data['client_code'][0]
        name = data['name'][0]
        company_name = data['company_name'][0]
        employee = data['employee'][0]
        employee_obj = Employees.objects.get(id=int(employee))
        job_title = data['job_title'][0]
        phone = data['phone'][0]
        tg_id = data['tg_id'][0]
        tg_id = tg_id.replace('@','')
        client = Clients.objects.get(id=pk)

        client.client_code = client_code
        client.name = name
        client.company_name = company_name
        client.employee = employee_obj
        client.job_title = job_title
        client.phone = phone
        client.tg_id = tg_id
        client.save()
        messages.success(request, "Клиент сохранен!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)



def delete_client_btn(request):
    try:
        if request.method == "POST":
            data = request.POST.dict()
            client_id = data['client_id']
            client = Clients.objects.get(id=client_id)
            client.delete()
        messages.success(request, "Клиент удален!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def add_employee(request):
    try:
        data = dict(request.POST)
        if Employees.objects.filter(username=data['login'][0]).exists():
            return messages.error(request, "Укажите уникальный логин")
        else:
            name = data['name'][0]
            surname = data['surname'][0]
            login = data['login'][0]
            password = data['password'][0]
            confirm_password = data['confirm_password'][0]
            tg_id = data['tg_id'][0]
            tg_id = tg_id.replace('@','')
            phone = data['phone'][0]
            role = data['role'][0]
            job_title = data['job_title'][0]
            if str(password) != str(confirm_password):
                return messages.error(request, "Пароли должны совпадать!")
            employee = Employees.objects.create(
                name=name,
                surname=surname,
                username=login,
                tg_id=tg_id,
                phone=phone,
                role=role,
                job_title=job_title,
            )
            employee.set_password(str(password))
            employee.save()
            messages.success(request, "Сотрудник добавлен!")
            return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)



def get_one_employee(request):
    try:
        pk = int(dict(request.GET)['pk'][0])
        employee = Employees.objects.get(id=pk)
        employee_dict = {}
        if employee.name != None or employee.name != 'Nan':
            employee_dict['name'] = employee.name
        else:
            employee_dict['name'] = ''
        if employee.surname != None or employee.surname != 'Nan':
            employee_dict['surname'] = employee.surname
        else:
            employee_dict['surname'] = ''
        if employee.username != None or employee.username != 'Nan':
            employee_dict['login'] = employee.username
        else:
            employee_dict['login'] = ''
        if employee.password != None or employee.password != 'Nan':
            employee_dict['password'] = employee.password
        else:
            employee_dict['password'] = 0
        if employee.tg_id != None or employee.tg_id != 'Nan':
            employee_dict['tg_id'] = f"@{employee.tg_id}"
        else:
            employee_dict['tg_id'] = 0
        if employee.phone != None or employee.phone != 'Nan':
            employee_dict['phone'] = employee.phone
        else:
            employee_dict['phone'] = 0
        if employee.role != None or employee.role != 'Nan':
            employee_dict['role'] = employee.role
        else:
            employee_dict['role'] = ''
        if employee.job_title != None or employee.job_title != 'Nan':
            employee_dict['job_title'] = employee.job_title
        else:
            employee_dict['job_title'] = ''
        return JsonResponse(employee_dict)
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def update_employee_view(request):
    try:
        data = dict(request.POST)
        pk = int(data['pk'][0])
        name = data['name'][0]
        surname = data['surname'][0]
        login = data['login'][0]
        password = data['password'][0]
        confirm_password = data['confirm_password'][0]
        tg_id = data['tg_id'][0]
        tg_id = tg_id.replace('@','')
        phone = data['phone'][0]
        role = data['role'][0]
        job_title = data['job_title'][0]
        employee = Employees.objects.get(id=pk)
        if password != confirm_password:
            messages.error(request, "Пароли должны совпадать!")
            return JsonResponse({"message": "success"})
        employee.name = name
        employee.surname = surname
        employee.login = login
        employee.set_password(str(password))
        employee.tg_id = tg_id
        employee.phone = phone
        employee.role = role
        employee.job_title = job_title
        employee.save()
        messages.success(request, "Сотрудник сохранен!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def delete_employee_btn(request):
    try:
        if request.method == "POST":
            data = request.POST.dict()
            employee_id = data['employee_id']
            employee = Employees.objects.get(id=employee_id)
            employee.delete()
        messages.success(request, "Сотрудник удален!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def add_task(request):
    try:
        data = dict(request.POST)
        feedback_type = data['feedback_type'][0]
        client = data['client'][0]
        client_obj = Clients.objects.get(id=int(client))
        start_date = data['start_date'][0]
        period_len_by_days = data['period_len_by_days'][0]
        end_data_time = f"{str(start_date).split('-')[0]}-{str(start_date).split('-')[1]}-{int(str(start_date).split('-')[2])+int(period_len_by_days)}"
        progress_status = data['progress_status'][0]
        employee = data['employee'][0]
        employee_obj = Employees.objects.get(id=int(employee))
        answer = data['answer'][0]
        if client_obj.employee:
            supervisor=client_obj.employee.id
        else:
            supervisor = ''
        task = FeedBack.objects.create(
            feedback_type=feedback_type,
            client=client_obj,
            data_time=start_date,
            progress_status=progress_status,
            employee=employee_obj,
            answer=answer,
            is_light=False,
            light_answer='',
            supervisor=supervisor,
            status=False,
            by_employee='',
            feedback_id='',
            end_data_time=end_data_time,
        )
        messages.success(request, "Сотрудник добавлен!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def get_one_task(request):
    try:
        pk = int(dict(request.GET)['pk'][0])
        task = model_to_dict(FeedBack.objects.get(id=pk))
        task['data_time'] = task['data_time'].split(' ')[0]
        if task['is_light'] == True:
            date = datetime.datetime.strptime(
                f"{int(str(task['data_time']).split('-')[2])}.{str(task['data_time']).split('-')[1]}.{str(task['data_time']).split('-')[0]}",
                '%d.%m.%Y')
            date = date + datetime.timedelta(days=1)
        else:
            date = datetime.datetime.strptime(
                f"{int(str(task['data_time']).split('-')[2])}.{str(task['data_time']).split('-')[1]}.{str(task['data_time']).split('-')[0]}",
                '%d.%m.%Y')
            date = date + datetime.timedelta(days=5)
        task['end_data_time'] = str(date).split(' ')[0]
        return JsonResponse(task)
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)



def update_task_view(request):
    try:
        data = dict(request.POST)
        pk = int(data['pk'][0])
        task = FeedBack.objects.get(id=pk)
        feedback_type = data['feedback_type'][0]
        client = data['client'][0]
        client_obj = Clients.objects.get(id=int(client))
        data_time = data['data_time'][0]
        employee = data['employee'][0]
        if employee != '':
            employee_obj = Employees.objects.get(id=int(employee))
            task.employee = employee_obj
        answer = data['answer'][0]
        report = data['report'][0]
        end_data_time = data['end_data_time'][0]
        progress_status = data['progress_status'][0]
        task.feedback_type = feedback_type
        task.client = client_obj
        task.data_time = data_time
        task.answer = answer
        task.report = report
        task.end_data_time = end_data_time
        task.progress_status = progress_status
        task.save()
        messages.success(request, "Задача сохранена!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def delete_task_btn(request):
    try:
        if request.method == "POST":
            data = request.POST.dict()
            task_id = data['task_id']
            task = FeedBack.objects.get(id=task_id)
            task.delete()
        messages.success(request, "Задача удалена!")
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)

def get_pagination_for_client(request):
    try:
        pagination_count = math.ceil(len(Clients.objects.all()) / 10)
        if pagination_count == 0:
            pagination_count = 1
        if request.user.is_authenticated:
            return JsonResponse({"pagination_count": pagination_count}, status=200)
        else:
            messages.success(request, "Войдите в систему!")
            return redirect("clients", pg=1)
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def get_pagination_for_employee(request):
    try:
        pagination_count = math.ceil(len(Employees.objects.filter(role='employee')) / 10)
        if pagination_count == 0:
            pagination_count = 1
        if request.user.is_authenticated:
            return JsonResponse({"pagination_count": pagination_count}, status=200)
        else:
            messages.success(request, "Войдите в систему!")
            return redirect("clients", pg=1)
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def get_pagination_for_user(request):
    try:
        pagination_count = math.ceil(len(Employees.objects.filter(role='user')) / 10)
        if pagination_count == 0:
            pagination_count = 1
        if request.user.is_authenticated:
            return JsonResponse({"pagination_count": pagination_count}, status=200)
        else:
            messages.success(request, "Войдите в систему!")
            return redirect("clients", pg=1)
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def get_pagination_for_task(request):
    try:
        pagination_count = math.ceil(len(FeedBack.objects.all()) / 10)
        if pagination_count == 0:
            pagination_count = 1
        if request.user.is_authenticated:
            return JsonResponse({"pagination_count": pagination_count}, status=200)
        else:
            messages.success(request, "Войдите в систему!")
            return redirect("clients", pg=1)
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def get_pagination_for_surveys_and_reviews(request):
    try:
        pagination_count = math.ceil(len(FeedBack.objects.all()) / 10)
        if pagination_count == 0:
            pagination_count = 1
        if request.user.is_authenticated:
            return JsonResponse({"pagination_count": pagination_count}, status=200)
        else:
            messages.success(request, "Войдите в систему!")
            return redirect("clients", pg=1)
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def download_clients_excel(request):
    try:
        response = clients_excel()
        return response
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def download_employees_excel(request):
    try:
        response = employees_excel()
        return response
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)



def download_users_excel(request):
    try:
        response = users_excel()
        return response
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)



def download_reviews_excel(request, date):
    try:
        select_date, select_date_2 = None, None
        for i in date.split('&'):
            if 'select_date=' in f"{i}":
                select_date = str(i).split('select_date=')[1]
            if 'select_date_2=' in f"{i}":
                select_date_2 = str(i).split('select_date_2=')[1]
        if 'select_date=' in date:
            date = {'select_date': select_date,
                    'select_date_2': select_date_2}
        response = surveys_and_reviews_excel(date)
        return response
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def get_light_survey(request):
    try:
        SurveyFormAnswersAdded.objects.filter(user=request.user).delete()
        SurveyFormAnswersCreated.objects.filter(user=request.user).delete()
        id_survey = get_default_servery()
        survey_obj = CustomSurvey.objects.get(id=id_survey)
        count = int(survey_obj.questions.all().count())
        for i in survey_obj.questions.all():
            if count > 1:
                question_get = CustomQuestion.objects.get(id=i.id)
                survey_added = SurveyFormAnswersAdded.objects.create(
                    user=request.user,
                    question = question_get.question
                )
                for j in i.answer_variants.all():
                    answer = CustomAnswers.objects.get(id=j.id)
                    survey_added.answer_variants.add(answer)
                count -=1
            else:
                question_get = CustomQuestion.objects.get(id=i.id)
                survey_added = SurveyFormAnswersCreated.objects.create(
                    user=request.user,
                    question = question_get.question
                )
                for j in i.answer_variants.all():
                    answer = CustomAnswers.objects.get(id=j.id)
                    survey_added.answer_variants.add(answer)
                count -=1
        return JsonResponse({"survey": str(survey_obj.name)})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def reset_clients(request):
    try:
        SurveyForm.objects.filter(user=request.user).delete()
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def reset_answers(request):
    try:
        SurveyFormAnswersCreated.objects.filter(user=request.user).delete()
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def change_light_survey(request):
    try:
        data = dict(request.POST)
        survey_name = data['survey'][0]
        question_last = data['question'][0]
        survey_id = get_default_servery()
        survey = CustomSurvey.objects.get(id=survey_id)
        survey.name = str(survey_name)
        survey = CustomSurvey.objects.get(id=survey_id)
        survey.name=survey_name
        survey.questions.all().delete()
        for i in SurveyFormAnswersAdded.objects.filter(user=request.user):
            question = CustomQuestion.objects.create(
                question=i.question
            )
            for j in i.answer_variants.all():
                question.answer_variants.add(j)
            survey.questions.add(question)
            survey.save()
            i.delete()
        for i in SurveyFormAnswersCreated.objects.filter(user=request.user):
            question = CustomQuestion.objects.create(
                question=question_last
            )
            for j in i.answer_variants.all():
                question.answer_variants.add(j)
            survey.questions.add(question)
            survey.save()
            i.delete()

        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


def stop_auto_survey(request):
    try:
        data = dict(request.POST)
        print(data)
        auto_survey = TimeRunSurvey.objects.get(id=int(data['survey_id'][0]))
        auto_survey.is_active = False
        auto_survey.save()
        return JsonResponse({"message": "success"})
    except BaseException as e:
        print(traceback.print_exc(limit=5))
        messages.error(request, "Что то пошло не так...")
        print_exception(e)


