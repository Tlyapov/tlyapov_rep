from rest_framework_json_api import serializers
from .models import Clients


class ClientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clients
        fields = ("id", "phone", "name", "company_name", "job_title", "tg_id", "chat_id", "employee")
