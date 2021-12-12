from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView

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
        form = forms.AddDocumentForm()
        return render(request, "add-document.html", {"form": form})

    def post(self, request):
        file = request.FILES["file"]
        fss = FileSystemStorage()
        fss.save(file.name, file)
        return redirect("main")


class AddProduct(FormView):
    template_name = "add-product.html"
    form_class = forms.AddProductForm

    def form_valid(self, form):
        model = form.cleaned_data.get("model")
        name = form.cleaned_data.get("name")
        description = form.cleaned_data.get("description")

        models.Product.objects.create(
            model=model,
            name=name,
            description=description
        )
        return redirect("manage")


class AddCategory(FormView):
    template_name = "add-category.html"
    form_class = forms.AddCategoryForm

    def form_valid(self, form):
        name = form.cleaned_data.get("name")

        models.Category.objects.create(
            name=name,
        )
        return redirect("manage")

