from django.contrib import admin

# Register your models here.
from .models import partNumber, pnCategory, BomElement, QtyReason
from .models import elePrice, pnQty, planerElement, partNote

admin.site.register(partNumber)
admin.site.register(pnCategory)
admin.site.register(BomElement)
admin.site.register(QtyReason)
admin.site.register(elePrice)
admin.site.register(pnQty)
admin.site.register(planerElement)
admin.site.register(partNote)
