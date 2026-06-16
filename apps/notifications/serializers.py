from rest_framework import serializers
from .models import EmailQueue, GeneratedDocument, ScheduledTaskLog


class EmailQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailQueue
        fields = '__all__'


class GeneratedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedDocument
        fields = '__all__'


class ScheduledTaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledTaskLog
        fields = '__all__'