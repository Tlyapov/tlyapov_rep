from django.contrib import admin
from django.urls import path,include
from CustomSurvey.views import GetDefaultSurvey, DeferredSurveyPost,DeferredSurveySet, ClientAnswersToCustomSurveyPost,FakeClientAnsersPost
from clients.views import ClientsPost, ClientsViewSet
from traffic_light.views import  ReviewsPost, FeedbackPost,  ReviewsByEmployeePost,OffersPost
from employees.views import EmployeesViewSet, EmployeesManyViewSet
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_client/', ClientsPost.as_view()),
    path('client/<int:pk>', ClientsViewSet.as_view()),
    path('add_review/', ReviewsPost.as_view()),
    path('add_offer/', OffersPost.as_view()),
    path('add_answer_to_custom_survey/', ClientAnswersToCustomSurveyPost.as_view()),
    path('add_fake_client_ansers/', FakeClientAnsersPost.as_view()),
    path('add_review_by_employee/', ReviewsByEmployeePost.as_view()),
    path('add_feedback/', FeedbackPost.as_view()),
    path('get_all_admins/', EmployeesViewSet.as_view()),
    path('employee/<int:pk>', EmployeesManyViewSet.as_view()),
    path('get_default_survey', GetDefaultSurvey.as_view()),
    path('add_deferred_survey', DeferredSurveyPost.as_view()),
    path('deferred_survey/<int:pk>', DeferredSurveySet.as_view()),
    path('crm/', include('web_app.urls'))
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
