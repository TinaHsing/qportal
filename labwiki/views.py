from django.shortcuts import render
from .forms import ArticleForm, CategoryForm
from django.views.generic import TemplateView, CreateView, ListView, DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from datetime import date
from . models import Article, Category
from markdownx.utils import markdownify
# Create your views here.

class AddSucess(TemplateView):
    """View for Add Category Sucess
    """
    template_name = 'AddArticleSucess.html'

class Labwiki(TemplateView):
    template_name='Labwiki.html'

    def get_context_data(self):
        articles = Article.objects.order_by('-date')[:20]
        context = {'articles':articles}
        return context

class NewArticle(PermissionRequiredMixin, CreateView):
    """
    Create NewArticle page view, user can add new article
    """
    template_name = 'AddArticle.html'
    form_class = ArticleForm
    model = Article
    success_url = 'AddSucess'
    permission_required ='labManager.add_elecategory'

    def form_valid (self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.date = date.today()
        obj.save()
        return super().form_valid(form)

class NewTag(PermissionRequiredMixin, CreateView):
    """
    Create Category page view, user can add the elelment category
    """
    template_name = 'AddArticleTag.html'
    form_class = CategoryForm
    model = Category
    success_url = 'AddSucess'
    permission_required ='labwiki.add_category'

    def form_valid (self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.date = date.today()
        obj.save()
        return super().form_valid(form)

class ViewTag(ListView):
    template_name = 'Labwiki.html'
    model = Article
    context_object_name = 'articles'

    def get_queryset(self):
        pk = self.kwargs['pk']
        articles = Article.objects.filter(category__id = pk)
        return articles

class ViewArticle(DetailView):
    template_name = 'ViewArticle.html'
    model = Article

class UpdateArticle(UpdateView):
    template_name = 'AddArticle.html'
    model = Article
    form_class = ArticleForm
    success_url = 'AddSucess'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.update_user = self.request.user 
        obj.update_date = date.today()
        obj.save()
        return super().form_valid(form)
