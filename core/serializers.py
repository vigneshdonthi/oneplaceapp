from rest_framework import serializers
from .models import Task, Habit, Note
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'user', 'title', 'due_time', 'priority', 'is_completed', 'created_at','date']
        read_only_fields = ['id', 'user', 'created_at']

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            'id',
            'user',
            'name',
            'icon',
            'days',
            'is_done_today',
            'last_checkin',
            'streak',
            'longest_streak',
            'weekly_progress',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'streak',
            'longest_streak',
            'weekly_progress',
            'last_checkin',
            'is_done_today'
        ]


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email']



class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already in use.")]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This username is already taken.")]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
