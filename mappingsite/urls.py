from django.urls import path
from . import views
from django.views.generic import ListView

app_name = 'mappingsite'
urlpatterns = [
    path('', views.mainview, name="main"),
    path('<task>/<urlid>/<fmt>/', views.checkview, name="check"),
    path('<task>/<urlid>/<fmt>/<date>/', views.displayview, name="display")
]