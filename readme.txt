## start project ##
django-admin start project [project name:qportal]
## create app ##
python3 manage.py startapp portal
## register app in qportal/settings.py
INSTALL_APPS = [....., 
	'portal.apps.PortalConfig']
## hooking the url mapper in portal/urls.py

from django.urls import include, path
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('portal/', include('portal.urls')),
    path('',RedirectView.as_view(url='/erp/'))
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

## migrate the deta base ##
python3 mamage.py makemigrations
python3 manage.py migrate

## runserver to test ##
python3 manage.py runserver

## CreateSupper User ##
python3 manage.py createsuperuser

## Create Page  ##
所有的 template 都可以放在這裡
in qportal/template/ 
create base_generic.html
create index.html

modify portal/views.py

## register models for admin editing##
add following code in erp/admin.py
admin.site.register(partNumber)

## login 後重新導向首頁 ##
in qportal/settings.py
LOGIN_REDIRECT_URL = '/'

## 新增頁面功能順序 ##
1. 修改 views
2. 新增 html template
3. 添加  urlpattern in url.py



