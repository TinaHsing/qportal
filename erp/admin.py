from django.contrib import admin

# Register your models here.
from .models import partNumber, pnCategory, BomElement, QtyReason
from .models import elePrice, pnQty, planerElement, partNote
from .models import bomDefine, purchaseList, mpList
from .models import customer, ccnList, software, endProduct


#admin.site.register(pnCategory)
#admin.site.register(BomElement)
#admin.site.register(QtyReason)
#admin.site.register(planerElement)
admin.site.register(partNote)
admin.site.register(bomDefine)
#admin.site.register(purchaseList)
admin.site.register(mpList)
admin.site.register(customer)
#admin.site.register(ccnList)
admin.site.register(software)

@admin.register(partNumber)
class partNumberAdmin(admin.ModelAdmin):
	list_display =('name','approve', 'discription')
	list_filter =('approve',)

@admin.register(elePrice)
class elePriceAdmin(admin.ModelAdmin):
	list_display =('partNumber','price', 'user', 'date')
	list_filter =('user','date')
	search_fields = ('partNumber__name',)

@admin.register(BomElement)
class BomElementAdmin(admin.ModelAdmin):
	list_display =('bf','part', 'unitQty', 'user')
	list_filter =('user',)
	search_fields = ('part__name', 'bf__product__name')

@admin.register(endProduct)
class endProductAdmin(admin.ModelAdmin):
	list_display =('part', 'serial', 'status')
	list_filter =('status',)
	search_fields = ('part__name',)
@admin.register(pnQty)
class pnQtyAdmin(admin.ModelAdmin):
	list_display =('partNumber', 'reason', 'Qty', 'user', 'date')
	list_filter =('reason', 'user', 'date')
	search_fields = ('partNumber__name',)

