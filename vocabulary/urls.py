from django.urls import path
from . import views

app_name = 'vocabulary'

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('learn/<int:word_id>/', views.learn_word, name='learn_word'),
    path('quiz/<slug:slug>/', views.quiz, name='quiz'),
    path('profile/', views.profile, name='profile'),
    path('export/pdf/<slug:slug>/', views.export_pdf, name='export_pdf'),
]