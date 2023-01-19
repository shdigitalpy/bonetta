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
