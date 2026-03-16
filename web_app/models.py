from django.db import models

from CustomSurvey.models import CustomAnswers
from clients.models import Clients
from employees.models import Employees


class SurveyForm(models.Model):
    class Meta:
        verbose_name = 'Список клиентов'
        ordering = ["id"]

    user = models.ForeignKey(Employees, default=None, on_delete=models.CASCADE, verbose_name="User")
    client = models.ForeignKey(Clients, on_delete=models.PROTECT, verbose_name="Клиент")



class SurveyFormAnswersAdded(models.Model):
    class Meta:
        verbose_name = 'Список вопросов(добавленные)'
        ordering = ["id"]

    user = models.ForeignKey(Employees, default=None, on_delete=models.CASCADE, verbose_name="User")
    question = models.TextField(default="", blank=True, null=True, verbose_name="Вопрос")
    answer_variants = models.ManyToManyField(CustomAnswers, verbose_name="Варианты ответов")



class SurveyFormAnswersCreated(models.Model):
    class Meta:
        verbose_name = 'Список вопросов(созданные)'
        ordering = ["id"]

    user = models.ForeignKey(Employees, default=None, on_delete=models.CASCADE, verbose_name="User")
    question = models.TextField(default="", blank=True, null=True, verbose_name="Вопрос")
    answer_variants = models.ManyToManyField(CustomAnswers, verbose_name="Варианты ответов")

