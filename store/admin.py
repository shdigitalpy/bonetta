from django.contrib import admin
from .models import *
from django.utils.translation import gettext_lazy as _


class ElementeAdmin(admin.ModelAdmin):
    list_display = ('elementnr', 'get_artikelnummer', 'get_kunden')  # Anzeige-Spalten
    search_fields = ('elementnr', 'artikel__artikelnr', 'kunden__name')  # Suchfelder
    filter_horizontal = ('kunde',)  # Improves ManyToMany selection in admin

    def get_artikelnummer(self, obj):
        """ Zeigt die Artikelnummer des verknüpften Artikels an """
        return obj.artikel.artikelnr if obj.artikel else "Kein Artikel"
    get_artikelnummer.short_description = "Artikelnummer"  # Spaltenüberschrift setzen

    def get_kunden(self, obj):
        """ Zeigt die verknüpften Kunden als Liste an """
        return ", ".join([kunde.firmenname for kunde in obj.kunde.all()]) if obj.kunde.exists() else "Kein Kunde"
    get_kunden.short_description = "Kunden"

    
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(Elemente, ElementeAdmin)
admin.site.register(Kunde)
admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(ShippingCost)
admin.site.register(ShippingAddress)
admin.site.register(Marke)
admin.site.register(CRMAddress)
admin.site.register(Artikel)
admin.site.register(Elemente_Bestellungen)
admin.site.register(ElementeCartItem)
admin.site.register(LieferantenBestellungen)
admin.site.register(LieferantenStatus)
admin.site.register(LieferantenBestellungenArtikel)

admin.site.site_header = 'Bonetta CMS'                    # default: "Django Administration"
admin.site.index_title = 'Übersicht Module'                 # default: "Site administration"
admin.site.site_title = 'Django Seitenadministration' # default: "Django site admin"
