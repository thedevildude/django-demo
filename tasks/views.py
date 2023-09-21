from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from tasks.models import Task


class UserLoginView(LoginView):
    template_name = "user_login.html"
    success_url = "/tasks"


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "user_create.html"
    success_url = "/user/login"


def session_storage_view(request):
    total_views = request.session.get("total_views", 0)
    request.session["total_views"] = total_views + 1
    return HttpResponse(f"Total views: {total_views} and the user is {request.user}")


class AuthorisedTaxManager(LoginRequiredMixin):
    def get_queryset(self):
        return Task.objects.filter(deleted=False, user=self.request.user)


class GenericTaskDeleteView(AuthorisedTaxManager, DeleteView):
    model = Task
    template_name = "task_delete.html"
    success_url = "/tasks"


class TaskCreateForm(LoginRequiredMixin, ModelForm):
    def clean_title(self):
        title = self.cleaned_data["title"]
        if len(title) < 10:
            raise ValidationError("Title must be at least 10 characters long")
        return title.upper()

    class Meta:
        model = Task
        fields = ["title", "description", "completed"]


class GenericTaskUpdateView(AuthorisedTaxManager, UpdateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "task_update.html"
    success_url = "/tasks"


class GenericTaskCreateView(AuthorisedTaxManager, CreateView):
    form_class = TaskCreateForm
    template_name = "task_create.html"
    success_url = "/tasks"

    def form_valid(self, form):
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class GenericTaskView(AuthorisedTaxManager, ListView):
    queryset = Task.objects.filter(deleted=False, completed=False)
    template_name = "tasks.html"
    context_object_name = "tasks"
    paginate_by = 5

    def get_queryset(self):
        search_term = self.request.GET.get("search")
        tasks = Task.objects.filter(
            deleted=False, completed=False, user=self.request.user
        )
        if search_term:
            tasks = tasks.filter(title__icontains=search_term)
        return tasks


class CreateTaskView(View):
    def get(self, request):
        return render(request, "task_create.html")

    def post(self, request):
        task_value = request.POST.get("task")
        task_obj = Task(title=task_value)
        task_obj.save()
        return HttpResponseRedirect("/tasks")


class TaskView(View):
    def get(self, request):
        search_term = request.GET.get("search")
        tasks = Task.objects.filter(deleted=False, completed=False)
        if search_term:
            tasks = tasks.filter(title__icontains=search_term)
        return render(request, "tasks.html", {"tasks": tasks})

    def post(self, request):
        pass


def test_static_view(request):
    return render(request, "test_static.html")


def task_view(request):
    search_term = request.GET.get("search")
    tasks = Task.objects.filter(deleted=False, completed=False)
    if search_term:
        tasks = tasks.filter(title__icontains=search_term)
    return render(request, "tasks.html", {"tasks": tasks})


def add_task_view(request):
    task_value = request.GET.get("task")
    task_obj = Task(title=task_value)
    task_obj.save()
    return HttpResponseRedirect("/tasks")


def delete_task_view(request, index):
    Task.objects.filter(id=index).update(deleted=True)
    return HttpResponseRedirect("/tasks")


def complete_task_view(request, task_id):
    task = Task.objects.filter(id=task_id)
    task.update(completed=True)
    return HttpResponseRedirect("/tasks")


def completed_task_view(request):
    tasks = Task.objects.filter(deleted=False, completed=True)
    return render(request, "completed_tasks.html", {"tasks": tasks})
