from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(Elemente)
admin.site.register(Kunde)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(ShippingCost)
admin.site.register(ShippingAddress)
admin.site.register(Marke)
admin.site.register(Marketplace)
admin.site.register(MP_Category)

admin.site.site_header = 'Bonetta CMS'                    # default: "Django Administration"
admin.site.index_title = 'Übersicht Module'                 # default: "Site administration"
admin.site.site_title = 'Django Seitenadministration' # default: "Django site admin"
