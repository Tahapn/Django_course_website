from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .permissions import IsTeacher
from . import serializers
from . import models


class CoursesViewSet(ReadOnlyModelViewSet):
    serializer_class = serializers.CourseSerializer
    queryset = models.Course.objects.all()


class TeacherProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user.id
        teacher = get_object_or_404(models.Teacher, user=user)
        serializer = serializers.TeacherSerializer(teacher)
        return Response(serializer.data)

    def post(self, request):
        try:
            serializer = serializers.TeacherSerializer(
                data=request.data, context=self.get_serializer_context(request))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        except IntegrityError:
            return Response('Teacher profile already exists. no need to send post request', status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        teacher = get_object_or_404(models.Teacher, user=self.request.user.id)
        serializer = serializers.TeacherSerializer(
            teacher, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    def get_serializer_context(self, request):
        return {'user': self.request.user.id}


class TeacherCoursesViewSet(ModelViewSet):

    def get_queryset(self):
        teacher = models.Teacher.objects.get(user=self.request.user.id)
        return models.Course.objects.filter(teacher=teacher)

    def get_serializer_context(self):
        teacher = models.Teacher.objects.get(user=self.request.user.id)
        return {'teacher': teacher}

    serializer_class = serializers.CourseSerializer

    permission_classes = [IsTeacher]
