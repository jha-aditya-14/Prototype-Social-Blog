from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Define your URL patterns here

admin.site.site_header="Blog App"
urlpatterns = [
    path('', views.signin, name='signin'),
    path('sign-up/', views.signup, name='signup'),
    path('<int:user_id>/dashboard/', views.dashBoard, name='dashBoard'),
    path('<int:user_id>/personal-blogs/', views.personalBlogs, name='personalBlogs'),
    path('<int:user_id>/deleteBlog/<int:id>/', views.deleteBlog, name='deleteBlogs'),
    path('<int:user_id>/update-blog/<int:id>/', views.updateBlog, name='updateBlogs'),
    path('<int:user_id>/profile/', views.profile, name='profile'),
    path('<int:user_id>/profile/new-blog/', views.addNewBlog, name='newBlog'),
    path('<int:user_id>/profile/upoad-profile-img/', views.uploadProfileImage, name='profileImg'),
    path('<int:user_id>/profile/update-userInfo/', views.updateUserInfo, name='updateUserinfo'),
    path('<int:user_id>/settings/', views.setting, name='settings'),
    path('<int:user_id>/change-passw/', views.changePass, name='changePassw'),
    path('<int:user_id>/verify-user-otp/', views.verifyUserOtp, name='verifyUserOtp'),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)