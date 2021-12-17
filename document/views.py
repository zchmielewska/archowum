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


class AddProductView(LoginRequiredMixin, CreateView):
    model = models.Product
    fields = "__all__"
    success_url = reverse_lazy("manage")


class EditProductView(LoginRequiredMixin, UpdateView):
    model = models.Product
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")


class DeleteProductView(DeleteView):
    model = models.Product
    success_url = reverse_lazy("manage")


class AddCategoryView(LoginRequiredMixin, CreateView):
    model = models.Category
    fields = "__all__"
    success_url = reverse_lazy("manage")


class EditCategoryView(LoginRequiredMixin, UpdateView):
    model = models.Category
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")


class DeleteCategoryView(DeleteView):
    model = models.Category
    success_url = reverse_lazy("manage")


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


class EditDocumentView(LoginRequiredMixin, UpdateView):
    model = models.Document
    fields = ["product", "category", "validity_start", "file"]
    template_name_suffix = "_update_form"

    def form_valid(self, form):
        document_new = form.save(commit=False)
        document_old = models.Document.objects.get(pk=self.object.id)
        now = timezone.now()

        if not document_new.product == document_old.product:
            models.History.objects.create(
                document=document_old,
                element="produkt",
                changed_from=document_old.product,
                changed_to=document_new.product,
                changed_by=self.request.user,
                changed_at=now,
            )

        if not document_new.category == document_old.category:
            models.History.objects.create(
                document=document_old,
                element="kategoria dokumentu",
                changed_from=document_old.category,
                changed_to=document_new.category,
                changed_by=self.request.user,
                changed_at=now,
            )

        if not document_new.validity_start == document_old.validity_start:
            models.History.objects.create(
                document=document_old,
                element="ważny od",
                changed_from=document_old.validity_start,
                changed_to=document_new.validity_start,
                changed_by=self.request.user,
                changed_at=now,
            )

        if not document_new.file == document_old.file:
            models.History.objects.create(
                document=document_old,
                element="plik",
                changed_from=document_old.file,
                changed_to=document_new.file,
                changed_by=self.request.user,
                changed_at=now,
            )

        document_new.save()
        return redirect("document_detail", document_new.id)


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

