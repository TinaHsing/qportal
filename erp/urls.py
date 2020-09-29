from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns =[
	path('', views.erpindex, name='erpindex'),
	path('partNumber/', views.viewPartNumber, name = 'viewPartNumber'),
	path('addCategory/', views.addCategory, name = 'addCategory'),
	path('addPartNumber/', views.addPartNumber, name = 'addPartNumber'),
	path('BOM/', views.viewBomList, name = 'viewBomList'),
	path('BOM/<int:Pid>/', views.editBomList, name = 'editBomList'),
	path('BOM/<int:Pid>/<int:Bid>/', views.addElement, name = 'addElement'),
	path('BOM/Upload/<int:Pid>/', views.uploadBom, name='uploadBom'),
	path('purchasing/', views.purchasing, name = 'purchasing'),
	path('purchasing/<int:Pid>/', views.addPurchasing, name = 'addPurchasing'),
	path('purchasing/Upload/', views.uploadPO, name = 'uploadPO'),
	path('discard/', views.discard, name = 'discard'),
	path('discard/<int:Pid>/', views.addDiscard, name = 'addDiscard'),
	path('planer/', views.planer, name ='planer'),
	path('planer/<int:Pid>/',views.addPlaner, name= 'addplaner'),
	path('planer/calculate/', views.PdCalculate, name ='calculate'),
	path('production/', views.PdRecord, name ='production'),
	path('production/<int:Pid>/', views.addPdRecord, name = 'addPdRecord'),
	
	#path('partNumber/', views.viewPartNumber, name = 'viewPartNumber'),
	#path(r'partNumber/?pnKW=(?P<pnKW>\W+)', views.selectPartNumber, name='selectPartNumber')
	#path('partNumber/', views.selectPartNumber.as_view(), name='selectPartNumber'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)