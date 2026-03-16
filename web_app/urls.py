from django.urls import path
from . import views
urlpatterns = [
    path('', views.logout_user, name="logout"),


    path('clients/<int:pg>', views.clients_page, name='clients'),
    path("add_client/", views.add_client, name="add_client"),
    path("get_one_client/", views.get_one_client, name="get_one_client"),
    path("delete_client_btn/", views.delete_client_btn, name="delete_client_btn"),
    path("update_client_view/", views.update_client_view, name="update_client_view"),
    path("download_clients_excel/", views.download_clients_excel, name="download_clients_excel"),
    path("get_pagination_for_client/", views.get_pagination_for_client, name="get_pagination_for_client"),


    path('employees/<int:pg>', views.employees_page, name='employees'),
    path("add_employee/", views.add_employee, name="add_employee"),
    path("get_one_employee/", views.get_one_employee, name="get_one_employee"),
    path("update_employee_view/", views.update_employee_view, name="update_employee_view"),
    path("delete_employee_btn/", views.delete_employee_btn, name="delete_employee_btn"),
    path("download_employees_excel/", views.download_employees_excel, name="download_employees_excel"),
    path("get_pagination_for_employee/", views.get_pagination_for_employee, name="get_pagination_for_employee"),

    path('users/<int:pg>', views.users_page, name='users'),
    path("download_users_excel/", views.download_users_excel, name="download_users_excel"),
    path("get_pagination_for_user/", views.get_pagination_for_user, name="get_pagination_for_user"),


    path('surveys_and_reviews/<int:pg>', views.surveys_and_reviews_page, name='surveys_and_reviews'),
    path("add_clients_to_survey/", views.add_clients_to_survey, name="add_clients_to_survey"),
    path("start_survey/", views.start_survey, name="start_survey"),
    path("start_add_survey/", views.start_add_survey, name="start_add_survey"),
    path("add_answer_to_new_survey/", views.add_answer_to_new_survey, name="add_answer_to_new_survey"),
    path("add_question/", views.add_question, name="add_question"),
    path("add_question_to_survey/", views.add_question_to_survey, name="add_question_to_survey"),
    path("delete_question_all/", views.delete_question_all, name="delete_question_all"),
    path("delete_question/", views.delete_question, name="delete_question"),
    path("download_reviews_excel/<str:date>", views.download_reviews_excel, name="download_reviews_excel"),
    path("get_pagination_for_surveys_and_reviews/", views.get_pagination_for_surveys_and_reviews,
         name="get_pagination_for_surveys_and_reviews"),
    path("get_light_survey/", views.get_light_survey, name="get_light_survey"),
    path("change_light_survey/", views.change_light_survey, name="change_light_survey"),
    path("reset_clients/", views.reset_clients, name="reset_clients"),
    path("reset_answers/", views.reset_answers, name="reset_answers"),
    path("stop_auto_survey/", views.stop_auto_survey, name="stop_auto_survey"),


    path('tasks/<int:pg>', views.tasks, name='tasks'),
    path("add_task/", views.add_task, name="add_task"),
    path("get_one_task/", views.get_one_task, name="get_one_task"),
    path("update_task_view/", views.update_task_view, name="update_task_view"),
    path("delete_task_btn/", views.delete_task_btn, name="delete_task_btn"),
    path("get_pagination_for_task/", views.get_pagination_for_task, name="get_pagination_for_task"),
    ]