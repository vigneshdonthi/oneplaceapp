from django.contrib import admin
from django.contrib.admin import RelatedOnlyFieldListFilter
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth.models import User

# Register your models here.
from .models import Task, Habit, Note  # import your models

class UserDropdownForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=True, label='Select User')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'is_completed', 'date', 'due_time', 'created_at')
    list_filter = (
        ('user', RelatedOnlyFieldListFilter),
        'priority',
        'is_completed',
        'date',
    )
    search_fields = ('title', 'user__username')

    change_list_template = "admin/task_change_list.html"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('filter_by_user/', self.admin_site.admin_view(self.filter_by_user), name='core_task_filter_by_user')
        ]
        return custom_urls + urls

    def filter_by_user(self, request):
        if request.method == 'POST':
            form = UserDropdownForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                url = reverse('admin:core_task_changelist') + f'?user__id__exact={user.id}'
                return HttpResponseRedirect(url)
        else:
            form = UserDropdownForm()
        context = dict(
            self.admin_site.each_context(request),
            form=form,
        )
        from django.shortcuts import render
        return render(request, "admin/filter_by_user.html", context)

class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'icon', 'is_done_today', 'last_checkin', 'streak', 'longest_streak', 'created_at')
    list_filter = (
        ('user', RelatedOnlyFieldListFilter),
        'is_done_today',
    )
    search_fields = ('name', 'user__username')

    change_list_template = "admin/habit_change_list.html"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('filter_by_user/', self.admin_site.admin_view(self.filter_by_user), name='core_habit_filter_by_user')
        ]
        return custom_urls + urls

    def filter_by_user(self, request):
        if request.method == 'POST':
            form = UserDropdownForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                url = reverse('admin:core_habit_changelist') + f'?user__id__exact={user.id}'
                return HttpResponseRedirect(url)
        else:
            form = UserDropdownForm()
        context = dict(
            self.admin_site.each_context(request),
            form=form,
        )
        from django.shortcuts import render
        return render(request, "admin/filter_by_user.html", context)

class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'created_at')
    list_filter = (
        ('user', RelatedOnlyFieldListFilter),
    )
    search_fields = ('content', 'user__username')

    change_list_template = "admin/note_change_list.html"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('filter_by_user/', self.admin_site.admin_view(self.filter_by_user), name='core_note_filter_by_user')
        ]
        return custom_urls + urls

    def filter_by_user(self, request):
        if request.method == 'POST':
            form = UserDropdownForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                url = reverse('admin:core_note_changelist') + f'?user__id__exact={user.id}'
                return HttpResponseRedirect(url)
        else:
            form = UserDropdownForm()
        context = dict(
            self.admin_site.each_context(request),
            form=form,
        )
        from django.shortcuts import render
        return render(request, "admin/filter_by_user.html", context)

admin.site.register(Task, TaskAdmin)
admin.site.register(Habit, HabitAdmin)
admin.site.register(Note, NoteAdmin)
