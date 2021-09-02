from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:user_id>/profile/', views.profile, name='profile'),
    path('<int:user_id>/unlike', views.unlike, name='unlike'),
    path('<int:image_id>/like/', views.like, name='like'),
    path('leaderboard/', views.LeaderboardView.as_view(), name='poll'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('<int:user_id>/add_image', views.add_image, name='add_image'),
    path('<int:user_id>/upload_file', views.upload_file, name='upload_file'),
]