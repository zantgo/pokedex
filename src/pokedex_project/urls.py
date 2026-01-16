from django.contrib import admin
from django.urls import path
from analysis.views import pokedex_view, sync_data_view 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pokedex_view, name='home'),
    path('sync-data/', sync_data_view, name='sync_data'),
]