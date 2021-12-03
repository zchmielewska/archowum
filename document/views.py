from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from document import models


class Main(View):
    def get(self, request):
        documents = models.Document.objects.all().order_by("-id")[:10]
        return render(request, "main.html", {"documents": documents})


class AddDocument(View):
    def get(self, request):
        return render(request, "add-document.html")

    def post(self, request):
        file = request.FILES["file"]
        fss = FileSystemStorage()
        fss.save(file.name, file)
        return redirect("main")


class Manage(View):
    def get(self, request):
        categories = models.Category.objects.all().order_by("id")
        products = models.Product.objects.all().order_by("id")
        return render(request, "manage.html", {"categories": categories, "products": products})

