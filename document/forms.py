from django import forms

from document import models


class DateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'


class AddDocumentFormOld(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = ("file", "product", "category", "validity_start")
        labels = {
            "product": "Produkt",
            "category": "Kategoria dokumentu",
            "file": "Plik",
            "validity_start": "Ważny od",
        }
        widgets = {
            'validity_start': DateInput()
        }


class AddDocumentForm(forms.Form):
    file = forms.FileField(label="Plik")
    product = forms.ModelChoiceField(queryset=models.Product.objects.all(), label="Produkt")
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), label="Kategoria dokumentu")
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
