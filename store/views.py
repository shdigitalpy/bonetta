from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, OrderItem, Order, Address, ShippingAddress, Elemente, Kunde, Category, Subcategory, ShippingCost
from django.views.generic import ListView, DetailView, View, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import ElementeCreateForm, KundeEditAdvancedForm, KundeCreateForm, VersandkostenCreateForm, AddressForm, RegistrationForm, PaymentForm, ShippingAddressForm, CheckoutForm, AussenmassForm, ProduktEditForm, KundeEditForm, ElementeEditForm
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

	context = { }
	return render(request, 'cms.html', context)


@staff_member_required
def cms_bestellungen(request):
	order = Order.objects.filter(ordered=True)
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
def cms_kunden(request):
	user = User.objects.all().order_by('-id')
	search_query = request.GET.get('search', '')


	if search_query:
		user = User.objects.filter(Q(profile__firmenname__icontains=search_query))

	else:
		user = User.objects.all().order_by('-id')
			

	context = {
			'user': user,		
			 }
	return render(request, 'cms-kunden.html', context)

@staff_member_required
def cms_kunden_erfassen(request):
	if request.method == "POST":
		form = KundeCreateForm(request.POST or None)
		if form.is_valid():
			new_user = User.objects.create_user(**form.cleaned_data)
			new_kunde = Kunde.objects.create(user=new_user, firmenname=request.POST['username'], rabatt=0)
			new_kunde.save()
			new_address = Address.objects.create(user=new_user, rechnung_strasse='Bitte ändern')
			
			return redirect('store:cms_kunden')

		else:
			messages.error(request, "Error")

	else: 
		form = form = KundeCreateForm()

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
def cms_produkte(request):
	category = Category.objects.all()
	filter_query = request.GET.get('category', '')
	search_query = request.GET.get('search', '')


	if search_query:
		produkte = Item.objects.filter(Q(titel__icontains=search_query) | Q(artikelnr__icontains=search_query) | Q(kategorie__name__icontains=search_query) | Q(subkategorie__sub_name__icontains=search_query))
	
		if filter_query:
			produkte = produkte.filter(kategorie__name=filter_query)
		else:
			pass
	else:
		if filter_query:
			produkte = Item.objects.filter(kategorie__name=filter_query)
		else: 
			produkte = Item.objects.all()
			

	context = {
		'category': category,
		'produkte': produkte,
	 }
	return render(request, 'cms-produkte.html', context)

@staff_member_required
def product_cms_edit(request, pk):
	item = get_object_or_404(Item, pk=pk)
	
	if request.method == "POST":
		form = ProduktEditForm(request.POST or None, request.FILES or None, instance=item)
		if form.is_valid():
			form.save()
			return redirect('store:cms_produkte')

		else:
			messages.error(request, "Error")
	else: 
		form = ProduktEditForm(request.POST or None, request.FILES or None, instance=item)

	context = {
		'form': form,
		'item': item,
				}
	return render(request, 'cms-produkte-bearbeiten.html', context)

@staff_member_required
def product_cms_create(request):
	if request.method == "POST":
		form = ProduktEditForm(request.POST or None, request.FILES or None)
		if form.is_valid():
			form.save()
			return redirect('store:cms_produkte')

		else:
			messages.error(request, "Error")

	else: 
		form = ProduktEditForm()

	context = {
		'form': form,
				}
	return render(request, 'cms-produkte-erfassen.html', context)

@staff_member_required
def cms_remove_product(request, pk):
	eintrag = get_object_or_404(Item, pk=pk)
	eintrag.delete()
	messages.info(request, "Der Eintrag wurde gelöscht.")
	return redirect("store:cms_produkte")	


@staff_member_required
def cms_elemente(request, pk):
	search_query = request.GET.get('search', '')
	if search_query:
		elemente = Elemente.objects.filter(Q(profile__firmenname__icontains=search_query) | Q(elementnr__icontains=search_query))
	else:
		kunde_data = Kunde.objects.get(pk=pk)

	context = {
		'kunde_data': kunde_data,
		
	 }
	return render(request, 'cms-elemente.html', context)


@staff_member_required
def cms_elemente_create(request, pk):

	form = ElementeCreateForm(request.POST or None)
	form.fields["kunde"].queryset = Kunde.objects.filter(pk=pk)
	
	if request.method == "POST":
		if form.is_valid():
			form.save()
			return redirect('store:cms_kunden')

		else:
			messages.error(request, "Error")

	else: 
		pass

	context = {
		'form': form,
				}
	return render(request, 'cms-elemente-erfassen.html', context)

@staff_member_required
def cms_elemente_edit(request, pk):
	element = get_object_or_404(Elemente, pk=pk)
	
	if request.method == "POST":
		form = ElementeEditForm(request.POST or None, instance=element)
		if form.is_valid():
			form.save()
			return redirect('store:cms_kunden')

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
def cms_elemente_löschen(request, pk):
	eintrag = get_object_or_404(Elemente, pk=pk)
	eintrag.delete()
	messages.info(request, "Der Eintrag wurde gelöscht.")
	return redirect("store:cms_kunden")	


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