from django.urls import path

# 正在部署的应用的名称
from . import views

app_name = 'resume'

urlpatterns = [
    # 目前还没有urls
    path('resume-list/', views.resume_list, name='resume_list'),
    path('resume-detail/<int:id>/', views.resume_detail, name='resume_detail'),
]
