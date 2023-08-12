from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import ResumeShow

# 注册ArticlePost到admin中
admin.site.register(ResumeShow)
