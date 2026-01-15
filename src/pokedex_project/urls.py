from django.contrib import admin
from django.urls import path
from analysis.views import pokedex_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pokedex_view, name='home'),
]
