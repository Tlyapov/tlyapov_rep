from django.contrib import admin
from .models import CustomAnswers, CustomSurvey, CustomQuestion, ClientAnswersToCustomSurvey, FakeClientAnsers, TimeRunSurvey, DeferredSurvey
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.forms.models import model_to_dict
from django_object_actions import DjangoObjectActions, action
import django_excel as excel
from clients.models import Clients


class BooleanDefaultNoFilter(SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('all', 'Все'),
            ("yes", 'Да'),
            ('no', 'Нет')
        )

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == (str(lookup) if lookup else lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == "yes":
            custom_list = []
            for i in queryset:
                if model_to_dict(i)[self.parameter_name]:
                    custom_list.append(i.id)
            return queryset.filter(id__in=custom_list)
        if self.value() == "no":
            custom_list = []
            for i in queryset:
                if not model_to_dict(i)[self.parameter_name]:
                    custom_list.append(i.id)
            return queryset.filter(id__in=custom_list)
        if self.value() == 'all':
            return queryset
        if self.value() is None:
            return queryset


class NamedFilter(BooleanDefaultNoFilter):
    title = _('Активен')
    parameter_name = 'is_active'


class SurveyStatusFilter(BooleanDefaultNoFilter):
    title = _('Пройден')
    parameter_name = 'status'


@admin.register(CustomAnswers)
class CustomAnswersAdmin(admin.ModelAdmin):
    list_display = ('value', )
    search_fields = ("value", )


@admin.register(CustomQuestion)
class CustomQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', )
    search_fields = ("question", )


@admin.register(CustomSurvey)
class CustomSurveyAdmin(admin.ModelAdmin):
    list_display = ("name", )
    search_fields = ("name", )


@admin.register(ClientAnswersToCustomSurvey)
class CustomSurveyAdmin(DjangoObjectActions, admin.ModelAdmin):
    def export_to_xls(self, request, obj):
        query_record = ClientAnswersToCustomSurvey.objects.all().values()
        return_list = list(query_record)
        for i in return_list:
            i["client_id"] = Clients.objects.all().get(pk=i["client_id"]).__str__()
            i["survey_id"] = CustomSurvey.objects.all().get(pk=i["survey_id"]).__str__()
            answers = FakeClientAnsers.objects.all().filter(all_answers=ClientAnswersToCustomSurvey.objects.get(pk=i['id']))
            for j in range(0, len(answers)):
                i[f'question #{j}'] = answers[j].question.__str__()
                i[f"answer #{j}"] = answers[j].answer.__str__()
        ret_list = []
        ret_list.append(return_list[0].keys())
        for i in return_list:
            ret_list.append(i.values())
        return excel.make_response_from_array(
            ret_list,
            file_type="xlsx",
            file_name="ClientAnswersToCustomSurvey"
        )
    list_display = ("survey", "client")
    readonly_fields = ("DisplayClientAnswers", "survey", "client")
    search_fields = ("survey__name", "client__name")
    export_to_xls.label = "Экспорт в Excel"
    changelist_actions = ('export_to_xls',)


@admin.register(TimeRunSurvey)
class TimeRunSurveyAdmin(admin.ModelAdmin):
    list_display = ("survey", "all_clients", "start_time", "end_time", "periodicity", 'is_active')
    search_fields = ("survey", )
    list_filter = (NamedFilter, )
    readonly_fields = ('last_send_date', )

@admin.register(DeferredSurvey)
class DeferredSurveyAdmin(admin.ModelAdmin):
    list_display = ("survey", "client")
    search_fields = ("survey",)
    list_filter = (SurveyStatusFilter,)