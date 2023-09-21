from tasks.models import Task
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from rest_framework.viewsets import ModelViewSet

from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    CharFilter,
    ChoiceFilter,
)

from tasks.models import STATUS_CHOICES


class TaskFilter(FilterSet):
    title = CharFilter(lookup_expr="icontains")
    status = ChoiceFilter(choices=STATUS_CHOICES)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]


class TaskSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ["title", "description", "completed", "user"]


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(deleted=False, user=self.request.user)


class TaskListApi(APIView):
    def get(self, request):
        tasks = Task.objects.filter(deleted=False)
        data = TaskSerializer(tasks, many=True).data
        return Response({"tasks": data})
