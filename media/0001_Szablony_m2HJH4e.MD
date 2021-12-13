# Szablony

## Lokalizacja plików

Pliki szablonów umieszczamy w katalogu `templates` aplikacji

```
exercises/
├── admin.py
├── apps.py
├── forms.py
├── __init__.py
├── migrations
│   ├── 0001_initial.py
├── models.py
├── templates <----------------------
│   ├── add_student.html
│   ├── base.html
├── tests.py
└── views.py

```

## Renderowanie szablonu

Przy użyciu TemplateResponse

```py
ctx = {"Klucz": "Wartość"}
TemplateResponse(request, "nazwaszablonu.html", ctx)
```

gdzie, ctx to słownik (kontekst jaki przekazujemy do szablonu)

Przy użyciu render

```py
ctx = {"Age": 16}
render(request, "nazwaszablonu.html", ctx)
```

## Konstrukcje w szablonie

- Wyświetlenie zawartości kontekstu (Wąs Wąs)

```twig
    {{ nazwa_przekazanego_elementu }}
```

---

- Pętla (Wąs z procentami)
```twig
{% for element in zbior %}
    {{ element }}
{% endfor %}
```

- Pętla po pustym zbiorze

```twig
{% for element in zbior %}
    {{ element }}
{% empty %}
    treść wyświetlana jeśli zbiór jest pusty
{% endfor %}
```

- Pętle jak chcemy mieć wartość i klucz ze zbioru

```twig
{% for klucz, element in zbior.items %}
    {{ klucz }} : {{ element }}
{% endfor %}
```

---

- Komentarz (Wąs hasz)

```twig
{# Tekst nie wyrenderowany na stronie #}
```

---

- Dobieranie się do pola w przekazanym obiekcie

```twig
{{ student.first_name }}
```

- Dobieranie się do wartości w tupli

```twig
{{ nasza_tupla.0 }} pierwszy element tupli
{{ nasza_tupla.1 }} drugi element tupli
```

---

- Instrukcje warunkowe

```twig
{% if warunek %}
    Jak prawda
{% elif warunek2 %}
    Jak inna prawda
{% else %}
    Jak fałsz
{% endif%}
```

`Ważne` jeśli danej zmiennej nie ma w kontekscie warunek `if` zwróci `False`.

## Załączanie do szablonu innych szablonów

```twig
{% include 'formularz.html' %}
```

## Dziedziczenie szablonów

Ważne linijka ta powinna znaleźć się na początku szablonu, w którym chcemy dzie

```twig
{% extends 'szablon_którego_dziedziczymy.html' %}
```

---

- przygotowanie bloku w szablonie bazowym

```twig
{% block nazwabloku %}
Domyślna zawartość bloku jeśli go nie nadpiszemy w szablonie, który będzie z niego dziedziczyć
{% endblock%}
```

- nadpisanie zawartości w szablonie dziedziczącym

```twig
{% extends 'szablon_którego_dziedziczymy.html' %}

{% block nazwabloku %}
Nowa zawartość
{% endblock%}
```

---

- Generowanie url do formularzy/menu i innych miejsc

Przykładowy plik urls.py
```py

from django.urls import re_path, path

from exercises.views import SchoolClassView, UserList
urlpatterns = [
    path('class/<int:class_id>', SchoolClassView.as_view(), name="school-class"),
    path('list_users', UserList.as_view(), name="list-view"),
]

```

Do tej pory wstawialiśmy w hmtl/template linki pisane ręcznie.
Django pozwala nam na dynamiczne generowanie tych linków.
W szablonach dokonujemy tego przez tag `url`

```twig
<a href="{% url 'list-view' %}">Link do listy użyszkodników</a>
<a href="{% url 'school-class' class_id=3 %}">Link do widoku klasy o id 3</a>
```

Tag ten wykorzystujemy, ponieważ pozwala on na trzymanie w jednym miejscu informacji o danym linku i jeśli będziemy chcieli go zmienić na inny. 
Wystarczy, że zmienimy go tylko w pliku urls.py, a zmiany zostaną zastosowane w wszystkich miejscach gdzie dany url jest generowany na podstawie etykiety (`name`).

Jeśli chcemy wygenerować link w kodzie pythona mamy dwie możliwości.

```py
reverse('list-view')
reverse_lazy('list-view')
```

Różnica między nimi polega na tym, że `reverse` odrazu wypluwa url, a drugi `reverse_lazy` wypluwa url dopiero wtedy, będzie użyty.
Użycie `reverse_lazy` możesz zobaczyć w pliku `0002_Formularze.MD` w sekcji CREATE VIEW, gdzie do ustawienia success_url.
