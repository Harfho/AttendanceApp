from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from ..decorators import teacher_required
from ..forms import TeacherSignUpForm
from ..models import User, Level, Class, Attendance

# QUIZ = CLASS, ANSWER = ATTENDANCE


class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('teachers:welcome_teacher')


class TeacherWelcomeView(ListView):
    template_name = 'classroom/teachers/welcome_teacher.html'

    def get_queryset(self):
        """Return Schools """
        return self.request.user.username


@method_decorator([login_required, teacher_required], name='dispatch')
class ClassListView(ListView):
    model = Class
    ordering = ('name', )
    context_object_name = 'classes'
    template_name = 'classroom/teachers/class_list.html'

    def get_queryset(self):
        queryset = self.request.user.classes \
            .selected_related('level') \
            .annotate(attendee_count=Count('classes', distinct=True)) \
            .annotate(attendee_count=Count('attended_class', distinct=True))

        return queryset
