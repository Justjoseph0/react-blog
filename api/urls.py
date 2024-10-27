from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', views.CreateUserView.as_view(), name='create-user'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create_profile/',views.update_profile,name='update_profile'),
    path('profile/',views.view_profile,name='profile'),
    path('check-profile/', views.has_profile, name='check-profile'),
    path('dashboard/',views.dashboad,name='dashboard'),
    path('posts/',views.posts_list,name='posts'),
    path('create_post/',views.create_post,name='create_post'),
    path('posts/<slug:slug>/', views.post_detail, name='post-detail'),
    path('posts/edit/<slug:slug>/', views.edit_post, name='edit_post'),
    path('posts/delete/<slug:slug>/', views.post_delete, name='post_delete'),
    path('comment/delete/<int:id>/', views.comment_delete, name='comment_delete'),
    path('posts/comments/<slug:slug>/', views.create_comment, name='create_comment'),
    path('posts/get_comments/<slug:slug>/', views.get_comment_for_post, name='get_comment_for_post'),
    path('auth/user/', views.current_user, name='get_current_user'),
    path('profile/<str:username>/', views.user_details, name='user-profile'),
]
