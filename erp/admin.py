from django.contrib import admin

# Register your models here.
from .models import partNumber, pnCategory, BomElement, QtyReason
from .models import elePrice, pnQty, planerElement, partNote
from .models import bomDefine, purchaseList, mpList
from .models import customer, ccnList, software, endProduct

admin.site.register(partNumber)
admin.site.register(pnCategory)
admin.site.register(BomElement)
admin.site.register(QtyReason)
admin.site.register(elePrice)
admin.site.register(pnQty)
admin.site.register(planerElement)
admin.site.register(partNote)
admin.site.register(bomDefine)
admin.site.register(purchaseList)
admin.site.register(mpList)
admin.site.register(customer)
#admin.site.register(ccnList)
#admin.site.register(software)
admin.site.register(endProduct)
