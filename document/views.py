import boto3
import mimetypes
import os

from botocore.exceptions import ClientError
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView

from archowum import settings
from document import models
from document import forms
from document.utils import utils
from archowum.settings import DEPLOYMENT_TYPE


class MainView(LoginRequiredMixin, View):
    """
    Home page of the application.

    Shows ten newest documents in reverse-chronological order.
    Allows searching documents using a phrase.
    """
    def get(self, request):
        phrase = request.GET.get("phrase")
        if phrase:
            documents = utils.search(phrase)
        else:
            documents = models.Document.objects.order_by("-id")[:10]

        ctx = {
            "documents": documents,
            "phrase": phrase,
            "no_documents": documents.count(),
        }
        return render(request, "main.html", ctx)


class ManageView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Manage products and categories. Add, edit or delete objects."""
    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()

    def get(self, request):
        categories = models.Category.objects.all().order_by("id")
        products = models.Product.objects.all().order_by("id")
        return render(request, "manage.html", {"categories": categories, "products": products})


class AddProductView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """Form to add a new product."""
    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()

    model = models.Product
    fields = "__all__"
    success_url = reverse_lazy("manage")
    success_message = "Dodano nowy produkt!"


class EditProductView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """Form to edit an existing product."""
    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()

    model = models.Product
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")
    success_message = "Zaktualizowano produkt!"


class DeleteProductView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete a product."""
    model = models.Product
    success_url = reverse_lazy("manage")
    success_message = "Usunięto produkt!"

    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteProductView, self).delete(request, *args, **kwargs)


class AddCategoryView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    """Form to add a new category."""
    model = models.Category
    fields = "__all__"
    success_url = reverse_lazy("manage")
    success_message = "Dodano nową kategorię!"

    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()


class EditCategoryView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """Form to edit an existing category."""
    model = models.Category
    fields = "__all__"
    template_name_suffix = "_update_form"
    success_url = reverse_lazy("manage")
    success_message = "Zaktualizowano kategorię!"

    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()


class DeleteCategoryView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    """Delete a category."""
    model = models.Category
    success_url = reverse_lazy("manage")
    success_message = "Usunięto kategorię!"

    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(DeleteCategoryView, self).delete(request, *args, **kwargs)


class AddDocumentView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Add a new document.

    The behaviour differs between LOCAL and AWS deployment types.

    If the deployment type is LOCAL, django handles duplicates filenames
    and when a file with already existent filename get added, django adds a random string to the filename.

    If the deployment type is AWS, there is no support for the duplicated filenames.
    User gets an error and is asked to change the filename.
    """
    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()

    def get(self, request):
        form = forms.DocumentForm
        return render(request, "document_form.html", {"form": form})

    def post(self, request):
        form = forms.DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.cleaned_data.get("product")
            category = form.cleaned_data.get("category")
            validity_start = form.cleaned_data.get("validity_start")
            form_file = form.cleaned_data.get("file")

            # In AWS, user changes duplicated filename manually
            if DEPLOYMENT_TYPE == "AWS":
                filename = str(form_file)
                if utils.exists_in_s3(filename):
                    d = models.Document.objects.filter(file=filename).first()
                    error_msg = "Plik o tej nazwie już istnieje. Proszę zmień nazwę pliku. "
                    error_msg = error_msg + f"(Powiązany dokument #{d.id})" if d else error_msg
                    form.add_error("file", error_msg)
                    return render(request, "document_form.html", {"form": form})

            document = models.Document.objects.create(
                product=product,
                category=category,
                validity_start=validity_start,
                file=form_file,
                created_by=request.user,
            )
            if document.file != form_file:
                text = f"Plik o nazwie {form_file} już istnieje. Przesłany plik zapisano jako {document.file}."
                messages.info(request, text)

            messages.success(request, "Dodano nowy dokument!")
            return redirect("main")

        return render(request, "document_form.html", {"form": form})


class EditDocumentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Edit an existing document and save history of the changes made to the document.

    The behaviour differs between LOCAL and AWS deployment types in respect to the duplicated filenames.
    """
    model = models.Document
    template_name_suffix = "_update_form"
    form_class = forms.DocumentForm

    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()

    def get_initial(self):
        initial = super(EditDocumentView, self).get_initial()
        initial["validity_start"] = self.object.validity_start.strftime("%Y-%m-%d")
        return initial

    def form_valid(self, form):
        # Form contains the filename delivered by the user
        form_file = form.cleaned_data.get("file")

        # Filename after saving might differ from the one uploaded
        document_new = form.save(commit=False)
        document_old = models.Document.objects.get(id=self.object.id)

        # In AWS, user changes duplicated filename manually
        if DEPLOYMENT_TYPE == "AWS":
            filename = str(form_file)
            if utils.exists_in_s3(filename) and filename != document_old:
                d = models.Document.objects.filter(file=filename).first()
                error_msg = "Plik o tej nazwie już istnieje. Proszę zmień nazwę pliku. "
                error_msg = error_msg + f"(Powiązany dokument #{d.id})" if d else error_msg
                form.add_error("file", error_msg)
                return render(self.request, "document_update_form.html", {"form": form})

        # Filename is converted to None after deletion
        data_old = document_old.__dict__.copy()
        if self.request.FILES.get("file"):
            document_old.file.delete()

        # History of changes gets saved
        document_new.save()
        data_new = document_new.__dict__.copy()
        utils.save_history(data_old, data_new, user=self.request.user)

        messages.success(self.request, "Zaktualizowano dokument!")

        # Other documents might use the file with the same name
        if document_new.file != form_file:
            text = f"Plik o nazwie {form_file} już istnieje. Przesłany plik zapisano jako {document_new.file}."
            messages.info(self.request, text)

        return redirect("document_detail", document_new.id)


class DeleteDocumentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a document."""
    model = models.Document
    success_url = reverse_lazy("main")
    success_message = "Usunięto dokument!"

    def test_func(self):
        return self.request.user.groups.filter(name="manager").exists()


class DocumentDetailView(LoginRequiredMixin, View):
    """Show document's details."""
    def get(self, request, pk):
        document = get_object_or_404(models.Document, pk=pk)
        history_set = document.history_set.all().order_by("-changed_at")
        ctx = {
            "document": document,
            "history_set": history_set,
        }
        return render(request, "document_detail.html", ctx)


class DownloadDocumentView(LoginRequiredMixin, View):
    """Download a document's file."""
    def get(self, request, pk):
        document = get_object_or_404(models.Document, id=pk)

        if DEPLOYMENT_TYPE == "LOCAL":
            filepath = os.path.join(settings.MEDIA_ROOT, document.file.name)

            if os.path.exists(filepath):
                with open(filepath, "rb") as fh:
                    mime_type, _ = mimetypes.guess_type(filepath)
                    response = HttpResponse(fh.read(), content_type=mime_type)
                    response["Content-Disposition"] = "inline; filename=" + os.path.basename(filepath)
                    return response
            else:
                raise Http404
        elif DEPLOYMENT_TYPE == "AWS":
            s3 = boto3.client("s3")
            try:
                url = s3.generate_presigned_url("get_object", Params={"Bucket": "archowum", "Key": document.file.name})
                return redirect(url)
            except ClientError:
                raise Http404
        else:
            raise ValueError("Incorrent value for DEPLOYMENT_TYPE.")


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
            password2 = form.cleaned_data["password2"]

            username_is_taken = username in User.objects.values_list("username", flat=True)
            if username_is_taken:
                form.add_error("username", "Ta nazwa użytkownika jest już zajęta.")
                return render(request, "register.html", {"form": form})

            passwords_are_different = password != password2
            if passwords_are_different:
                form.add_error("username", "Podane hasła różnią się.")
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
