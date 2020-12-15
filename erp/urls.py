from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns =[
	path('', views.erpindex, name='erpindex'),
	path('partNumber/', views.viewPartNumber, name = 'viewPartNumber'),
	path('partNumber/<int:Pid>/', views.editPartNumber, name = 'editPartNumber'),
	path('partNumber/upload/', views.uploadPart, name = 'uploadPart'),
	path('addCategory/', views.addCategory, name = 'addCategory'),
	path('addPartNumber/', views.addPartNumber, name = 'addPartNumber'),
	path('BOM/', views.viewBomList, name = 'viewBomList'),
	path('BOM/<int:Pid>/', views.viewBomDefine, name = 'viewBomDefine'),
	path('BOM/<int:Pid>/new/', views.newBomDefine, name = 'newBomDefine'),
	path('BOM/<int:Pid>/<int:Serial>/', views.editBomList, name = 'editBomList'),
	path('BOM/<int:Pid>/<int:Serial>/cost/', views.costEvaluation, name = 'costEvaluation'),
	path('BOM/<int:Pid>/<int:Serial>/<int:Bid>/', views.addElement, name = 'addElement'),
	path('BOM/<int:Pid>/<int:Serial>/upload/', views.uploadBom, name='uploadBom'),
	path('purchasing/', views.purchasing, name = 'purchasing'),
	path('purchasing/<int:Pid>/', views.addPurchasing, name = 'addPurchasing'),
	path('purchasing/Upload/', views.uploadPO, name = 'uploadPO'),
	path('discard/', views.discard, name = 'discard'),
	path('discard/<int:Pid>/', views.addDiscard, name = 'addDiscard'),
	path('planer/', views.planer, name ='planer'),
	path('planer/<int:bomserial>/',views.addPlaner, name= 'addplaner'),
	path('planer/calculate/', views.PdCalculate, name ='calculate'),
	path('production/', views.PdRecord, name ='production'),
	path('production/<int:Pid>/', views.addPdRecord, name = 'addpPdRecord'),
	path('testing/', views.testRecord, name ='testing'),
	path('testing/<int:Pid>/', views.addTestRecord, name ='addTesting'),
	path('puraseList/', views.viewPurchaseList, name = 'purchaseList'),
	path('puraseList/<int:Pid>/', views.addPurchaseList, name = 'addPurchaseList'),
	path('puraseList/close/<int:serial>/', views.closePurchaseList, name = 'closePurchaseList'),
	path('mpList/', views.viewMpList, name = 'mpList'),
	path('mpList/<int:Pid>/', views.addMpList, name = 'addMpList'),
	path('mpList/close/<int:serial>/', views.closeMpList, name = 'closeMpList'),
	path('ccnList/', views.viewCCNList, name = 'ccnList'),
	path('ccnList/<int:Pid>/', views.addCCNList, name = 'addCCNList'),
	path('ccnList/close/<int:serial>/', views.closeCCN, name = 'closeCCN')
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)