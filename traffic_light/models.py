

from django.db import models
from clients.models import Clients
from employees.models import Employees
from django.utils import timezone

from light_admin.settings import BASE_DIR, MEDIA_ROOT


class Reviews(models.Model):
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ["id"]

    client = models.ForeignKey(Clients, on_delete=models.CASCADE, verbose_name="Клиент")
    answer = models.TextField(default="", null=True, blank=True, verbose_name="Отзыв")

class ReviewsByEmployee(models.Model):
    class Meta:
        verbose_name = 'Отзыв о сотруднике'
        verbose_name_plural = 'Отзывы о сотруднике'
        ordering = ["id"]

    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, verbose_name="Сотрудник")
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, verbose_name="Клиент")
    answer = models.TextField(default="", null=True, blank=True, verbose_name="Отзыв о сотруднике")


class Offers(models.Model):
    class Meta:
        verbose_name = 'Предложение'
        verbose_name_plural = 'Предложения'
        ordering = ["id"]
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, verbose_name="Клиент")
    answer = models.TextField(default="", null=True, blank=True, verbose_name="Предложение")



class Audio(models.Model):
    class Meta:
        verbose_name = 'Аудио'
        verbose_name_plural = 'Аудио'
        ordering = ["id"]

    audio_answer = models.FileField(upload_to='audio', blank=True)



class FeedBack(models.Model):
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ["id"]

    pr_status = [
        ("not_taken", "Не взят в работу"),
        ("in_progress", "В работе"),
        ("done", "Выполнено")
    ]

    fb_types = [
        ("review", "Отзыв общий"),
        ("survey", "Опрос"),
        ("review_by_employee", "Отзыв о сотруднике"),
        ("light", "Светофор"),
        ("light_by_employee", "Светофор по сотруднику"),
        ("offer","Предложение")
    ]
    client = models.ForeignKey(Clients, on_delete=models.CASCADE, verbose_name="Клиент")
    answer = models.TextField(default="", null=True, blank=True, verbose_name="Отзыв")
    audio_answer = models.ForeignKey(Audio, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Аудио")
    is_light = models.BooleanField(default=False, null=True, blank=True, verbose_name="Переход из светофора")
    light_answer = models.CharField(default="", max_length=150,  null=True, blank=True, verbose_name="Оценка светофор")
    supervisor = models.CharField(default="", max_length=150, null=True, blank=True, verbose_name="Ответственный руководитель")
    employee = models.ForeignKey(Employees, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Исполнитель")
    status = models.BooleanField(default=False, null=True, blank=True, verbose_name="Сделано?")
    progress_status = models.CharField(max_length=11, choices=pr_status, default="not_taken", verbose_name="Статус выполнения")
    by_employee = models.CharField(default="", max_length=150, null=True, blank=True, verbose_name="По сотруднику")
    feedback_type = models.CharField(max_length=18, choices=fb_types, default="", verbose_name="Тип FeedBack")
    feedback_id = models.CharField(default="", max_length=150,  null=True, blank=True, verbose_name="Id feedback")
    data_time = models.CharField(default="", max_length=150, null=True, blank=True, verbose_name="Дата постановки")
    report = models.TextField(default="", null=True, blank=True, verbose_name="Отчёт")
    end_data_time = models.CharField(default="", max_length=150, null=True, blank=True, verbose_name="Дата выполнения")
    get_req = models.CharField(default="", max_length=250, null=True, blank=True, verbose_name="get запрос голосовой")


