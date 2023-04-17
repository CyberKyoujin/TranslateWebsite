from django.urls import path
from . import views

app_name = 'translator_app'

urlpatterns = [
    path('signup/', views.signup_page, name='signup'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('translations/', views.translation_page, name='translations'),
    path("wordbook/", views.wordbook_page, name="wordbook"),
    path('translator/', views.translator_page, name='translator'),
    path('translations/<int:pk>/details/', views.translation_detail, name='translation_detail'),
    path('translations/<int:pk>/delete/', views.TranslationDelete.as_view(), name='translation_delete'),
    path('wordbook/<int:pk>/delete/', views.WordDeleteView.as_view(), name='word_delete'),
    path('wordbook/<int:pk>/details/', views.word_detail, name='word_detail'),
]