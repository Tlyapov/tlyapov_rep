from django.contrib import admin
from .models import  Reviews, FeedBack, ReviewsByEmployee, Offers
from django_object_actions import DjangoObjectActions, action
import django_excel as excel
from clients.models import Clients
from employees.models import Employees
from CustomSurvey.admin import BooleanDefaultNoFilter
from django.utils.translation import gettext_lazy as _


class FeedbackFilter_is_light(BooleanDefaultNoFilter):
    title = _('Переход из светофора')
    parameter_name = 'is_light'


class FeedbackFilter_status(BooleanDefaultNoFilter):
    title = _('Сделано')
    parameter_name = 'status'




@admin.register(Reviews)
class ReviewsAmin(DjangoObjectActions, admin.ModelAdmin):
    def export_to_xls(self, request, obj):
        query_record = Reviews.objects.all().values()
        return_list = list(query_record)
        for i in return_list:
            i["client_id"] = Clients.objects.all().get(pk=i["client_id"]).__str__()

        ret_list = []
        ret_list.append(return_list[0].keys())
        for i in return_list:
            ret_list.append(i.values())
        print(return_list)
        return excel.make_response_from_array(
            ret_list,
            file_type="xlsx",
            file_name="Reviews"
        )
    list_display = ('client', 'answer')
    readonly_fields = ('client', 'answer')
    search_fields = ("client__name",)
    export_to_xls.label = "Экспорт в Excel"
    changelist_actions = ('export_to_xls',)


@admin.register(ReviewsByEmployee)
class ReviewsByEmployeeAmin(DjangoObjectActions, admin.ModelAdmin):
    def export_to_xls(self, request, obj):
        query_record = ReviewsByEmployee.objects.all().values()
        return_list = list(query_record)
        for i in return_list:
            i["client_id"] = Clients.objects.all().get(pk=i["client_id"]).__str__()
            i["employee_id"] = Employees.objects.all().get(pk=i["employee_id"]).__str__()

        ret_list = []
        ret_list.append(return_list[0].keys())
        for i in return_list:
            ret_list.append(i.values())
        print(return_list)
        return excel.make_response_from_array(
            ret_list,
            file_type="xlsx",
            file_name="ReviewsByEmployee"
        )
    list_display = ('client','employee', 'answer')
    readonly_fields = ('client','employee', 'answer')
    search_fields = ("client__name",)
    export_to_xls.label = "Экспорт в Excel"
    changelist_actions = ('export_to_xls',)



@admin.register(Offers)
class OffersAmin(DjangoObjectActions, admin.ModelAdmin):
    def export_to_xls(self, request, obj):
        query_record = Offers.objects.all().values()
        return_list = list(query_record)
        for i in return_list:
            i["client_id"] = Clients.objects.all().get(pk=i["client_id"]).__str__()

        ret_list = []
        ret_list.append(return_list[0].keys())
        for i in return_list:
            ret_list.append(i.values())
        print(return_list)
        return excel.make_response_from_array(
            ret_list,
            file_type="xlsx",
            file_name="Reviews"
        )
    list_display = ('client', 'answer')
    readonly_fields = ('client', 'answer')
    search_fields = ("client__name",)
    export_to_xls.label = "Экспорт в Excel"
    changelist_actions = ('export_to_xls',)


@admin.register(FeedBack)
class FeedBackAmin(DjangoObjectActions, admin.ModelAdmin):
    def export_to_xls(self, request, obj):
        query_record = FeedBack.objects.all().values()
        return_list = list(query_record)
        for i in return_list:
            i["client_id"] = Clients.objects.all().get(pk=i["client_id"]).__str__()
            i["employee_id"] = Employees.objects.all().get(pk=i["employee_id"]).__str__()

        ret_list = []
        ret_list.append(return_list[0].keys())
        for i in return_list:
            ret_list.append(i.values())
        print(return_list)
        return excel.make_response_from_array(
            ret_list,
            file_type="xlsx",
            file_name="FeedBack"
        )
    list_display = ('client', 'answer', 'is_light', 'light_answer', 'employee', 'status', 'by_employee', 'feedback_type', 'supervisor', 'feedback_id','progress_status','data_time', 'report')
    list_filter = (FeedbackFilter_is_light, FeedbackFilter_status)
    readonly_fields = ('client', 'answer', 'light_answer','feedback_type')
    search_fields = ("client__name", "employee__name", "employee__phone", "employee__job_title")
    export_to_xls.label = "Экспорт в Excel"
    changelist_actions = ('export_to_xls',)

