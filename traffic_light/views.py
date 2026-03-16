import requests
from django.shortcuts import render
import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from clients.models import Clients
from employees.models import Employees
from light_admin.settings import BASE_DIR
from .models import Reviews, FeedBack, ReviewsByEmployee, Offers, Audio
from django.forms.models import model_to_dict
from django.core.files.base import ContentFile

now = datetime.datetime.now()






class ReviewsPost(APIView):
    def post(self, request):
        data = request.data
        client = Clients.objects.get(id=int(data['client']))
        res = Reviews.objects.create(client=client, answer=data['answer'])
        return Response(model_to_dict(res))


class ReviewsByEmployeePost(APIView):
    def post(self, request):
        data = request.data
        client = Clients.objects.get(id=int(data['client']))
        employee = Employees.objects.get(id=int(data['employee']))
        res = ReviewsByEmployee.objects.create(client=client, employee=employee, answer=data['answer'])
        return Response(model_to_dict(res))


class OffersPost(APIView):
    def post(self, request):
        data = request.data
        client = Clients.objects.get(id=int(data['client']))
        res = Offers.objects.create(client=client, answer=data['answer'])
        return Response(model_to_dict(res))


class FeedbackPost(APIView):
    def post(self, request):
        data = request.data
        client = Clients.objects.get(id=int(data['client']))
        if str(data['audio_answer']) != '':
            audio = f"{data['feedback_type']}{data['feedback_id']}"+'.ogg'
            doc = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(data['audio_answer'][0], data['audio_answer'][1]))

            audio_obj = Audio.objects.create()
            audio_obj.audio_answer.save(audio, ContentFile(doc.content))
            audio_obj.save()


            res = FeedBack.objects.create(client=client, answer=data['answer'], is_light=data['is_light'],
                                          light_answer=data['light_answer'], by_employee=data['by_employee'],
                                          feedback_type=data['feedback_type'], supervisor=data['supervisor'],
                                          feedback_id=data['feedback_id'], data_time=data['data_time'],
                                          audio_answer=audio_obj,get_req=str('https://api.telegram.org/file/bot{0}/{1}'.format(data['audio_answer'][0], data['audio_answer'][1])))

        else:
            if data['is_light'] == True:
                fb_date = data['data_time'].split()[0]
                date = datetime.datetime.strptime(
                    f"{int(str(fb_date).split('-')[2])}.{str(fb_date).split('-')[1]}.{str(fb_date).split('-')[0]}",
                    '%d.%m.%Y')
                date = date + datetime.timedelta(days=1)
            else:
                fb_date = data['data_time'].split()[0]
                date = datetime.datetime.strptime(
                    f"{int(str(fb_date).split('-')[2])}.{str(fb_date).split('-')[1]}.{str(fb_date).split('-')[0]}",
                    '%d.%m.%Y')
                date = date + datetime.timedelta(days=5)
            res = FeedBack.objects.create(client=client, answer=data['answer'], is_light=data['is_light'],
                                          light_answer=data['light_answer'], by_employee=data['by_employee'],
                                          feedback_type=data['feedback_type'], supervisor=data['supervisor'],end_data_time=date,
                                          feedback_id=data['feedback_id'], data_time=data['data_time'], get_req='')
        res.save()
        return Response(model_to_dict(res))