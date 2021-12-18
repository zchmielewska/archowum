from django import forms

from document import models


class DateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'


class DocumentForm(forms.Form):
    product = forms.ModelChoiceField(queryset=models.Product.objects.all(), label="Produkt")
    category = forms.ModelChoiceField(queryset=models.Category.objects.all(), label="Kategoria dokumentu")
    validity_start = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Ważny od")
    file = forms.FileField(label="Plik")


class DocumentForm2(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = ('product', 'category', 'validity_start', 'file')
        widgets = {
            'validity_start': forms.DateInput(attrs={'type': 'date'}),
        }


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=36, label="Nazwa użytkownika")
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Powtórz hasło", widget=forms.PasswordInput)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=36, label="Nazwa użytkownika")
    password = forms.CharField(label="Hasło", widget=forms.PasswordInput)
