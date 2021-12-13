from django import forms

from document import models


class DateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'


class AddDocumentForm(forms.Form):
    product = forms.ModelChoiceField(queryset=models.Product.objects.all(), label="Produkt")
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), label="Kategoria dokumentu")
    file = forms.FileField(label="Plik")
    validity_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Ważny od")


class AddProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = "__all__"
        labels = {
            "model": "Model przepływów pieniężnych  ",
            "name": "Nazwa produktu",
            "description": "Opis produktu",
        }


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = "__all__"
        labels = {"name": "Nazwa kategorii produktów"}


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=36, label="Nazwa użytkownika")
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Powtórz hasło", widget=forms.PasswordInput)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=36, label="Nazwa użytkownika")
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)
