from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView, CreateView, UpdateView, DeleteView

from document import models
from document import forms


class Main(View):
    def get(self, request):
        documents = models.Document.objects.all().order_by("-id")[:10]
        return render(request, "main.html", {"documents": documents})


class Manage(View):
    def get(self, request):
        categories = models.Category.objects.all().order_by("id")
        products = models.Product.objects.all().order_by("id")
        return render(request, "manage.html", {"categories": categories, "products": products})


class AddDocument(View):
    def get(self, request):
        form = forms.AddDocumentForm
        return render(request, "document_form.html", {"form": form})

    def post(self, request):
        form = forms.AddDocumentForm(request.POST, request.FILES)
        print("form:", form)
        if form.is_valid():
            product = form.cleaned_data.get("product")
            category = form.cleaned_data.get("category")
            validity_start = form.cleaned_data.get("validity_start")
            file = form.cleaned_data.get("file")
            fss = FileSystemStorage()
            fss.save(file.name, file)
            models.Document.objects.create(
                product=product,
                category=category,
                validity_start=validity_start,
                file=file,
            )
            return redirect("main")


class AddProduct(CreateView):
    model = models.Product
    fields = "__all__"
    success_url = reverse_lazy("manage")


class AddCategory(CreateView):
    model = models.Category
    fields = "__all__"
    success_url = reverse_lazy("manage")


class EditProduct(UpdateView):
    model = models.Product
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")


class EditCategory(UpdateView):
    model = models.Category
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")


class DeleteProduct(DeleteView):
    model = models.Product
    success_url = reverse_lazy("manage")


class DeleteCategory(DeleteView):
    model = models.Category
    success_url = reverse_lazy("manage")


class Register(View):
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


class Login(View):
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


class Logout(View):
    """Form to log out."""
    def get(self, request):
        logout(request)
        return redirect("main")

