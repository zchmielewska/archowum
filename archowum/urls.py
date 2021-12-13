"""archowum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from document import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Main.as_view(), name="main"),
    path('dokument/dodaj/', views.AddDocument.as_view(), name="add_document"),
    path('produkt/dodaj/', views.AddProduct.as_view(), name="add_product"),
    path('kategoria/dodaj/', views.AddCategory.as_view(), name="add_category"),
    path('produkt/edytuj/<pk>', views.EditProduct.as_view(), name="edit_product"),
    path('kategoria/edytuj/<pk>', views.EditCategory.as_view(), name="edit_category"),
    path('produkt/usun/<pk>', views.DeleteProduct.as_view(), name="delete_product"),
    path('kategoria/usun/<pk>', views.DeleteCategory.as_view(), name="delete_category"),
    path('zarzadzaj/', views.Manage.as_view(), name="manage"),
    path('zarejestruj/', views.Register.as_view(), name="register"),
    path('zaloguj/', views.Login.as_view(), name="login"),
    path('wyloguj/', views.Logout.as_view(), name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
