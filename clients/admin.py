from django.contrib import admin
from .models import Clients
from django_object_actions import DjangoObjectActions, action
import django_excel as excel


@admin.register(Clients)
class ClientsAdmin(DjangoObjectActions, admin.ModelAdmin):
    def export_to_xls(self, request, obj):
        query_record = Clients.objects.all().values()
        return_list = list(query_record)
        ret_list = []
        ret_list.append(return_list[0].keys())
        for i in return_list:
            ret_list.append(i.values())
        print(return_list)
        return excel.make_response_from_array(
            ret_list,
            file_type="xlsx",
            file_name="Clients"
        )
    list_display = ('phone', 'name', 'company_name', 'job_title')
    exclude = ('chat_id', 'client_code',)
    search_fields = ("name", "phone", "company_name", "job_title")
    export_to_xls.label = "Экспорт в Excel"
    changelist_actions = ('export_to_xls', )