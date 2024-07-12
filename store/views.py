from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from django.views.generic import ListView, DetailView, View, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import *
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.shortcuts import reverse, HttpResponse
from django.db.models import Q, Count, Sum
from django.db.models.functions import Coalesce
from django.template.loader import render_to_string, get_template
from django.conf import settings
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
from django.contrib.admin.views.decorators import staff_member_required
from itertools import chain

@login_required
def marktplatz_jobinserat_erfolg(request, pk):
	mp = get_object_or_404(JobsMarketplace, id=pk)

	'''subject = 'Inserat Nr.' + ' ' + str(mp.id) + ' ' + mp.title + ' wurde erstellt.'
	if mp.condition == "G":
		condition = "Gebraucht"
	else:
		condition = "Neu"
	template = render_to_string('marktplatz/inserat-email-erfolg.html', {
			'title' : mp.title,
			'price': mp.price, 
			'condition': mp.condition,
			'place': mp.place,
			'add_date': mp.add_date,
			'category': mp.category,		
					 })
	email = ''	
	#send email for order
	email = EmailMessage(
			subject,
			template,
			email,
			['sandro@sh-digital.ch','livio.bonetta@geboshop.ch'],
				)
	email.fail_silently=False
	email.content_subtype = "html"
	email.send()'''

	context = {

	'mp' : mp,
		
				}
	return render(request, 'marktplatz/marktplatz-jobs-erfolg.html', context)


@login_required
def marktplatz_jobinserat_summary(request, pk):
	mp = get_object_or_404(JobsMarketplace, id=pk)

	if request.method == "POST":
		#return redirect(link)
		return redirect ("store:marktplatz_jobinserat_erfolg", pk=mp.id)

	else:
		context = {	
			'inserat' : mp,
				
				}
	
		return render(request, 'marktplatz/marktplatz-jobsummary.html', context)

@login_required
def marktplatz_jobinserat_ändern(request, pk):
	inserat = get_object_or_404(JobsMarketplace, id=pk)
	
	if request.method == "POST":
		form = InseratJobsCreateForm(request.POST or None, request.FILES or None, instance=inserat)
		if form.is_valid():
			mp = form.save(commit=False)
			mp.user = request.user
			mp.save()
			return redirect('store:marktplatz_jobinserat_summary', pk=mp.id)

		else:
			messages.error(request, "Error")

	else: 
		form = form = InseratJobsCreateForm(instance=inserat)

	context = {
		'form': form,
				}
	return render(request, 'marktplatz/marktplatz-inserat-erfassen.html', context)


@login_required
def marktplatz_jobinserat_erfassen(request):
	if request.method == "POST":
		form = InseratJobsCreateForm(request.POST or None,request.FILES or None,)
		if form.is_valid():
			mp = form.save(commit=False)
			mp.user = request.user
			mp.save()
			
			return redirect('store:marktplatz_jobinserat_summary', pk=mp.id)

		else:
			messages.error(request, "Error")

	else: 
		form = form = InseratJobsCreateForm()

	context = {
		'form': form,
				}
	return render(request, 'marktplatz/marktplatz-jobs-erstellen.html', context)



def anleitung_videos(request):
	

	context = {
	

	}
	return render (request, 'anleitung-videos.html', context)

def marktplatz_video(request):
	context = {
	
	}
	return render (request, 'marktplatz/marktplatz-video.html', context)

def marktplatz_jobs(request):
	mp_categories = MP_JobsCategory.objects.all().order_by('name')
	search_query = request.GET.get('search', '')

	if search_query:
		mp_inserate = JobsMarketplace.objects.filter(Q(place__icontains=search_query) | Q(region__icontains=search_query))

	else:
		mp_inserate = JobsMarketplace.objects.all()


	context = {

	'mp_inserate': mp_inserate,
	'mp_categories': mp_categories,
	

	}
	return render (request, 'marktplatz/marktplatz-jobs.html', context)

def marktplatz_overview(request):
	
	context = {

			
		
				}
	return render(request, 'marktplatz/marktplatz-overview.html', context)

@login_required
def marktplatz_zahlung(request, pk, tid):
	mp = get_object_or_404(Marketplace, id=pk)
	#### regular
	context = {

			'inserat' : mp,
		
				}
	return render(request, 'marktplatz/marktplatz-zahlung.html', context)

@login_required
def marktplatz_inserat_summary(request, pk):
	import urllib.request
	import hmac
	import hashlib
	import base64
	import json

	mp = get_object_or_404(Marketplace, id=pk)

	betrag = 1500
	sku = int(mp.id) + 1000

	post_data = {
	"amount": betrag,
	"vatRate": 8.1,
	"currency": "CHF",
	"sku": sku,
	"preAuthorization": 0,
	"reservation": 0,
	"successRedirectUrl": settings.PAYMENT_SUCCESS_URL,
	"failedRedirectUrl": settings.PAYMENT_DECLINE_URL

			}

	data = urllib.parse.urlencode(post_data).encode('UTF-8')

	string = settings.INSTANCE_API_SECRET
	as_bytes = bytes(string, 'UTF-8')

	dig = hmac.new(as_bytes, msg=data, digestmod=hashlib.sha256).digest()
	post_data['ApiSignature'] = base64.b64encode(dig).decode()
	post_data['instance'] = settings.INSTANCE_NAME

	data = urllib.parse.urlencode(post_data, quote_via=urllib.parse.quote).encode('UTF-8')

	try:
		payment_url = settings.PAYMENT_URL_OPEN

		url = urllib.request.urlopen(payment_url, data) 
		
		content = url.read().decode('UTF-8')
		response = json.loads(content)
		result = response['data'][0]['id']
		link = response['data'][0]['link']

	except Exception as exc:
		result = "Wrong"

	mp.tid = result
	mp.save()

	if request.method == "POST":
		#return redirect(link)
		return redirect ("store:marktplatz_inserat_erfolg", pk=mp.id)

	else:
		context = {	
			'inserat' : mp,
			'result' : result,
			'tid' : result,
		
				}
	
		return render(request, 'marktplatz/marktplatz-summary.html', context)

@login_required
def marktplatz_inserat_erfolg(request, pk):
	mp = get_object_or_404(Marketplace, id=pk)

	subject = 'Inserat Nr.' + ' ' + str(mp.id) + ' ' + mp.title + ' wurde erstellt.'
	if mp.condition == "G":
		condition = "Gebraucht"
	else:
		condition = "Neu"
	template = render_to_string('marktplatz/inserat-email-erfolg.html', {
			'title' : mp.title,
			'price': mp.price, 
			'condition': mp.condition,
			'place': mp.place,
			'add_date': mp.add_date,
			'category': mp.category,		
					 })
	email = ''	
	#send email for order
	email = EmailMessage(
			subject,
			template,
			email,
			['sandro@sh-digital.ch','livio.bonetta@geboshop.ch'],
				)
	email.fail_silently=False
	email.content_subtype = "html"
	email.send()

	context = {

	'mp' : mp,
		
				}
	return render(request, 'marktplatz/marktplatz-erfolg.html', context)

@login_required
def marktplatz_inserat_erfassen(request):
	if request.method == "POST":
		form = InseratCreateForm(request.POST or None,request.FILES or None,)
		if form.is_valid():
			mp = form.save(commit=False)
			mp.user = request.user
			mp.save()
			
			return redirect('store:marktplatz_inserat_summary', pk=mp.id)

		else:
			messages.error(request, "Error")

	else: 
		form = form = InseratCreateForm()

	context = {
		'form': form,
				}
	return render(request, 'marktplatz/marktplatz-inserat-erfassen.html', context)

@login_required
def marktplatz_inserat_ändern(request, pk):
	inserat = get_object_or_404(Marketplace, id=pk)
	
	if request.method == "POST":
		form = InseratCreateForm(request.POST or None, request.FILES or None, instance=inserat)
		if form.is_valid():
			mp = form.save(commit=False)
			mp.user = request.user
			mp.save()
			return redirect('store:marktplatz_inserat_summary', pk=mp.id)

		else:
			messages.error(request, "Error")

	else: 
		form = form = InseratCreateForm(instance=inserat)

	context = {
		'form': form,
				}
	return render(request, 'marktplatz/marktplatz-inserat-erfassen.html', context)

def marktplatz_main(request):
	

	mp_inserate = Marketplace.objects.all()

	mp_categories = MP_Category.objects.all()

	context = {

	'mp_inserate': mp_inserate,
	'mp_categories': mp_categories,
	

	}
	return render (request, 'marktplatz/marktplatz-main.html', context)





#myinserate benutzer übersicht

@login_required
def myinserate(request):
	myinserat = Marketplace.objects.filter(user=request.user)

	context = { 
			'myinserat': myinserat,
			
			}
	return render(request, 'marktplatz/marktplatz-inserate-benutzer.html', context)


@login_required
def myinserate_löschen(request, pk):
	element = get_object_or_404(Marketplace, pk=pk)
	if request.method == "POST":
		return redirect("store:myinserate-wirklich", pk=pk)

	else:
		messages.info(request, "Achtung!")
		context = {
		'element': element,
				}
		return render(request, 'marktplatz/marktplatz-inserate-wirklich-loeschen.html', context)


@login_required
def myinserate_wirklich(request, pk):
	eintrag = get_object_or_404(Marketplace, pk=pk)
	eintrag.delete()
	messages.info(request, "Das Inserat wurde gelöscht.")
	return redirect("store:myinserate")

@login_required
def myinserate_ändern(request, pk):
	inserat = get_object_or_404(Marketplace, id=pk)
	
	if request.method == "POST":
		form = InseratCreateForm(request.POST or None, request.FILES or None, instance=inserat)
		if form.is_valid():
			mp = form.save(commit=False)
			mp.user = request.user
			mp.save()
			return redirect('store:myinserate')

		else:
			messages.error(request, "Error")

	else: 
		form = form = InseratCreateForm(instance=inserat)

	context = {
		'form': form,
				}
	return render(request, 'marktplatz/marktplatz-inserate-benutzer-edit.html', context)

#myinserate benutzer übersicht end

def marktplatz_jobinserat_details(request, pk, slug):
	inserat = get_object_or_404(JobsMarketplace, id=pk, slug=slug)

	context = {

			'inserat' : inserat,

			}

	return render (request, 'marktplatz/marktplatz-jobinserat-details.html', context)

def marktplatz_inserat_details(request, slug):
	inserat = get_object_or_404(Marketplace, slug=slug)

	if request.user.is_authenticated:
		user = request.user 
		kunde = Kunde.objects.get(user=user)

		inserat_kunde = Kunde.objects.get(user=inserat.user)

		if request.method =="POST":
			nachricht = request.POST['message']
			

			subject = 'Anfrage für Inserat Nr. ' + str(inserat.id)
			template = render_to_string('marktplatz/inserat-verk-email.html', {
				'benutzer': user.username,
				'firma': kunde.firmenname,
				'nachricht': nachricht,	
				'inserat' : inserat,
				'email' : kunde.user.email,
				'telefon' : kunde.phone,		
				 })

			email = ''
			
			#send email for order
			email = EmailMessage(
				subject,
				template,
				email,
				[inserat.user.email],
			)

			email.fail_silently=False
			email.content_subtype = "html"
			email.send()
			messages.error(request, "Die Nachricht wurde erfolgreich gesendet")
			return redirect('store:marktplatz_inserat_details', slug=inserat.slug)

		else:
			context = {

			'inserat' : inserat,

			}
			return render (request, 'marktplatz/marktplatz-inserat-details.html', context)

	else:
		context = {

			'inserat' : inserat,

			}
		return render (request, 'marktplatz/marktplatz-inserat-details.html', context)


def marktplatz_condition(request, cond):

	if cond == "Gebraucht":
		mp_inserate = Marketplace.objects.filter(condition="G")

	elif cond == "Neu":
		mp_inserate = Marketplace.objects.filter(condition="N")

	else: 
		mp_inserate = Marketplace.objects.all()

	mp_categories = MP_Category.objects.all()

	context = {

	'mp_categories' : mp_categories,
	'mp_inserate': mp_inserate,

	}
	return render (request, 'marktplatz/marktplatz-main.html', context)


# Marktplatz CMS

@staff_member_required
def cms_inserat_freigeben(request, pk, portal):
	
	if portal == "Jobs":
		mp = get_object_or_404(JobsMarketplace, pk=pk)
		mp.is_active = True 
		mp.save()
		'''messages.info(request, "Das Inserat wurde freigegeben.")
		subject = 'Inserat Nr.' + ' ' + str(mp.id) + ' ' + mp.title + ' wurde freigegeben.'
		if mp.condition == "G":
			condition = "Gebraucht"
		else:
			condition = "Neu"
		template = render_to_string('marktplatz/inserat-email.html', {
			'title' : mp.title,
			'price': mp.price, 
			'condition': condition,
			'place': mp.place,
			'add_date': mp.add_date,
			'category': mp.category,		
					 })
		email = ''	
		#send email for order
		email = EmailMessage(
			subject,
			template,
			email,
			[mp.user.email],
				)

		email.fail_silently=False
		email.content_subtype = "html"
		email.send()'''
		return redirect("store:cms_marktplatz")
	else:
		mp = get_object_or_404(Marketplace, pk=pk)
		mp.is_active = True 
		mp.save()
		messages.info(request, "Das Inserat wurde freigegeben.")
		subject = 'Inserat Nr.' + ' ' + str(mp.id) + ' ' + mp.title + ' wurde freigegeben.'
		if mp.condition == "G":
			condition = "Gebraucht"
		else:
			condition = "Neu"
		template = render_to_string('marktplatz/inserat-email.html', {
			'title' : mp.title,
			'price': mp.price, 
			'condition': condition,
			'place': mp.place,
			'add_date': mp.add_date,
			'category': mp.category,		
					 })
		email = ''	
		#send email for order
		email = EmailMessage(
			subject,
			template,
			email,
			[mp.user.email],
				)

		email.fail_silently=False
		email.content_subtype = "html"
		email.send()
		return redirect("store:cms_marktplatz")

@staff_member_required
def cms_inserat_deaktivieren(request, pk, portal):

	if portal == "Jobs":
		mp = get_object_or_404(JobsMarketplace, pk=pk)
	else:
		mp = get_object_or_404(Marketplace, pk=pk)
	mp.is_active = False 
	mp.save()
	messages.info(request, "Das Inserat wurde deaktiviert.")
	return redirect("store:cms_marktplatz")

@staff_member_required
def cms_marktplatz(request):
	query1 = Marketplace.objects.all()
	query2 = JobsMarketplace.objects.all()
	inserate = list(chain(query1, query2))
	

	context = {
		'produkte': inserate,
	 }
	return render(request, 'marktplatz/cms-marktplatz.html', context)


@staff_member_required
def cms_mp_bearbeiten(request, pk):
	mp = get_object_or_404(Marketplace, pk=pk)
	if request.method == "POST":
		form = InseratCreateForm(request.POST or None,request.FILES or None, instance=mp)
		if form.is_valid():
			form.save()
			return redirect('store:cms_marktplatz')

		else:
			messages.error(request, "Error")
			
	else:
		form = InseratCreateForm(request.POST or None, request.FILES or None, instance=mp)
		context = {
			'form': form,
			'mp': mp,
			 }
		return render(request, 'marktplatz/cms-marktplatz-edit.html', context)

@staff_member_required
def cms_mp_löschen(request, pk):
	eintrag = get_object_or_404(Marketplace, pk=pk)
	eintrag.delete()
	messages.info(request, "Das Inserat wurde gelöscht.")
	return redirect("store:cms_marktplatz")

# Marktplatz CMS END

def marktplatz_main_category(request, cat):

	mp_inserate = Marketplace.objects.filter(category__name=cat)

	mp_categories = MP_Category.objects.all()

	context = {

	'mp_inserate': mp_inserate,
	'mp_categories': mp_categories,

	}
	return render (request, 'marktplatz/marktplatz-main.html', context)

def marktplatz_main_jobs_category(request, cat):

	mp_inserate = JobsMarketplace.objects.filter(category__name=cat)

	mp_categories = MP_JobsCategory.objects.all().order_by('name')

	context = {

	'mp_inserate': mp_inserate,
	'mp_categories': mp_categories,

	}
	return render (request, 'marktplatz/marktplatz-jobs.html', context)



def error_404(request, exception):
        data = {}
        return render(request,'404.html', data)

#Hauptseite
def home(request):
	search_query = request.GET.get('search', '')
	if search_query:
		items = Item.objects.filter(titel__icontains=search_query)
	else:
		items = Item.objects.all()
		if request.method =="POST":
			vorname = request.POST['message-vorname']
			nachname = request.POST['message-name']
			firma = request.POST['message-firma']
			email = request.POST['message-email']
			nachricht = request.POST['message']
			telefon = request.POST['message-phone']
			anrede = request.POST['message-anrede']

			subject = 'Nachricht von ' + ' '+ firma + ' ' + vorname + ' ' + nachname
			template = render_to_string('shop/kontakt-email.html', {
				'anrede' : anrede,
				'vorname': vorname, 
				'nachname': nachname,
				'firma': firma,
				'email': email,
				'telefon': telefon,
				'nachricht': nachricht,			
				 })
			
			#send email for order
			email = EmailMessage(
				subject,
				template,
				email,
				['bestellungen@gastrodichtung.ch', 'livio.bonetta@geboshop.ch'],
			)

			email.fail_silently=False
			email.content_subtype = "html"
			email.send()

			context = {
				'items': items,
				'vorname' : vorname,
			}
			return render(request, 'dichtungen.html', context)
		else:
			context = {
				'items': items
			}
			return render(request, 'dichtungen.html', context)

	return render(request, 'dichtungen.html', context)

def searchbar(request):
	search_query = request.GET.get('search', '')
	if search_query:
		items = Item.objects.filter(Q(titel__icontains=search_query) | Q(artikelnr__icontains=search_query) | Q(kategorie__name__icontains=search_query) | Q(subkategorie__sub_name__icontains=search_query))
	else:
		items = Item.objects.all()


	context = {'items': items}
	return render(request, 'shop/searchbar.html', context)


def impressum(request):
	context = {}
	return render(request, 'impressum.html', context)


#Kontaktseite
def kontakt(request):

	if request.method =="POST":
		vorname = request.POST['message-surname']
		nachname = request.POST['message-name']
		firma = request.POST['message-company']
		email = request.POST['message-email']
		nachricht = request.POST['message']
		telefon = request.POST['message-phone']
		anrede = request.POST['message-anrede']

		subject = 'Nachricht von ' + ' '+ firma + ' ' + vorname + ' ' + nachname
		template = render_to_string('shop/kontakt-email.html', {
			'anrede' : anrede,
			'vorname': vorname, 
			'nachname': nachname,
			'firma': firma,
			'email': email,
			'telefon': telefon,
			'nachricht': nachricht,			
			 })
		
		#send email for order
		email = EmailMessage(
			subject,
			template,
			email,
			['bestellungen@gastrodichtung.ch', 'livio.bonetta@geboshop.ch'],
		)

		email.fail_silently=False
		email.content_subtype = "html"
		email.send()

		context = {
			'message_kontakt' : 'Die Nachricht wurde erfolgreich gesendet.'
			 }
		return render(request, 'kontakt.html', context)
	
	else:
		context = { }
		return render(request, 'kontakt.html', context)

#Kontaktseite
def firma(request):
	context = { }
	return render(request, 'firma.html', context)


#Marke Übersicht
def marke(request):
	marken = Marke.objects.all()
	context = { 
		'marken' : marken, 
		}
	return render(request, 'shop/store-marke.html', context)


#Marke Store
def HomeMarkeView(request, cat_marke):
	seo_marke = get_object_or_404(Marke, slug=cat_marke)
	marke_products = Item.objects.filter(item_marken__slug=cat_marke)
	context = { 
		'marke_products' : marke_products, 
		'cat_marke': cat_marke.replace('-', ''),
		'seo_marke' : seo_marke,
		}
	return render(request, 'shop/store-marke-details.html', context)

#Produktübersichten
def HomeProduktView(request, cats):
	category_products = Item.objects.filter(kategorie__slug=cats)
	seo_cat = get_object_or_404(Category, slug=cats)
	context = { 
		'category_products' : category_products, 
		'cats': cats.replace('-', ''),
		'seo_cat' : seo_cat,
		}
	return render(request, 'shop/store.html', context)


#Produktübersichten
def HomeSubProduktView(request, subcats, cats):
	category_products = Item.objects.filter(kategorie__slug=cats)
	subcategory_products = Item.objects.filter(subkategorie__sub_slug=subcats)
	seo_subcat = get_object_or_404(Subcategory, sub_slug=subcats)
	context = { 
		'category_products' : category_products, 
		'cats': cats.replace('-', ''),
		'subcategory_products' : subcategory_products, 
		'subcats': subcats.replace('-', ''),
		'seo_subcat' : seo_subcat,
		}
	return render(request, 'shop/store-subcat.html', context)


#Produktbeschreibungen
def product_detail(request, slug):
	item = get_object_or_404(Item, slug=slug)
	if request.user.is_authenticated:
		orderitem, created = OrderItem.objects.get_or_create(
					item=item,
					user=request.user,
					ordered=False,
					aussenbreite=250, 
					aussenhöhe=250,
				)
		form = AussenmassForm(request.POST or None)
			
		context = { 
				'item': item,
				'orderitem': orderitem,
				'form': form,
			}
		return render(request, 'shop/descriptions.html', context)
	else:
		orderitem = ' '
		form = AussenmassForm(request.POST or None)
			
		context = { 
				'item': item,
				'orderitem': orderitem,
				'form': form,
			}
		return render(request, 'shop/descriptions.html', context)


#Produktbeschreibungen
def weitere_product_detail(request, slug):
	item = get_object_or_404(Item, slug=slug)
	if request.user.is_authenticated:
		orderitem, created = OrderItem.objects.get_or_create(
					item=item,
					user=request.user,
					ordered=False,
					aussenbreite=250, 
					aussenhöhe=250,
				)
		form = AussenmassForm(request.POST or None)
			
		context = { 
				'item': item,
				'orderitem': orderitem,
				'form': form,
			}
		return render(request, 'shop/descriptions_sub.html', context)
	else:
		orderitem = ' '
		form = AussenmassForm(request.POST or None)
			
		context = { 
				'item': item,
				'orderitem': orderitem,
				'form': form,
			}
		return render(request, 'shop/descriptions_sub.html', context)

@login_required
def add_to_cart(request, slug, pk):
	
	#check if it's post or not
	if request.method == "POST":
		aussenbreite = request.POST['aussenbreite']
		aussenhöhe = request.POST['aussenhöhe']
		anzahl = int(request.POST['anzahl'])
		
		#get the right product
		item = get_object_or_404(Item, slug=slug)
		
		#check if the order exists
		order_qs = Order.objects.filter(user=request.user, ordered=False)
		if order_qs.exists():
			order = order_qs[0]

			#check if there is existing order item
			order_item, created = OrderItem.objects.get_or_create(
				item=item,
				user=request.user,
				ordered=False,
				aussenbreite=aussenbreite,
				aussenhöhe=aussenhöhe,
				)

			#check if the order item is in the order

			#if the order item exist adjust quantity
			if order.items.filter(item__slug=item.slug, aussenbreite=aussenbreite, aussenhöhe=aussenhöhe).exists():
				order_item.quantity += anzahl
				order_item.save()
				messages.info(request, "Die Menge wurde aktualisiert.")
				return redirect("store:order_summary")
			
			#if the order item not exist add it into order
			else:
				#these below steps are working, dont change
				order_item.aussenbreite = aussenbreite
				order_item.aussenhöhe = aussenhöhe
				order_item.quantity = anzahl
				order_item.save()
				order.items.add(order_item)
				messages.info(request, "Das Produkt wurde erfolgreich in den Warenkorb gelegt.")
				return redirect("store:order_summary")

		
		#the order not existing for magnetdichtung and pvcohne
		else:
			ordered_date = timezone.now()
			order = Order.objects.create(user=request.user, ordered_date=ordered_date)
			if request.method == "POST":
				aussenbreite = request.POST['aussenbreite']
				aussenhöhe = request.POST['aussenhöhe']
				anzahl = request.POST['anzahl']
				#these below steps are working, dont change
				order_item, created = OrderItem.objects.get_or_create(
					item=item,
					user=request.user,
					ordered=False,
					aussenbreite=aussenbreite,
					aussenhöhe=aussenhöhe,
					quantity=anzahl,
						)
				order.items.add(order_item)
				messages.info(request, "Das Produkt wurde erfolgreich in den Warenkorb gelegt.")
				return redirect("store:order_summary")
			
			#the order not existing for gummidichtungen
			else:
				aussenbreite = 250
				aussenhöhe = 250
				ordered_date = timezone.now()
				order = Order.objects.create(user=request.user, ordered_date=ordered_date)
				#these below steps are working, dont change
				order_item, created = OrderItem.objects.get_or_create(
					item=item,
					user=request.user,
					ordered=False,
					aussenbreite=aussenbreite,
					aussenhöhe=aussenhöhe,
						)
				order.items.add(order_item)
				messages.info(request, "Das Produkt wurde erfolgreich in den Warenkorb gelegt.")
				return redirect("store:order_summary")

	
	#if it's not request.method == "POST"
	else:
		#get the right product
		item = get_object_or_404(Item, slug=slug)
		
		#check if the order exists
		order_qs = Order.objects.filter(user=request.user, ordered=False)
		if order_qs.exists():
			order = order_qs[0]

			#check if there is existing order item
			order_item, created = OrderItem.objects.get_or_create(
				item=item,
				user=request.user,
				ordered=False,
				pk=pk,
				)

			#check if the order item is in the order

			#if the order item exist adjust quantity
			if order.items.filter(item__slug=item.slug, pk=pk).exists():
				order_item.quantity +=1
				order_item.save()
				messages.info(request, "Die Menge wurde aktualisiert.")
				return redirect("store:order_summary")
			else:
				pass
				#this case not existing
		else:
			pass
			#this case not existing

#Kundendichtungen
@login_required
def mydichtungen(request):
	allelements = Elemente.objects.filter(kunde=request.user.profile)
	kunde = Kunde.objects.get(user=request.user)
	if request.method == "POST":
		mydslug = request.POST['mydslug']
		aussenbreite = request.POST['aussenbreite']
		aussenhöhe = request.POST['aussenhöhe']
		anzahl = request.POST['anzahl']
		element = request.POST['elementnr']
		item = get_object_or_404(Item, slug=mydslug)
		orderitem, created = OrderItem.objects.get_or_create(
				item=item,
				user=request.user,
				ordered=False,
				aussenbreite=aussenbreite, 
				aussenhöhe=aussenhöhe,
				element=element,
			)
		return redirect("store:add_to_cart_myd", slug=mydslug, pk=item.pk, aussenbreite=aussenbreite, aussenhöhe=aussenhöhe, anzahl=anzahl, element=element)
	else:
		orderitem = ' '
		context = { 
			'allelements': allelements,
			'orderitem': orderitem,
			'kunde': kunde,
			}
	return render(request, 'shop/mydichtungen.html', context)

#add to cart for mydichtungen
@login_required
def add_to_cart_myd(request, slug, pk, aussenbreite, aussenhöhe, anzahl, element):
	#get the right product
	item = get_object_or_404(Item, slug=slug)
		
	#check if the order exists
	order_qs = Order.objects.filter(user=request.user, ordered=False)
	if order_qs.exists():
		order = order_qs[0]

		#check if there is existing order item
		order_item, created = OrderItem.objects.get_or_create(
				item=item,
				user=request.user,
				ordered=False,
				aussenbreite=aussenbreite,
				aussenhöhe=aussenhöhe,
				element=element,
				)

			#check if the order item is in the order

		#if the order item exist adjust quantity
		if order.items.filter(item__slug=item.slug, aussenbreite=aussenbreite, aussenhöhe=aussenhöhe, element=element).exists():
			order_item.quantity += anzahl
			order_item.save()
			messages.info(request, "Die Menge wurde aktualisiert.")
			return redirect("store:order_summary")
			
		#if the order item not exist add it into order
		else:
			#these below steps are working, dont change
			order_item.aussenbreite = aussenbreite
			order_item.aussenhöhe = aussenhöhe
			order_item.quantity = anzahl
			order_item.element = element
			order_item.save()
			order.items.add(order_item)
			messages.info(request, "Das Produkt wurde erfolgreich in den Warenkorb gelegt.")
			return redirect("store:order_summary")

		
	#the order not existing for magnetdichtung and pvcohne
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(user=request.user, ordered_date=ordered_date)
			
		#these below steps are working, dont change
		order_item, created = OrderItem.objects.get_or_create(
					item=item,
					user=request.user,
					ordered=False,
					aussenbreite=aussenbreite,
					aussenhöhe=aussenhöhe,
					element=element,
						)
		order.items.add(order_item)
		messages.info(request, "Das Produkt wurde erfolgreich in den Warenkorb gelegt.")
		return redirect("store:order_summary")
		
@login_required
def remove_from_cart(request, slug, pk):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user, 
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		#check if the order item is in the order
		if order.items.filter(item__slug=item.slug, pk=pk).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False,
				pk=pk,
			)[0]
			order.items.remove(order_item)
			order_item.delete()
			messages.info(request, "Das Produkt wurde aus dem Warenkorb gelöscht.")
			return redirect("store:order_summary")	
		else:
			messages.info(request, "Es hat kein Produkt im Warenkorb.")
			return redirect("store:product-detail", slug=slug)	
	else:
		messages.info(request, "Es gibt keine aktuelle Bestellung.")
		return redirect("store:product-detail", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug, pk):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user=request.user, 
		ordered=False
	)
	if order_qs.exists():
		order = order_qs[0]
		#check if the order item is in the order
		if order.items.filter(item__slug=item.slug, pk=pk).exists():
			order_item = OrderItem.objects.filter(
				item=item,
				user=request.user,
				ordered=False,
				pk=pk,
			)[0]
			if order_item.quantity >1 :
				order_item.quantity -=1
				order_item.save()
			else: 
				order.items.remove(order_item)
				order_item.delete()
			messages.info(request, "Die Menge wurde angepasst.")
			return redirect("store:order_summary")	
		else:
			messages.info(request, "Es hat kein Produkt im Warenkorb.")
			return redirect("store:product-detail", slug=slug)	
	else:
		messages.info(request, "Es gibt keine aktuelle Bestellung.")
		return redirect("store:product-detail", slug=slug)

#Warenkorb
class OrderSummaryView(LoginRequiredMixin, View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			total = order.get_total()

			shipping1 = ShippingCost.objects.all().filter(price_from__lte=total, price_to__gt=total)

			if order.items.filter(item__subkategorie__sub_name="Duschdichtungen"):
				order.shippingcost = shipping1[0].shipping_price + 18
				zuschlag = 18
				order.save()
				context = {
				'object': order,
				'zuschlag': zuschlag,
				}
			else:

				order.shippingcost = shipping1[0].shipping_price
				order.save()
				context = {
					'object': order,
				
					}
			
			return render(self.request, 'shop/order_summary.html', context)
		except ObjectDoesNotExist:
			messages.info(self.request,"Es gibt keine Bestellung.")
			return redirect("store:home")


#Bestellung abschliessen
class FinalSummaryView(View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			order_items = order.items.all()
			context = {
				'order_items' : order_items,
				'object' : order,
			}
			return render(self.request, 'shop/final_summary.html', context)
		except ObjectDoesNotExist:
			messages.info(self.request,"Es gibt keine Bestellung.")
			return redirect("store:home")	

	def post(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			order_items = order.items.all()
		
			order_items.update(ordered=True)
			for item in order_items:
				item.save()

			order.discount = order.get_rabatt()
			order.discount_pct = order.user.profile.rabatt
			order.skonto = order.get_skonto()
			order.pre_total = order.get_total_pre_mwst()
			order.order_mwst = order.mwst()
			order.total = order.grandtotal()

			order.ordered = True
			order.payment = True
			order.save()

			subject = 'Auftragsbestätigung Bestellung 206505'+str(order.id) +' von Gastrodichtungen.ch'
			template = render_to_string('shop/bestellbestaetigung.html', {
					'vorname': self.request.user.first_name, 
					'nachname': self.request.user.last_name,
					'datum' : str(order.ordered_date.strftime('%d' + '.' + ' %b' + ' %Y')),
					'order_items' : order_items, 
					'mwst' : order.mwst(),
					'total': order.grandtotal(),
					'object' : order,
					 })
						
			#send email for order
			email = EmailMessage(
					subject,
					template,
					settings.EMAIL_HOST_USER,
					[self.request.user.email, 'livio.bonetta@geboshop.ch'],
							)

			email.fail_silently=False
			email.content_subtype = "html"
			email.send()

			#redirect to success page
			return redirect('store:rechnung')

		except ObjectDoesNotExist:
			messages.error(request, "Es gibt keine Bestellung.")
			return redirect("store:home")



#Adresse und Lieferung
class CheckoutView(View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			form = CheckoutForm()
			
			context = {
							'form': form,
							'order': order,
						}

			billing_address_qs = Address.objects.filter(
				user=self.request.user,
				address_type='B',
			)
			if billing_address_qs.exists():
				context.update({'billing_address': billing_address_qs[0]})
			
			shipping_address_qs = ShippingAddress.objects.filter(
				user=self.request.user,
				address_type='S',
			)
			if shipping_address_qs.exists():
				context.update({'shipping_address': shipping_address_qs[0]})
			
			return render(self.request, 'shop/checkout.html', context)
		except ObjectDoesNotExist:
			messages.info(self.request, "Es gibt keine bestehende Bestellung.")
			return redirect("store:home")

	def post(self, *args, **kwargs):
		form = CheckoutForm(self.request.POST or None)
		try:
			user=self.request.user
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():
				use_other_billing = form.cleaned_data.get(
					'use_other_billing')
				different_shipping_address = form.cleaned_data.get(
							'different_shipping_address')

				if use_other_billing:
					rechnung_strasse = form.cleaned_data.get('rechnung_strasse')
					rechnung_nr = form.cleaned_data.get('rechnung_nr')
					rechnung_ort = form.cleaned_data.get('rechnung_ort')
					rechnung_land = form.cleaned_data.get('rechnung_land')
					rechnung_plz = form.cleaned_data.get('rechnung_plz')
					rechnung_firmenname = form.cleaned_data.get('rechnung_firmenname')
					rechnung_vorname = form.cleaned_data.get('rechnung_vorname')
					rechnung_nachname = form.cleaned_data.get('rechnung_nachname')

					billing_address = Address.objects.create(
						user=self.request.user,
						address_type='B',
					)

					billing_address.rechnung_strasse = rechnung_strasse
					billing_address.rechnung_nr = rechnung_nr
					billing_address.rechnung_ort = rechnung_ort
					billing_address.rechnung_land = rechnung_land
					billing_address.rechnung_plz = rechnung_plz
					billing_address.address_type = 'B'
					billing_address.save()
					user.profile.firmenname = rechnung_firmenname
					user.first_name = rechnung_vorname
					user.last_name = rechnung_nachname
					user.save()
					user.profile.save()
					order.billing_address = billing_address
					order.save()

					if different_shipping_address:
							
							lieferung_strasse = form.cleaned_data.get('lieferung_strasse')
							lieferung_nr = form.cleaned_data.get('lieferung_nr')
							lieferung_ort = form.cleaned_data.get('lieferung_ort')
							lieferung_plz = form.cleaned_data.get('lieferung_plz')
							lieferung_land = form.cleaned_data.get('lieferung_land')
							lieferung_firmenname = form.cleaned_data.get('firmenname')
							lieferung_vorname = form.cleaned_data.get('vorname')
							lieferung_nachname = form.cleaned_data.get('nachname')

							shipping_address = ShippingAddress.objects.create(
									user=self.request.user,
									address_type='S',

								)

							shipping_address.lieferung_strasse = lieferung_strasse
							shipping_address.lieferung_nr = lieferung_nr
							shipping_address.lieferung_ort = lieferung_ort								
							shipping_address.lieferung_plz = lieferung_plz
							shipping_address.lieferung_land = lieferung_land
							shipping_address.firmenname = lieferung_firmenname
							shipping_address.vorname = lieferung_vorname
							shipping_address.nachname = lieferung_nachname
							shipping_address.address_type = 'S'
							shipping_address.save()
							order.shipping_address = shipping_address
							order.save()
							return redirect('store:payment')

					else:
						order.shipping_address = None
						order.save()
						return redirect('store:payment')

				else:
					address_qs = Address.objects.filter(
						user=self.request.user,
						address_type='B',
						)

					if address_qs.exists():
						billing_address = address_qs[0]
						order.billing_address = billing_address
						order.save()

						if different_shipping_address:
							lieferung_strasse = form.cleaned_data.get('lieferung_strasse')
							lieferung_nr = form.cleaned_data.get('lieferung_nr')
							lieferung_ort = form.cleaned_data.get('lieferung_ort')
							lieferung_plz = form.cleaned_data.get('lieferung_plz')
							lieferung_land = form.cleaned_data.get('lieferung_land')
							lieferung_firmenname = form.cleaned_data.get('firmenname')
							lieferung_vorname = form.cleaned_data.get('vorname')
							lieferung_nachname = form.cleaned_data.get('nachname')
							
							shipping_address = ShippingAddress.objects.create(
									user=self.request.user,
									address_type='S',

								)

							shipping_address.lieferung_strasse = lieferung_strasse
							shipping_address.lieferung_nr = lieferung_nr
							shipping_address.lieferung_ort = lieferung_ort								
							shipping_address.lieferung_plz = lieferung_plz
							shipping_address.lieferung_land = lieferung_land
							shipping_address.firmenname = lieferung_firmenname
							shipping_address.vorname = lieferung_vorname
							shipping_address.nachname = lieferung_nachname
							shipping_address.address_type = 'S'
							shipping_address.save()
							order.shipping_address = shipping_address
							order.save()
							return redirect('store:payment')

						else:
							order.shipping_address = None
							order.save()
							return redirect('store:payment')

					else: 
						return redirect('store:payment')				
			else: 
				pass
						
		except ObjectDoesNotExist:
			messages.error(request, "Es gibt keine Bestellung.")
			return redirect("store:home")


#Adresse und Lieferung
class PaymentView(View):
	def get(self, *args, **kwargs):
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			payment_form = PaymentForm()
			context = {
				'payment_form' : payment_form,
				'order': order,
			}
			return render(self.request, 'shop/zahlung.html', context)
		except ObjectDoesNotExist:
			messages.info(self.request, "Es gibt keine bestehende Bestellung.")
			return redirect("store:home")

	def post(self, *args, **kwargs):
		form = PaymentForm(self.request.POST or None)
		try:
			order = Order.objects.get(user=self.request.user, ordered=False)
			if form.is_valid():
				payment_option = form.cleaned_data.get('payment_option')
				order.payment_method = payment_option
				order.save()
				#success page redirect
				return redirect('store:final_summary')
			else:
				pass
								
		except ObjectDoesNotExist:
			messages.error(request, "Es gibt keine Bestellung.")
			return redirect("store:home")

#Success Page
@login_required
def Rechnung(request):
	context = {	}
	return render(request, 'shop/rechnung.html', context)

#Success Page2
@login_required
def email(request, pk):
	order = Order.objects.get(pk=pk)
	order_items = order.items.all()
	context = {
		'order_items' : order_items,
		'object' : order,
		}
	return render(request, 'shop/bestellung_uebersicht.html', context)

@login_required
def bestellungen(request):
	order = Order.objects.filter(user=request.user).order_by('-ordered_date')
	
	context = {
		'object' : order,
		}
	return render(request, 'shop/bestellungen.html', context)


@login_required
def einstellungen(request):
	address = Address.objects.get(user=request.user)
	user = request.user
	if request.method == "POST":
		firmenname = request.POST['firmenname']
		vorname = request.POST['vorname']
		nachname = request.POST['nachname']
		birthday = request.POST['birthday']
		phone = request.POST['phone']
		mobile = request.POST['mobile']
		user.profile.birthday = birthday
		user.profile.mobile = mobile
		user.profile.phone = phone
		user.profile.firmenname = firmenname
		user.profile.save()
		user.first_name = vorname
		user.last_name = nachname
		user.save()
		form = AddressForm(request.POST or None, instance=address)
		if form.is_valid():
			form.save()
			return redirect('store:einstellungen')

		else:
			messages.error(request, "Error")

	else: 
		form = AddressForm(request.POST or None, instance=address)

	context = {
		'form': form,
		'address' : address,
				}
	return render(request, 'shop/einstellungen.html', context)	

@login_required
def lieferadresse(request):
	address = ShippingAddress.objects.get(user=request.user)
	if request.method == "POST":
		form = ShippingAddressForm(request.POST or None, instance=address)
		if form.is_valid():
			form.save()
			return redirect('store:einstellungen')

		else:
			messages.error(request, "Error")

	else: 
		form = ShippingAddressForm(request.POST or None, instance=address)

	context = {
		'form': form,
		'address' : address,
				}
	return render(request, 'shop/lieferadresse.html', context)

@login_required
def create_lieferadresse(request):
	if request.method == "POST":
		form = ShippingAddressForm(request.POST or None)
		if form.is_valid():
			adresse = form.save(commit=False)
			adresse.user = request.user
			adresse.address_type = 'S'
			adresse.save()
			return redirect('store:einstellungen')

		else:
			messages.error(request, "Error")

	else: 
		form = ShippingAddressForm()

	context = {
		'form': form,
				}
	return render(request, 'shop/lieferadresse-erfassen.html', context)




#CMS related fields --- only for staff available
@staff_member_required
def cms(request):

	cat = Category.objects.first()

	context = {
	'cat' : cat
	 }
	return render(request, 'cms.html', context)


@staff_member_required
def cms_bestellungen(request):
	order = Order.objects.filter(ordered=True).order_by('-ordered_date')
	context = {
			'order': order,
			 }
	return render(request, 'cms-bestellungen.html', context)

#Success Page2
@staff_member_required
def cms_bestellung_confirmation(request, pk):
	order = Order.objects.get(pk=pk)
	order_items = order.items.all()
	context = {
		'order_items' : order_items,
		'object' : order,
		}
	return render(request, 'cms-bestellung-confirmation.html', context)




@staff_member_required
def cms_kennzahlen_webseite(request):
	import json
	import requests
	import ast
	
	api_request_today = requests.get("http://api.clicky.com/api/stats/4?site_id=32020&type=visitors,bounce-rate,time-average&date=today&output=json")
	api_request_7day = requests.get("http://api.clicky.com/api/stats/4?site_id=32020&type=visitors,bounce-rate,time-average&date=last-7-days&output=json")
	api_request_month = requests.get("http://api.clicky.com/api/stats/4?site_id=32020&type=visitors,bounce-rate,time-average&date=this-month&output=json")
	api_request_lastmonth = requests.get("http://api.clicky.com/api/stats/4?site_id=32020&type=visitors,bounce-rate,time-average&date=last-month&output=json")
	api_request_lastweek = requests.get("http://api.clicky.com/api/stats/4?site_id=32020&type=visitors,bounce-rate,time-average&date=last-week&output=json")
	api_request_links_domains = requests.get("http://api.clicky.com/api/stats/4?site_id=32020&type=links-domains&date=last-14-days&output=json")

	try:
		api_today = json.loads(api_request_today.content)
		api_7day = json.loads(api_request_7day.content)
		api_month = json.loads(api_request_month.content)
		api_lastmonth = json.loads(api_request_lastmonth.content)
		api_lastweek = json.loads(api_request_lastweek.content)
		api_links_domains = json.loads(api_request_links_domains.content)

	except Exception as e:
		api = "Error..."

	r = requests.get("http://api.clicky.com/api/stats/4?site_id=32020&type=visitors&date=this-month&output=json")
	month_json = r.json()
	month_string = json.dumps(month_json[0]['dates'][0]['date'], indent=2)
	month_string = month_string[-11:]
	month_string = month_string[:-1]
	#month_string = datetime.strptime(month_string, '%Y/%m/%d')
	month_int = ast.literal_eval(json.dumps(month_json[0]['dates'][0]['items'][0]['value']))


	'''
	if Visitor.objects.filter(visitor_month=month_string).exists():
		t = Visitor.objects.get(visitor_month=month_string)
		t.visitor_number = month_int
		t.save()

	else:
		t = Visitor(visitor_month=month_string, visitor_number=month_int)
		t.save()
		'''

	x = datetime.now()
	today = x.strftime('%d' + '.' + ' %b' + ' %Y')
	context = {
		'month_int':month_int,
		'month_string': month_string, 
		'api_today': api_today, 
		'api_7day': api_7day, 
		'api_month': api_month, 
		'api_lastmonth': api_lastmonth, 
		'api_lastweek': api_lastweek, 
		'api_links_domains': api_links_domains, 
		'time': today }
	return render(request, 'cms-kennzahlen-webseite.html', context)

@staff_member_required
def cms_marken(request):
	marken = Marke.objects.all().order_by('-id')			

	context = {
			'marken': marken,		
			 }
	return render(request, 'cms-marken.html', context)

@staff_member_required
def cms_marke_erfassen(request):
	if request.method == "POST":
		form = MarkeChangeForm(request.POST or None, request.FILES or None)
		if form.is_valid():
			form.save()
			return redirect('store:cms_marken')

		else:
			messages.error(request, "Error")

	else: 
		form = MarkeChangeForm()

	context = {
		'form': form,
				}
	return render(request, 'cms-marke-erfassen.html', context)


@staff_member_required
def cms_marke_bearbeiten(request, pk):
	marke = get_object_or_404(Marke, pk=pk)
	if request.method == "POST":
		form = MarkeChangeForm(request.POST or None, instance=marke)
		if form.is_valid():
			form.save()
			return redirect('store:cms_marken')

		else:
			messages.error(request, "Error")
			
	else:
		form = MarkeChangeForm(request.POST or None, request.FILES or None, instance=marke)
		context = {
			'form': form,
			'marke': marke,
			 }
		return render(request, 'cms-marke-bearbeiten.html', context)

@staff_member_required
def cms_marke_löschen(request, pk):
	eintrag = get_object_or_404(Marke, pk=pk)
	eintrag.delete()
	messages.info(request, "Die Marke wurde gelöscht.")
	return redirect("store:cms_marken")	

@staff_member_required
def cms_product_marke_overview(request, pk):
	product = get_object_or_404(Item, id=pk)

	product_marke = product.item_marken.all

	context = {
			'product': product,
			'product_marke' : product_marke,		
			 }
	return render(request, 'cms-produkt-marken.html', context)

@staff_member_required
def cms_product_marke_erfassen(request, pk):

	product = get_object_or_404(Item, id=pk)

	if request.method == 'POST':
		form = ProductMarkeLinkForm(request.POST or None)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			item_marke = cleaned_data['item_marke']
			marke = get_object_or_404(Marke, name=item_marke)
			marke.item.add(product)
			marke.save()
			return redirect('store:cms_product_marke_overview', pk=product.id)
	else:
    		form = ProductMarkeLinkForm()

	context = {

		'product' : product,
		'form': form,
				}

	return render(request, 'cms-produkt-marke-erfassen.html', context)


@staff_member_required
def cms_product_marke_löschen(request, pkk, pk):
	product = get_object_or_404(Item, id=pkk)
	item_marke = get_object_or_404(Marke, id=pk)
	marke = get_object_or_404(Marke, name=item_marke)
	marke.item.remove(product)
	marke.save()
			
	return redirect('store:cms_product_marke_overview', pk=product.id)
	

	context = {

		'product' : product,
		'form': form,
				}

	return render(request, 'cms-produkt-marke-erfassen.html', context)




@staff_member_required
def cms_kunden(request):
	user = User.objects.all().order_by('-id')
	search_query = request.GET.get('search', '')


	if search_query:
		user = User.objects.filter(Q(profile__firmenname__icontains=search_query) | Q(profile__interne_nummer__icontains=search_query))

	else:
		user = User.objects.all().order_by('-id')
			

	context = {
			'user': user,		
			 }
	return render(request, 'cms-kunden.html', context)



@staff_member_required
def cms_kunden_erfassen(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST or None)
        if form.is_valid():
            # Extract only the fields needed for creating a user
            user_data = {
                'username': form.cleaned_data['username'],
                'password': form.cleaned_data['password1'],  # Assuming the form uses password1 and password2
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
            }
            new_user = User.objects.create_user(**user_data)
            new_kunde = Kunde.objects.create(user=new_user, phone=request.POST['phone'], firmenname=request.POST['firmenname'], rabatt=0)
            new_address = Address.objects.create(

            	user=new_user, 
            	rechnung_strasse=request.POST['strasse'],
            	rechnung_nr=request.POST['nr'],
            	rechnung_ort=request.POST['ort'],
            	rechnung_land=request.POST['land'],
            	rechnung_plz=request.POST['plz'],
            	address_type='B'

            	)
            
            return redirect('store:cms_kunden')

        else:
            messages.error(request, "Error")

    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'cms-kunden-erfassen.html', context)

@staff_member_required
def cms_user_bearbeiten(request, pk):
	kunde = get_object_or_404(User, pk=pk)
	if request.method == "POST":
		form = KundeEditForm(request.POST or None, request.FILES or None, instance=kunde)
		if form.is_valid():
			form.save()
			return redirect('store:cms_kunden')

		else:
			messages.error(request, "Error")
			
	else:
		form = KundeEditForm(request.POST or None, instance=kunde)
		context = {
			'form': form,
			'kunde': kunde,
			 }
		return render(request, 'cms-user-bearbeiten.html', context)


@staff_member_required
def cms_kunde_bearbeiten(request, pk):
	kunde = get_object_or_404(Kunde, pk=pk)
	if request.method == "POST":
		form = KundeEditAdvancedForm(request.POST or None, instance=kunde)
		if form.is_valid():
			form.save()
			return redirect('store:cms_kunden')

		else:
			messages.error(request, "Error")
			
	else:
		form = KundeEditAdvancedForm(request.POST or None, request.FILES or None, instance=kunde)
		context = {
			'form': form,
			'kunde': kunde,
			 }
		return render(request, 'cms-kunden-bearbeiten.html', context)

@staff_member_required
def cms_kundenadresse_bearbeiten(request, pk):
	kunde = get_object_or_404(User, pk=pk)
	address = Address.objects.get(user=kunde)
	if request.method == "POST":
		form = AddressForm(request.POST or None, instance=address)
		if form.is_valid():
			form.save()
			return redirect('store:cms_kunden')

		else:
			messages.error(request, "Error")
			
	else:
		form = AddressForm(request.POST or None, instance=address)
		context = {
			'form': form,
			'kunde': kunde,
			 }
		return render(request, 'cms-kundenadresse-bearbeiten.html', context)


@staff_member_required
def cms_kunde_löschen(request, pk):
	eintrag = get_object_or_404(User, pk=pk)
	eintrag.delete()
	messages.info(request, "Der Kunde wurde gelöscht.")
	return redirect("store:cms_kunden")	


@staff_member_required
def cms_produkte(request, first_cat):
	category = Category.objects.all()
	filter_query = request.GET.get('category', '')
	search_query = request.GET.get('search', '')
	first_cat_new = ''
	current_cat = 'standard'

	if search_query:
		produkte = Item.objects.filter(Q(titel__icontains=search_query) | Q(artikelnr__icontains=search_query) | Q(kategorie__name__icontains=search_query) | Q(subkategorie__sub_name__icontains=search_query))
		
		if filter_query:
			produkte = produkte.filter(kategorie__name=filter_query)
			current_cat_query = get_object_or_404(Category, name=filter_query)
			current_cat = current_cat_query.name 
			first_cat_new = current_cat
		else:
			pass
	else:
		if filter_query:
			produkte = Item.objects.filter(kategorie__name=filter_query)
			current_cat_query = get_object_or_404(Category, name=filter_query)
			current_cat = current_cat_query.name 
			first_cat_new = current_cat
		else: 
			produkte = Item.objects.filter(kategorie__name=first_cat)
			
	if current_cat == 'standard':
		current_cat = first_cat
	else:
		pass


	context = {
		'category': category,
		'produkte': produkte,
		'first_cat_new' : first_cat_new,
		'current_cat' : current_cat
	 }
	return render(request, 'cms-produkte.html', context)


@staff_member_required
def product_cms_create(request, cat):
	if request.method == "POST":
		form = ProduktCreateForm(request.POST or None, request.FILES or None)
		if form.is_valid():
			result = form.save(commit=False)
			result.kategorie = get_object_or_404(Category, name=cat)
			result.save()
			return redirect('store:cms_produkte', first_cat=cat)
		else:
			messages.error(request, "Error")
	else: 	
		initial_data = {
		        'kategorie': cat,
		        
		    }
		form = ProduktCreateForm(initial=initial_data)

	context = {
		'form': form,
		'cat' : cat,
				}
	return render(request, 'cms-produkte-erfassen.html', context)


@staff_member_required
def product_cms_edit(request, pk, current_cat):
	item = get_object_or_404(Item, pk=pk)
	
	if request.method == "POST":
		form = ProduktEditForm(request.POST or None, request.FILES or None, instance=item)
		if form.is_valid():
			form.save()
			return redirect('store:cms_produkte', first_cat=current_cat)

		else:
			messages.error(request, "Error")
	else: 
		form = ProduktEditForm(request.POST or None, request.FILES or None, instance=item)

	context = {
		'form': form,
		'item': item,
		'current_cat': current_cat
				}
	return render(request, 'cms-produkte-bearbeiten.html', context)

@staff_member_required
def cms_remove_product(request, pk, cat):
	eintrag = get_object_or_404(Item, pk=pk)
	eintrag.delete()
	messages.info(request, "Der Eintrag wurde gelöscht.")
	return redirect("store:cms_produkte", first_cat=cat)	

@staff_member_required
def cms_elemente_statistik(request):
	search_query = request.GET.get('search', '')
	if search_query:
		elemente = Elemente.objects.filter(Q(dichtungen__titel__icontains=search_query) | Q(kuehlposition__icontains=search_query) | Q(aussenbreite__icontains=search_query) | Q(aussenhöhe__icontains=search_query) | Q(elementnr__icontains=search_query))
	else:
		elemente = Elemente.objects.all

	context = {
		'elemente':elemente,
		
	 }
	return render(request, 'cms-elemente-statistik.html', context)

@staff_member_required
def cms_elemente(request, pk):
    kunde_data = Kunde.objects.get(pk=pk)
    search_query = request.GET.get('search', '')

    if search_query:
        elemente = Elemente.objects.filter(
            Q(dichtungen__titel__icontains=search_query) |
            Q(kuehlposition__icontains=search_query) |
            Q(aussenbreite__icontains=search_query) |
            Q(aussenhöhe__icontains=search_query) |
            Q(elementnr__icontains=search_query)
        ).filter(kunde=kunde_data).order_by('kunde', 'elementnr')
    else:
        elemente = Elemente.objects.filter(kunde=kunde_data).order_by('elementnr')

    context = {
        'elemente': elemente,
        'kunde_id': pk,
        'kunde_data': kunde_data,
    }
    return render(request, 'cms-elemente.html', context)


@staff_member_required
def cms_elemente_create(request, pk):
    kunde_queryset = Kunde.objects.filter(pk=pk)
    form = ElementeCreateForm(request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            elemente_instance = form.save(commit=False)
            elemente_instance.save()
            elemente_instance.kunde.set(kunde_queryset)
            elemente_instance.save()
            return redirect('store:cms_elemente', pk=pk)
        else:
            messages.error(request, "Error")
    
    context = {
        'form': form,
        'kunde_id':pk,
    }
    return render(request, 'cms-elemente-erfassen.html', context)

@staff_member_required
def cms_elemente_edit(request, pk, cpk):
	element = get_object_or_404(Elemente, pk=pk)
	
	if request.method == "POST":
		form = ElementeEditForm(request.POST or None, instance=element)
		if form.is_valid():
			form.save()
			return redirect('store:cms_elemente', pk=cpk)

		else:
			messages.error(request, "Error")

	else: 
		form = ElementeEditForm(request.POST or None, instance=element)

	context = {
		'form': form,
		'element': element,
				}
	return render(request, 'cms-elemente-bearbeiten.html', context)


@staff_member_required
def cms_elemente_löschen(request, pk, cpk):
	eintrag = get_object_or_404(Elemente, pk=pk)
	eintrag.delete()
	messages.info(request, "Der Eintrag wurde gelöscht.")
	return redirect('store:cms_elemente', pk=cpk)	


@staff_member_required
def cms_versandkosten(request):
	shippingcost = ShippingCost.objects.all()
	context = {
		'object' : shippingcost,
	}
	return render(request, 'cms-versandkosten.html', context)

@staff_member_required
def cms_versandkosten_erfassen(request):
	if request.method == "POST":
		form = VersandkostenCreateForm(request.POST or None, request.FILES or None)
		if form.is_valid():
			form.save()
			return redirect('store:cms_versandkosten')

		else:
			messages.error(request, "Error")

	else: 
		form = form = VersandkostenCreateForm()

	context = {
		'form': form,
				}
	return render(request, 'cms-versandkosten-erfassen.html', context)

@staff_member_required
def cms_remove_versandkosten(request, pk):
	eintrag = get_object_or_404(ShippingCost, pk=pk)
	eintrag.delete()
	messages.info(request, "Der Eintrag wurde gelöscht.")
	return redirect("store:cms_versandkosten")	

@staff_member_required
def cms_statistik_produkte(request):
	labels = []
	data = []


	queryset = Item.objects.values(
			'titel'
		).annotate(
			total_sales=Coalesce(Sum('orderitem__quantity'), 0)
		).order_by('-total_sales')[:5]

	for entry in queryset:
		labels.append(entry['titel'])
		data.append(entry['total_sales'])

	context = {
		'queryset': queryset,
		'labels': labels,
        'data': data,		
	}

	return render(request, 'cms-statistik-produkte.html', context)

@staff_member_required
def cms_benutzerdaten(request):
	context = { }
	return render(request, 'cms-benutzerdaten.html', context)


@login_required
def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, ('Erfolgreich angemeldet.'))
			return redirect ('store:cms')
		else:
			messages.success(request, ('Fehler - bitte überprüfen Sie Ihre Angaben.'))
			return redirect ('store:login_user')
	else:
		context = {}
		return render(request, 'cms-login.html', context )

@login_required
def logout_user(request):
	logout(request)
	messages.success(request, ('Sie wurden erfolgreich abgemeldet.'))
	return redirect('store:login_user')