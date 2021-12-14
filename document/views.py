import mimetypes
import os

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, CreateView, UpdateView, DeleteView, DetailView

from archowum import settings
from document import models
from document import forms


class MainView(LoginRequiredMixin, View):
    def get(self, request):
        documents = models.Document.objects.all().order_by("-id")[:10]
        return render(request, "main.html", {"documents": documents})


class ManageView(LoginRequiredMixin, View):
    def get(self, request):
        categories = models.Category.objects.all().order_by("id")
        products = models.Product.objects.all().order_by("id")
        return render(request, "manage.html", {"categories": categories, "products": products})


class AddDocumentView(LoginRequiredMixin, View):
    def get(self, request):
        form = forms.AddDocumentForm
        return render(request, "document_form.html", {"form": form})

    def post(self, request):
        form = forms.AddDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.cleaned_data.get("product")
            category = form.cleaned_data.get("category")
            validity_start = form.cleaned_data.get("validity_start")
            file = form.cleaned_data.get("file")
            models.Document.objects.create(
                product=product,
                category=category,
                validity_start=validity_start,
                file=file,
                created_by=request.user,
            )
            return redirect("main")
        return render(request, "document_form.html", {"form": form})


class AddProductView(LoginRequiredMixin, CreateView):
    model = models.Product
    fields = "__all__"
    success_url = reverse_lazy("manage")


class AddCategoryView(LoginRequiredMixin, CreateView):
    model = models.Category
    fields = "__all__"
    success_url = reverse_lazy("manage")


class EditProductView(LoginRequiredMixin, UpdateView):
    model = models.Product
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")


class EditCategoryView(LoginRequiredMixin, UpdateView):
    model = models.Category
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")


class DeleteProductView(DeleteView):
    model = models.Product
    success_url = reverse_lazy("manage")


class DeleteCategoryView(DeleteView):
    model = models.Category
    success_url = reverse_lazy("manage")


class RegisterView(View):
    """Form to create a new account."""
    def get(self, request):
        form = forms.RegisterForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            username_is_taken = username in User.objects.values_list("username", flat=True)
            if username_is_taken:
                form.add_error("username", "Ta nazwa użytkownika jest już zajęta.")
                return render(request, "register.html", {"form": form})

            user = User.objects.create_user(username=username, email=None, password=password)
            login(request, user)
            return redirect("main")
        else:
            return render(request, "register.html", {"form": form})


class LoginView(View):
    """Form to log in."""
    def get(self, request):
        form = forms.LoginForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                url_next = request.GET.get("next", "/")
                return redirect(url_next)
            else:
                form.add_error("username", "Nieprawidłowa nazwa użytkownika lub hasło.")
        return render(request, "login.html", {"form": form})


class LogoutView(View):
    """Form to log out."""
    def get(self, request):
        logout(request)
        return redirect("main")


class DocumentDetailView(DetailView):
    model = models.Document


class DownloadDocumentView(View):
    def get(self, request, pk):
        document = get_object_or_404(models.Document, id=pk)
        filepath = os.path.join(settings.MEDIA_ROOT, document.file.name)
        if os.path.exists(filepath):
            with open(filepath, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(filepath)
                response = HttpResponse(fh.read(), content_type=mime_type)
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(filepath)
                return response
        raise Http404


class DeleteDocumentView(DeleteView):
    model = models.Document
    success_url = reverse_lazy("main")
