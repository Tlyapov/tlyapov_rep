from rest_framework_json_api import serializers
from clients.serializers import ClientsSerializer
from .models import DeferredSurvey,CustomSurvey



class CustomSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomSurvey
        fields = "__all__"

class DeferredSurveySerializer(serializers.ModelSerializer):
    client = ClientsSerializer(read_only=True)
    survey = CustomSurveySerializer(read_only=True)

    class Meta:
        model = DeferredSurvey
        fields = ("id", "client", "survey", 'status')

    def to_representation(self, instance):
        self.fields['client'] = ClientsSerializer(read_only=True)
        self.fields['survey'] = CustomSurveySerializer(read_only=True)
        return super(DeferredSurveySerializer, self).to_representation(instance)