from django.shortcuts import render
from rest_framework.views import APIView
from clients.models import Clients
from rest_framework import status

from web_app.utils import get_default_servery
from .models import DeferredSurvey, CustomSurvey, ClientAnswersToCustomSurvey, FakeClientAnsers, \
    CustomQuestion, CustomAnswers
from .serializers import DeferredSurveySerializer
from rest_framework.response import Response
from django.forms.models import model_to_dict


class GetDefaultSurvey(APIView):
    def get(self, request):
        try:
            survey_id = get_default_servery()
            return Response({"id": survey_id})
        except BaseException as e:
            print(f"ERROR in CustomSurvey.views -- GetDefaultSurvey {e}")


class ClientAnswersToCustomSurveyPost(APIView):
    def post(self, request):
        data = request.data
        client = Clients.objects.get(id=int(data['client_id']))
        survey = CustomSurvey.objects.get(id=int(data['survey_id']))
        res = ClientAnswersToCustomSurvey.objects.create(client=client, survey=survey)
        return Response(model_to_dict(res))


class FakeClientAnsersPost(APIView):
    def post(self, request):
        data = request.data
        question = CustomQuestion.objects.get(id=int(data['question_id']))
        answer = CustomAnswers.objects.get(id=int(data['answer_id']))
        all_answers = ClientAnswersToCustomSurvey.objects.get(id=int(data['all_answers_id']))
        res = FakeClientAnsers.objects.create(question=question, answer=answer, all_answers=all_answers)
        return Response(model_to_dict(res))


class DeferredSurveyPost(APIView):
    def post(self, request):
        data = request.data
        client = Clients.objects.get(id=int(data['client']))
        survey = CustomSurvey.objects.get(id=int(data['survey']))
        res = DeferredSurvey.objects.create(client=client, survey=survey, status=data['status'])
        return Response(model_to_dict(res))


class DeferredSurveySet(APIView):
    def get(self, request, pk):
        deferred_survey = DeferredSurvey.objects.get(id=pk)
        serializer = DeferredSurveySerializer(deferred_survey)
        return Response(serializer.data)

    def put(self, request, pk):
        deferred_survey = DeferredSurvey.objects.get(id=pk)
        serializer = DeferredSurveySerializer(deferred_survey, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
