from django.conf import settings
from store.models import Category, Subcategory, Item, Marke

def extras(request):
	cat_menu = Category.objects.all()
	return {'cat_menu': cat_menu}

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

	
def marken_context(request):
    bestseller_marken = Marke.objects.filter(bestseller=True).order_by('name')

    return {
        'marken': Marke.objects.all(),
        'bestseller_marken': bestseller_marken,
    }