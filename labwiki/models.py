from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User

# Create your models here.
    
class Category(MPTTModel):
    name = models.CharField(max_length= 50, unique= True)
    parent = TreeForeignKey('self', on_delete = models.PROTECT, null = True, blank=True, \
        related_name='children')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null= True, blank = True)
    date = models.DateField(null = True, blank = True)
    def __str__(self):
        return str(self.name)

class Article(models.Model):
    title = models.CharField(max_length = 100)
    category = models.ManyToManyField(Category, blank= False)
    content = MarkdownxField()
    user = models.ForeignKey(User,related_name ='article_auther',on_delete=models.SET_NULL, null= True, blank = True)
    date = models.DateField(null = True, blank = True)
    update_user = models.ForeignKey(User,related_name ='article_update',on_delete=models.SET_NULL, null= True, blank = True)
    update_date = models.DateField(null = True, blank = True)
    def formated_markdown(self):
        return markdownify(self.content)
    
    def __str__(self):
        return str(self.title)


