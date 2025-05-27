from django.conf import settings
from store.models import Category, Subcategory, Item, Marke

def custom_sort(cat):
    order = {
        "Marke": 0,
        "PVC mit Magnet": 1,
        "PVC ohne Magnet": 2,
        "Gummidichtung": 3,
        "EPDM-Moosgummi": 4,
        "Ofen/Steamer Dichtung": 5,  # <-- genau hier einsortiert
        "Weitere Dichtungen": 6,
        "Zubehör": 7,
    }
    return order.get(cat.name, 99)  # unbekannte Kategorien ans Ende


def extras(request):
    cat_menu = list(Category.objects.all())
    cat_menu_sorted = sorted(cat_menu, key=custom_sort)
    return {'cat_menu': cat_menu_sorted}



def sub_extras(request):
	subcat_menu = Subcategory.objects.all()

	return {
		'subcat_menu': subcat_menu,
		}

def extras_marke(request):
	marke_menu = Marke.objects.all().count()
	return {'marke_menu': marke_menu}


def first_cat(request):
    catquery = Category.objects.order_by('name').first()
    
    if catquery:  # Check if catquery is not None
        first_cat = catquery.name
    else:
        first_cat = None  # Or a default value if no category exists
    
    return {'first_cat': first_cat}

	