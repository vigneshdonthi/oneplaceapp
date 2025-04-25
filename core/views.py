from django.shortcuts import render
from django.db.models import Case, When, IntegerField
from datetime import date
# Create your views here.
# core/views.py
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny,IsAuthenticated

from .models import Task, Habit, Note
from .serializers import (
    TaskSerializer,
    HabitSerializer,
    NoteSerializer,
    RegisterSerializer,
    UserProfileSerializer
)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        priority_order = Case(
            When(priority='high', then=1),
            When(priority='medium', then=2),
            When(priority='low', then=3),
            output_field=IntegerField(),
        )
        queryset = Task.objects.filter(user=self.request.user)
        date_param = self.request.query_params.get('date', None)
        if date_param:
            queryset = queryset.filter(date=date_param)
        return queryset.annotate(
            priority_order=priority_order
        ).order_by('priority_order')
        
        #return Task.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        habits = Habit.objects.filter(user=self.request.user).order_by('-created_at')

        # Optional filter by day (e.g., ?day=Mon)
        day_param = self.request.query_params.get('day', None)
        if day_param:
            habits = habits.filter(days__contains=[day_param])

        return habits

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()

        # Reset is_done_today if a new day
        if instance.last_checkin != date.today():
            instance.is_done_today = False
            instance.save()

    @action(detail=True, methods=["post", "put"], url_path="mark-done")
    def mark_done(self, request, pk=None):
        """
        POST /habits/<id>/mark-done/
        Marks today's habit as done, updates streaks and progress
        """
        habit = self.get_object()

        today = date.today()
        weekday = today.weekday()  # 0=Mon, 6=Sun

        # Weekly progress (ensure 7-length array)
        if len(habit.weekly_progress) != 7:
            habit.weekly_progress = [False] * 7

        if not habit.is_done_today:
            habit.is_done_today = True
            habit.last_checkin = today
            habit.streak += 1
            habit.longest_streak = max(habit.streak, habit.longest_streak)
            habit.weekly_progress[weekday] = True
            habit.save()
            return Response({"message": "Habit marked as done ✅", "streak": habit.streak})
        else:
            return Response({"message": "Habit already marked done today."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reset-done")
    def reset_done(self, request, pk=None):
        """
        POST /habits/<id>/reset-done/
        Resets today's completion (undo)
        """
        habit = self.get_object()
        today = date.today()
        weekday = today.weekday()

        if habit.is_done_today:
            habit.is_done_today = False
            habit.streak = max(habit.streak - 1, 0)
            habit.weekly_progress[weekday] = False
            habit.save()
            return Response({"message": "Today's habit undone."})
        else:
            return Response({"message": "Habit was not marked done today."})

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CustomLoginView(ObtainAuthToken):
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
        })
class RegisterView(APIView):
    # Set the permission classes at the class level, not inside the post method
    permission_classes = [AllowAny]  # This allows unauthenticated users to access this view

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
            }, status=status.HTTP_201_CREATED)

        print("Serializer errors:", serializer.errors)  # 👈 This MUST be here
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import logout


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

