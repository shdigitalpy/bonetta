from django.urls import path, re_path
from . import views
from .views import *
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView


app_name = 'store'

urlpatterns = [

	path('', views.home, name='home'),
	path('bestätigung/<int:pk>', views.email, name='email'),
	path('searchbar', views.searchbar, name='searchbar'),
	path('kontakt', views.kontakt, name='kontakt'),
	path('impressum', views.impressum, name='impressum'),
	path('checkout/', CheckoutView.as_view(), name='checkout'), 
	path('payment/', PaymentView.as_view(), name='payment'), 
	path('order-summary', OrderSummaryView.as_view(), name='order_summary'),
	path('final-summary', FinalSummaryView.as_view(), name='final_summary'),
	path('einstellungen', views.einstellungen, name='einstellungen'),
	path('lieferadresse', views.lieferadresse, name='lieferadresse'),
	path('lieferadresse/erfassen', views.create_lieferadresse, name='lieferadresse_erfassen'),
	path('bestellungen', views.bestellungen, name='bestellungen'),
	path('mydichtungen', views.mydichtungen, name='mydichtungen'),
	path('dichtung/<str:cats>', HomeProduktView, name="category"),
	path('dichtung/<str:cats>/<str:subcats>', HomeSubProduktView, name="subcategory"),
	path('dichtungen/m/<str:cat_marke>', HomeMarkeView, name="marke"),
	path('dichtungen/marke/', views.marke, name="marke"),
	path('p/<slug:slug>/', product_detail, name='product-detail'), 
	path('p/weitere-dichtungen/<slug:slug>/', weitere_product_detail, name='weitere_product_detail'), 
	path('add-to-cart/<slug:slug>/<int:pk>/', add_to_cart, name='add_to_cart'),
	path('add-to-cart-myd/<slug:slug>/<int:pk>/<int:aussenbreite>/<int:aussenhöhe>/<int:anzahl>/<int:element>', add_to_cart_myd, name='add_to_cart_myd'),
	path('remove-from-cart/<slug:slug>/<int:pk>/', remove_from_cart, name='remove_from_cart'),
	path('remove-item-from-cart/<slug:slug>/<int:pk>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
	path('rechnung/', views.Rechnung, name='rechnung'), 
	path('cms/', views.cms, name="cms"),
	path('cms/bestellungen', views.cms_bestellungen, name='cms_bestellungen'),
	path('cms/bestätigung/<int:pk>', views.cms_bestellung_confirmation, name='cms_bestellung_confirmation'),
	path('cms/kunden', views.cms_kunden, name='cms_kunden'),
	path('cms/kunden/erfassen', views.cms_kunden_erfassen, name='cms_kunden_erfassen'),
	path('cms/user/bearbeiten/<int:pk>', views.cms_user_bearbeiten, name='cms_user_bearbeiten'),
	path('cms/kundenadresse/bearbeiten/<int:pk>', views.cms_kundenadresse_bearbeiten, name='cms_kundenadresse_bearbeiten'),
	path('cms/kunden/bearbeiten/<int:pk>', views.cms_kunde_bearbeiten, name='cms_kunde_bearbeiten'),
	path('cms/kunden/löschen/<int:pk>', views.cms_kunde_löschen, name='cms_kunde_löschen'),
	path('cms/produkte', views.cms_produkte, name='cms_produkte'),
	path('cms/produkte/bearbeiten/<int:pk>', views.product_cms_edit, name='cms_produkte_edit'),
	path('cms/produkte/löschen/<int:pk>', views.cms_remove_product, name='cms_remove_product'),
	path('cms/produkte/erfassen', views.product_cms_create, name='product_cms_create'),
	path('cms/elemente/<int:pk>', views.cms_elemente, name='cms_elemente'),
	path('cms/elemente/erfassen/<int:pk>', views.cms_elemente_create, name='cms_elemente_create'),
	path('cms/elemente/bearbeiten/<int:pk>/', views.cms_elemente_edit, name='cms_elemente_edit'),
	path('cms/elemente/löschen/<int:pk>', views.cms_elemente_löschen, name='cms_elemente_löschen'),
	path('cms/benutzerdaten', views.cms_benutzerdaten, name='cms_benutzerdaten'),
	path('cms/versandkosten', views.cms_versandkosten, name='cms_versandkosten'),
	path('cms/versandkosten/erfassen', views.cms_versandkosten_erfassen, name='cms_versandkosten_erfassen'),
	path('cms/remove-versandkosten/<int:pk>/', views.cms_remove_versandkosten, name='cms_remove_versandkosten'),
	path('cms/marken', views.cms_marken, name='cms_marken'),
	path('cms/marke/erfassen', views.cms_marke_erfassen, name='cms_marke_erfassen'),
	path('cms/marke/löschen/<int:pk>', views.cms_marke_löschen, name='cms_marke_löschen'),
	path('cms/marke/bearbeiten/<int:pk>', views.cms_marke_bearbeiten, name='cms_marke_bearbeiten'),
	path('cms/kennzahlen', views.cms_kennzahlen_webseite, name='cms_kennzahlen_webseite'),
	path('cms/login_user', views.login_user, name='login_user'),
	path('cms/logout_user', views.logout_user, name='logout_user'),
	path('cms/statistik/produkte', views.cms_statistik_produkte, name='cms_statistik_produkte'),
	re_path(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_file"),
	#path('pdf_view/', views.ViewPDF.as_view(), name="pdf_view"),
    #path('pdf_download/', views.DownloadPDF.as_view(), name="pdf_download"),
	
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

