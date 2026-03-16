from django.db import models
from employees.models import Employees


class Clients(models.Model):
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ["id"]

    employee = models.ForeignKey(Employees, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Сотрудник")
    phone = models.CharField(max_length=25, unique=True, null=True, blank=False, verbose_name="Номер телефона")
    client_code = models.CharField(max_length=25, null=True, blank=True, verbose_name="Код клиента")
    job_title = models.CharField(max_length=100, null=True, blank=True, verbose_name="Должность")
    company_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Название компании")
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Имя")
    tg_id = models.CharField(max_length=150, null=True, blank=True, verbose_name="Телеграм ID")
    chat_id = models.CharField(max_length=150, null=True, blank=True, verbose_name="Телеграм ID")

    def __str__(self):
        return f"{self.name} {self.company_name}"






