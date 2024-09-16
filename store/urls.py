from django.urls import path, re_path
from . import views
from .views import *
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

app_name = 'store'

urlpatterns = [

	path('', views.home, name='home'),

	#pages
	path('kontakt', views.kontakt, name='kontakt'),
	path('montage', views.firma, name='firma'),
	path('anleitungen', views.anleitung_videos, name='anleitung_videos'),
	path('impressum', views.impressum, name='impressum'),
	path('bestellformular', views.bestellformular, name='bestellformular'),
	path('danke', views.danke, name='danke'),

	#shop
	path('bestätigung/<int:pk>', views.email, name='email'),
	path('searchbar', views.searchbar, name='searchbar'),
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
	path('dichtungen/m/<str:cat_marke>', HomeMarkeView, name="markedetails"),
	path('dichtungen/marke/', views.marke, name="marke"),
	path('p/<slug:slug>/', product_detail, name='product-detail'), 
	path('p/weitere-dichtungen/<slug:slug>/', weitere_product_detail, name='weitere_product_detail'), 
	path('add-to-cart/<slug:slug>/<int:pk>/', add_to_cart, name='add_to_cart'),
	path('add-to-cart-myd/<slug:slug>/<int:pk>/<int:aussenbreite>/<int:aussenhöhe>/<int:anzahl>/<int:element>', add_to_cart_myd, name='add_to_cart_myd'),
	path('remove-from-cart/<slug:slug>/<int:pk>/', remove_from_cart, name='remove_from_cart'),
	path('remove-item-from-cart/<slug:slug>/<int:pk>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
	path('rechnung/', views.Rechnung, name='rechnung'),

	#crm kunden
	path('cms/crm/kunden', views.crm_new_kunden, name='crm_new_kunden'),
	path('cms/crm/kunden/bearbeiten/<int:pk>', views.crm_new_kunde_bearbeiten, name='crm_new_kunde_bearbeiten'),
	path('cms/crm/adresse/bearbeiten/<int:pk>', views.cms_crm_adresse_bearbeiten, name='cms_crm_adresse_bearbeiten'),
	path('cms/crm/kunde/löschen/<int:pk>', views.cms_crm_kunde_löschen, name='cms_crm_kunde_löschen'),
	path('cms/crm/kunde/erfassen', views.crm_new_kunde_erfassen, name='crm_new_kunde_erfassen'),
	path('cms/crm/<int:pk>/update_last_service/', views.crm_update_last_service, name='crm_update_last_service'),
	path('kunde/delete-user-relationship/<int:pk>/', views.delete_kunde_user_relationship, name='delete_kunde_user_relationship'),

	#cms 
	path('cms/', views.cms, name="cms"),
	path('cms/bestellungen', views.cms_bestellungen, name='cms_bestellungen'),
	path('cms/bestätigung/<int:pk>', views.cms_bestellung_confirmation, name='cms_bestellung_confirmation'),

	#webshop kunden
	path('cms/webshop/kunden', views.cms_kunden, name='cms_kunden'),
	path('cms/webshop/erfassen', views.cms_kunden_erfassen, name='cms_kunden_erfassen'),
	path('cms/user/bearbeiten/<int:pk>', views.cms_user_bearbeiten, name='cms_user_bearbeiten'),
	path('cms/kundenadresse/bearbeiten/<int:pk>', views.cms_kundenadresse_bearbeiten, name='cms_kundenadresse_bearbeiten'),
	path('cms/webshop//bearbeiten/<int:pk>', views.cms_kunde_bearbeiten, name='cms_kunde_bearbeiten'),
	path('cms/webshop/löschen/<int:pk>', views.cms_kunde_löschen, name='cms_kunde_löschen'),

	#produkte
	path('cms/produkte/<str:first_cat>', views.cms_produkte, name='cms_produkte'),
	path('cms/produkte/bearbeiten/<int:pk>/<str:current_cat>', views.product_cms_edit, name='cms_produkte_edit'),
	path('cms/produkte/löschen/<int:pk>/<str:cat>', views.cms_remove_product, name='cms_remove_product'),
	path('cms/produkte/erfassen/<str:cat>', views.product_cms_create, name='product_cms_create'),
	path('cms/produkte-marke/<int:pk>', views.cms_product_marke_overview, name='cms_product_marke_overview'),
	path('cms/produkte-marke/erfassen/<int:pk>', views.cms_product_marke_erfassen, name='cms_product_marke_erfassen'),
	path('cms/produkte-marke/löschen/<int:pkk>/<int:pk>', views.cms_product_marke_löschen, name='cms_product_marke_löschen'),
	
	#elemente
	path('cms/elemente/statistik', views.cms_elemente_statistik, name='cms_elemente_statistik'),
	path('cms/elemente/<int:pk>', views.cms_elemente, name='cms_elemente'),
	path('cms/elemente/erfassen/<int:pk>', views.cms_elemente_create, name='cms_elemente_create'),
	path('cms/elemente/bearbeiten/<int:pk>/<int:cpk>', views.cms_elemente_edit, name='cms_elemente_edit'),
	path('cms/elemente/löschen/<int:pk>/<int:cpk>', views.cms_elemente_löschen, name='cms_elemente_löschen'),
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
	
	#objekte
	path('cms/elemente/objekte/<int:pk>/<int:cpk>', views.cms_elemente_objekte, name='cms_elemente_objekte'),
	path('cms/elemente/objekte-erfassen/<int:pk>/<int:cpk>', views.cms_elemente_objekte_erfassen, name='cms_elemente_objekte_erfassen'),
	path('cms/elemente/objekte-bearbeiten/<int:pk>/<int:epk>/<int:cpk>', views.cms_elemente_objekte_bearbeiten, name='cms_elemente_objekte_bearbeiten'),
	path('cms/elemente/objekte-loeschen/<int:pk>/<int:epk>/<int:cpk>', views.cms_elemente_objekte_löschen, name='cms_elemente_objekte_löschen'),

	re_path(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots_file"),
	
    #path('pdf_view/', views.ViewPDF.as_view(), name="pdf_view"),
    #path('pdf_download/', views.DownloadPDF.as_view(), name="pdf_download"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

