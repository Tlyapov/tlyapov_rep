from django.shortcuts import render
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .serializers import ClientsSerializer
from .models import Clients
from rest_framework import status
now = datetime.now()


class ClientsPost(APIView):
    def post(self, request):
        data = request.data
        serializer = ClientsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ClientsViewSet(APIView):
    def get(self, request, pk):
        client = Clients.objects.get(id=pk)
        serializer = ClientsSerializer(client)
        return Response(serializer.data)

    def put(self, request, pk):
        client = Clients.objects.get(id=pk)
        serializer = ClientsSerializer(client, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

