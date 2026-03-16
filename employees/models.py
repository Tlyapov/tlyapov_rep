import traceback

from django.db import models
from django.utils import timezone
from clients.models import Clients
from django.contrib import admin
from jinja2 import Template
from django.utils.html import format_html


class CustomAnswers(models.Model):
    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        ordering = ["id"]

    value = models.CharField(default="", max_length=250, null=True, blank=True, verbose_name="Значение")

    def __str__(self):
        return f"{self.value}"


class CustomQuestion(models.Model):
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ["id"]

    question = models.TextField(default="", blank=True, null=True, verbose_name="Вопрос")
    answer_variants = models.ManyToManyField(CustomAnswers, verbose_name="Варианты ответов")

    def __str__(self):
        return f"{self.question}"




class CustomSurvey(models.Model):
    class Meta:
        verbose_name = 'Опрос'
        verbose_name_plural = 'Опросы'
        ordering = ["id"]

    # all_clients = models.BooleanField(default=True, null=True, blank=True, verbose_name="Все клиенты")
    name = models.CharField(default="", max_length=250, null=True, blank=True, verbose_name="Название опроса")
    questions = models.ManyToManyField(CustomQuestion, verbose_name="Вопросы")
    is_light = models.BooleanField(default=False, verbose_name="Стандартный опрос")

    def __str__(self):
        return f"{self.name}"


class ClientAnswersToCustomSurvey(models.Model):
    class Meta:
        verbose_name = 'Ответ клиента'
        verbose_name_plural = 'Ответы клиента'
        ordering = ["id"]

    survey = models.ForeignKey(CustomSurvey, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Опрос")
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Клиент")

    def __str__(self):
        return f"{self.survey} {self.client}"

    @admin.display
    def DisplayClientAnswers(self):
        answers = FakeClientAnsers.objects.all().filter(all_answers=self)
        link = '''<div>{% for o in answers -%}
                <div style="margin-top: 15px !important">
                    <h2>{{o["question"]}}</h2>
                    <div style="margin-top: 5px"> {{o["answer"]}}</div>
                </div>
                {% endfor -%}</div>'''
        tm = Template(link)
        html_text = tm.render(answers=answers)
        return format_html(html_text)
    DisplayClientAnswers.short_description = f"Ответы"


class FakeClientAnsers(models.Model):
    class Meta:
        verbose_name = 'Ответ клиента(many)'
        verbose_name_plural = 'Ответы клиента(many)'
        ordering = ["id"]

    question = models.ForeignKey(CustomQuestion, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Вопрос")
    answer = models.ForeignKey(CustomAnswers, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Ответ")
    all_answers = models.ForeignKey(ClientAnswersToCustomSurvey, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Ответы на опрос")
    create_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.question}"


class TimeRunSurvey(models.Model):
    class Meta:
        verbose_name = 'Автоматический опрос'
        verbose_name_plural = 'Автоматические опросы'
        ordering = ["id"]

    clients = models.ManyToManyField(Clients, null=True, blank=True, verbose_name="Клиенты")
    survey = models.ForeignKey(CustomSurvey, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Опрос")
    all_clients = models.BooleanField(default=False, null=True, blank=True, verbose_name="Все клиенты?")
    start_time = models.DateField(default=timezone.now, null=True, blank=True, verbose_name="Дата начала")
    end_time = models.DateField(default=timezone.now, null=True, blank=True, verbose_name="Дата завершения")
    periodicity = models.IntegerField(default=0, null=True, blank=True,
                                      verbose_name="Периодичность(в днях)",
                                      help_text="Если периодичность равна нулю, то опрос будет отправлен один раз")
    is_active = models.BooleanField(default=True, null=True, blank=True, verbose_name="Активен")
    last_send_date = models.DateTimeField(default=None, null=True, blank=True, verbose_name="Дата последней отправки")
    send_time = models.TimeField(default=timezone.now, null=True, blank=True, verbose_name="Время отправки")


class DeferredSurvey(models.Model):
    class Meta:
        verbose_name = 'Отложенный опрос'
        verbose_name_plural = 'Отложенные опросы'
        ordering = ["id"]

    client = models.ForeignKey(Clients, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Клиент")
    survey = models.ForeignKey(CustomSurvey, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Опрос")
    status = models.BooleanField(default=False, null=True, blank=True, verbose_name="Пройден")

