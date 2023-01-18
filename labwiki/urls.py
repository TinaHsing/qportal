"""url for labManager app
"""
from django.urls import path

from .views import NewArticle, Labwiki, NewTag, AddSucess 
from .views import ViewTag, ViewArticle, UpdateArticle, UpdateTag
# from . import views

urlpatterns = [
path('Article/<int:pk>', ViewArticle.as_view()),
path('Article/<int:pk>/update', UpdateArticle.as_view()),
path('', Labwiki.as_view(), name = 'Labwiki' ),
path('NewArticle', NewArticle.as_view(), name = 'NewArticle' ),
path('NewTag', NewTag.as_view(), name = 'NewArticleTag' ),
path('AddSucess', AddSucess.as_view()),
path('Tag/<int:pk>', ViewTag.as_view()),
path('Tag/<int:pk>/update', UpdateTag.as_view()),
]
