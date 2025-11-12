from django.urls import path
from petguard import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path("animais/adicionar/", views.add_animal, name="adicionar_animal"),
    path("animais/editar/<int:id>/", views.add_animal, name="editar_animal"),
    path('index/', views.index, name='index'),
    path('logout/', views.logout_view, name='logout'),
    path('animais/excluir/<int:animal_id>/', views.excluir_animal, name='excluir_animal'),
    path('perfil/', views.perfil, name='perfil'),
]
