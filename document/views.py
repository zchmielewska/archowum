import mimetypes
import os
import datetime

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, CreateView, UpdateView, DeleteView, DetailView

from archowum import settings
from document import models
from document import forms
from document.utils import utils


class MainView(LoginRequiredMixin, View):
    def get(self, request):
        phrase = request.GET.get("phrase")

        if not phrase:
            documents = models.Document.objects.order_by("-id")[:10]
        else:
            documents = utils.search(phrase)

        ctx = {
            "documents": documents,
            "phrase": phrase,
            "no_documents": documents.count(),
        }
        return render(request, "main.html", ctx)


class ManageView(LoginRequiredMixin, View):
    def get(self, request):
        categories = models.Category.objects.all().order_by("id")
        products = models.Product.objects.all().order_by("id")
        return render(request, "manage.html", {"categories": categories, "products": products})


class AddProductView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Product
    fields = "__all__"
    success_url = reverse_lazy("manage")
    success_message = "Dodano nowy produkt!"


class EditProductView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Product
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")
    success_message = "Zaktualizowano produkt!"


class DeleteProductView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = models.Product
    success_url = reverse_lazy("manage")
    success_message = "Usunięto produkt!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteProductView, self).delete(request, *args, **kwargs)


class AddCategoryView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = models.Category
    fields = "__all__"
    success_url = reverse_lazy("manage")
    success_message = "Dodano nową kategorię!"


class EditCategoryView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = models.Category
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")
    success_message = "Zaktualizowano kategorię!"


class DeleteCategoryView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = models.Category
    success_url = reverse_lazy("manage")
    success_message = "Usunięto kategorię!"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteCategoryView, self).delete(request, *args, **kwargs)


class AddDocumentView(LoginRequiredMixin, View):
    def get(self, request):
        form = forms.DocumentForm
        return render(request, "document_form.html", {"form": form})

    def post(self, request):
        form = forms.DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.cleaned_data.get("product")
            category = form.cleaned_data.get("category")
            validity_start = form.cleaned_data.get("validity_start")
            file = form.cleaned_data.get("file")
            try:
                models.Document.objects.create(
                    product=product,
                    category=category,
                    validity_start=validity_start,
                    file=file,
                    created_by=request.user,
                )
                messages.success(request, 'Dodano nowy dokument!')
                return redirect("main")
            except IntegrityError:
                messages.error(request, 'Dokument dla podanego produktu, kategorii i daty już istnieje.')
                return render(request, "document_form.html", {"form": form})

        return render(request, "document_form.html", {"form": form})


class EditDocumentView(LoginRequiredMixin, View):
    def get(self, request, pk):
        document = models.Document.objects.get(pk=pk)
        form = forms.DocumentForm(initial={
            "product": document.product,
            "category": document.category,
            "validity_start": document.validity_start.strftime("%Y-%m-%d"),
            "file": document.file,
        })
        return render(request, "document_update_form.html", {"form": form})


class DeleteDocumentView(LoginRequiredMixin, DeleteView):
    model = models.Document
    success_url = reverse_lazy("main")


class DocumentDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        document = get_object_or_404(models.Document, pk=pk)
        history_set = document.history_set.all()
        ctx = {
            "document": document,
            "history_set": history_set,
        }
        return render(request, "document_detail.html", ctx)


class DownloadDocumentView(LoginRequiredMixin, View):
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

