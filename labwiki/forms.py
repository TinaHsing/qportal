from django import forms
from .models import Article, Category
from django.core.exceptions import ValidationError

class ArticleForm(forms.ModelForm):
    class Meta:
        """Use Element model"""
        model = Article
        fields = ['title', 'content', 'category']
        widgets = {'category':forms.CheckboxSelectMultiple(),
                    'title':forms.TextInput(attrs={'size':'110%'}),
                    'content':forms.Textarea(attrs={'rows':150 ,'cols':'20%'})
                }

class CategoryForm(forms.ModelForm):
    class Meta:
        """ Use the Category model """
        model = Category
        fields = ['name','parent']


  