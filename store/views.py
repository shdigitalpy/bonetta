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
import qrcode
import base64


# Bestellformular
def bestellformular(request):
    email = settings.EMAIL_HOST_USER  # Use the email from settings
    elemente_range = range(1, 100)
    
    if request.method == "POST":
        # Retrieve form data
        kunden_nr = request.POST.get('kunden-nr')
        betrieb_person = request.POST.get('betrieb-person')
        adresse = request.POST.get('adresse')
        plz = request.POST.get('plz')
        ort = request.POST.get('ort')
        elemente_nr = request.POST.getlist('elemente-nr')  # list for multiple checkboxes
        montage = request.POST.get('montage')  # mit/ohne montage checkbox
        bemerkung = request.POST.get('bemerkung')

        # Prepare email subject and message content
        subject = 'Bestellung Elemente ' + betrieb_person + ' ' + kunden_nr
        template = render_to_string('crm/mail-bestellung-elemente.html', {
            'kunden_nr': kunden_nr,
            'betrieb_person': betrieb_person,
            'adresse': adresse,
            'plz': plz,
            'ort': ort,
            'elemente_nr': ', '.join(elemente_nr),  # Join list into string for display
            'montage': montage,
            'bemerkung': bemerkung,
        })

        # Send email for order
        email = EmailMessage(
            subject,
            template,
            settings.EMAIL_HOST_USER,  # Use the correct sender email
            ['sandro@sh-digital.ch']  # Recipient email
        )
        email.fail_silently = False
        email.content_subtype = "html"  # to send the email as HTML
        email.send()

        # Debugging: Print email host and password to ensure correct loading
        print(config('EMAIL_HOST_USER'))
        print(config('EMAIL_HOST_PASSWORD'))

        # Success message to be displayed after form submission
        context = {
            'message_kontakt': 'Die Nachricht wurde erfolgreich gesendet.',
            'elemente_range': elemente_range,
        }
        return redirect("store:danke")

    else:
        # Render empty form for GET requests
        context = {
            'elemente_range': elemente_range,
        }
        return render(request, 'bestellformular.html', context)



@staff_member_required
def download_qr_code(request):
    url = request.build_absolute_uri(reverse('store:bestellformular'))

    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR Code
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Less error correction
        box_size=10,  # Size of each box in pixels
        border=4,  # Border size
    )
    
    # Add the URL data to the QR code
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white')

    # Save the image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Return the image as an HTTP response with content-disposition to download
    response = HttpResponse(buffer, content_type="image/png")
    response['Content-Disposition'] = 'attachment; filename="qr_code_bestellformular.png"'
    return response

@staff_member_required
def qr_code_view(request):
    url = request.build_absolute_uri(reverse('store:bestellformular'))

    # Create the QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR Code
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Less error correction
        box_size=10,  # Size of each box in pixels
        border=4,  # Border size
    )
    
    # Add the URL data to the QR code
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white')

    # Save the image to a BytesIO object
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # Convert the image to base64 to embed in HTML
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Pass the base64 image to the template
    return render(request, 'crm/qr-code.html', {'qr_code_base64': image_base64})


@staff_member_required
def delete_kunde_user_relationship(request, pk):
    # Get the Kunde object by primary key
    kunde = get_object_or_404(Kunde, pk=pk)
    
    # Unlink the user
    kunde.user = None
    kunde.save()
    
    # Redirect back to the customer list or another page
    return redirect(reverse('store:cms_kunden'))





def danke(request):
	context = {
	}
	return render (request, 'crm/danke.html', context)


#CMS
@staff_member_required
def cms_elemente_statistik(request):
    # Initialize the queryset
    elemente = Elemente.objects.all()
    
    # Capture individual search criteria
    produkt = request.GET.get('produkt', '')
    kuehlposition = request.GET.get('kuehlposition', '')
    aussenbreite = request.GET.get('aussenbreite', '')
    aussenhöhe = request.GET.get('aussenhöhe', '')
    serie = request.GET.get('serie', '')
    modell = request.GET.get('modell', '')
    typ = request.GET.get('typ', '')
    name = request.GET.get('name', '')
    
    # Capture sort_by parameter, default to sorting by 'kunde__firmenname'
    sort_by = request.GET.get('sort', 'kunde')

    # Filter the queryset based on search criteria
    if produkt:
        elemente = elemente.filter(produkt__icontains=produkt)
        # If no elements are found with the produkt, search in dichtungen.titel
        if not elemente.exists():
            elemente = Elemente.objects.filter(dichtungen__titel__icontains=produkt)

    if kuehlposition:
        elemente = elemente.filter(kuehlposition__icontains=kuehlposition)
    
    if aussenbreite:
        try:
            aussenbreite_value = int(aussenbreite)
            elemente = elemente.filter(aussenbreite=aussenbreite_value)
        except ValueError:
            pass  # Ignore invalid integer input
    
    if aussenhöhe:
        try:
            aussenhöhe_value = int(aussenhöhe)
            elemente = elemente.filter(aussenhöhe=aussenhöhe_value)
        except ValueError:
            pass  # Ignore invalid integer input
    
    if serie:
        elemente = elemente.filter(elemente_objekte__serie__icontains=serie)
    
    if modell:
        elemente = elemente.filter(elemente_objekte__modell__icontains=modell)
    
    if typ:
        elemente = elemente.filter(elemente_objekte__typ__icontains=typ)
    
    if name:
        elemente = elemente.filter(elemente_objekte__name__icontains=name)

    # Apply sorting based on the 'sort' parameter
    if sort_by == 'kunde':
        elemente = elemente.order_by('kunde__firmenname')
    elif sort_by == 'elementnr':
        elemente = elemente.order_by('elementnr')
    else:
        # Default to sorting by kunde__firmenname if no valid sort is provided
        elemente = elemente.order_by('kunde__firmenname')

    # Use distinct() to avoid duplicates if multiple criteria match
    elemente = elemente.distinct()

    # Calculate total laufmeter
    total_laufmeter = sum([element.elemente_laufmeter() for element in elemente])

    # Count the number of Elemente records
    elemente_count = elemente.count()

    # Pass total laufmeter and filtered elements to the context
    context = {
        'elemente': elemente,
        'total_laufmeter': total_laufmeter,  # Pass total laufmeter to template
        'elemente_count': elemente_count,  # Pass the count of elements to template
        'sort_by': sort_by,  # Pass sorting parameter to the template
    }

    return render(request, 'cms-elemente-statistik.html', context)




@staff_member_required
def cms_elemente_objekte_löschen(request, pk, epk, cpk):
    eintrag = get_object_or_404(Objekte, pk=pk)
    eintrag.delete()
    messages.info(request, "Das Objekt wurde gelöscht.")
    return redirect("store:cms_elemente_objekte", pk=epk, cpk=cpk)


@staff_member_required
def cms_elemente_objekte_bearbeiten(request, pk, epk, cpk):
    # Retrieve the Elemente instance (as before)
    elemente_instance = get_object_or_404(Elemente, pk=epk)

    # Retrieve the existing Objekte instance that we want to edit
    objekte_instance = get_object_or_404(Objekte, pk=pk)

    # Initialize the form with the existing objekte_instance
    form = ElementeObjekteCreateForm(request.POST or None, instance=objekte_instance)

    if request.method == "POST":
        if form.is_valid():
            # Save the form and update the objekte_instance
            objekte_instance = form.save(commit=False)
            objekte_instance.save()

            # Ensure the relationship between objekte_instance and elemente_instance is maintained
            objekte_instance.objekte.set([elemente_instance])  # Maintain the association
            objekte_instance.save()

            messages.success(request, "Objekt successfully updated and associated with Elemente.")
            return redirect("store:cms_elemente_objekte", pk=epk, cpk=cpk)
        else:
            messages.error(request, "Error in form submission. Please check the fields and try again.")

    context = {
        'form': form,
        'pk': pk,
        'epk': epk,
        'cpk': cpk,
    }
    return render(request, 'cms-elemente-objekte-erfassen.html', context)


@staff_member_required
def cms_elemente_objekte_erfassen(request, pk, cpk):
    # Ensure we get a single instance of Elemente
    elemente_instance = get_object_or_404(Elemente, pk=pk)  # Use get_object_or_404 for a single object

    form = ElementeObjekteCreateForm(request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            objekte_instance = form.save(commit=False)
            objekte_instance.save()
            # Associate the newly created objekte with the given elemente
            objekte_instance.objekte.set([elemente_instance])  # Pass a list to set
            objekte_instance.save()
            messages.success(request, "Objekt successfully created and associated with Elemente.")
            return redirect("store:cms_elemente_objekte", pk=pk, cpk=cpk)
        else:
            messages.error(request, "Error in form submission. Please check the fields and try again.")
    
    context = {
        'form': form,
        'pk': pk,
        'cpk': cpk,
    }
    return render(request, 'cms-elemente-objekte-erfassen.html', context)

@staff_member_required
def cms_elemente_objekte(request, pk, cpk):
	kunde = Kunde.objects.get(pk=cpk)
	elemente_data = get_object_or_404(Elemente, pk=pk)
	objekte = Objekte.objects.filter(objekte=elemente_data).order_by('id')

	context = {
    	'kunde': kunde,
    	'cpk':cpk,
    	'pk': pk,
        'objekte': objekte,
    }
	return render(request, 'cms-elemente-objekte.html', context)


def anleitung_videos(request):
	context = {
	}
	return render (request, 'anleitung-videos.html', context)




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
			marken = Marke.objects.all()
			context = {
				'items': items,
				'marken' : marken, 
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

#Kontaktseite END



def firma(request):
	context = { }
	return render(request, 'montage.html', context)



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



def lieferanten(request):
    search_query = request.GET.get('search', '')
    if search_query:
        lieferanten = Lieferanten.objects.filter(
            Q(name__icontains=search_query) |
            Q(adresse__icontains=search_query) |
            Q(ort__icontains=search_query) |
            Q(plz__icontains=search_query)
        ).order_by('-id')
    else:
        lieferanten = Lieferanten.objects.all().order_by('-id')

    context = {
        'lieferanten': lieferanten,
    }
    return render(request, 'crm/lieferanten.html', context)

def lieferant_create(request):
    if request.method == 'POST':
        form = LieferantenForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:lieferanten')
    else:
        form = LieferantenForm()

    return render(request, 'crm/lieferanten-erstellen.html', {'form': form})

def lieferant_edit(request, pk):
    lieferant = get_object_or_404(Lieferanten, pk=pk)
    if request.method == 'POST':
        form = LieferantenForm(request.POST, instance=lieferant)
        if form.is_valid():
            form.save()
            return redirect('store:lieferanten')
    else:
        form = LieferantenForm(instance=lieferant)

    return render(request, 'crm/lieferanten-erstellen.html', {'form': form})

@staff_member_required
def lieferant_delete(request, pk):
    eintrag = get_object_or_404(Lieferanten, pk=pk)
    eintrag.delete()
    messages.info(request, "Der Lieferant wurde gelöscht.")
    return redirect("store:lieferanten")

#CRM

def crm_lagerbestand(request):
    # Get the search parameters from GET
    dichtungstyp = request.GET.get('dichtungstyp', '')
    aussenbreite = request.GET.get('aussenbreite', '')
    aussenhoehe = request.GET.get('aussenhöhe', '')  # Using aussenhöhe with umlaut
    marke = request.GET.get('marke', '')

    # Start with the base queryset
    lager_queryset = CRMLager.objects.all()

    # Apply filters for each search field
    if dichtungstyp:
        lager_queryset = lager_queryset.filter(dichtungstyp__icontains=dichtungstyp)

    # Filter with tolerance for aussenbreite (+/- 10)
    if aussenbreite:
        try:
            aussenbreite_value = int(aussenbreite)
            lager_queryset = lager_queryset.filter(
                aussenbreite__gte=aussenbreite_value - 10,
                aussenbreite__lte=aussenbreite_value + 10
            )
        except ValueError:
            pass  # In case a non-integer is entered

    # Filter with tolerance for aussenhöhe (+/- 10)
    if aussenhoehe:
        try:
            aussenhoehe_value = int(aussenhoehe)  # Ensure this is correctly converted to an integer
            lager_queryset = lager_queryset.filter(
                aussenhöhe__gte=aussenhoehe_value - 10,
                aussenhöhe__lte=aussenhoehe_value + 10
            )
        except ValueError:
            pass  # In case a non-integer is entered

    if marke:
        # Adjust this depending on the field name in the 'Marke' model
        lager_queryset = lager_queryset.filter(marke__name__icontains=marke)

    # Always order by '-dichtungstyp' after filtering
    lager = lager_queryset.order_by('-dichtungstyp')

    context = {
        'lager': lager,
    }

    return render(request, 'crm/crm-lagerbestand.html', context)




def crm_lager_erfassen(request):
    if request.method == 'POST':
        # Initialize the form with POST data
        lager_form = CRMLagerForm(request.POST or None)

        if lager_form.is_valid():
            # Save the CRMLager instance
            lager = lager_form.save()  # Save the CRMLager form and get the instance

            # Redirect to another view or display a success message after saving
            return redirect('store:crm_lagerbestand')  # Change to the appropriate URL for your project

    else:
        # Initialize an empty form for GET request
        lager_form = CRMLagerForm()

    return render(request, 'crm/crm-lager-erfassen.html', {
        'lager_form': lager_form,
    })

@staff_member_required
def crm_lagerbestand_bearbeiten(request, pk):
    # Fetch the specific CRMLager instance using the primary key (pk)
    lager = get_object_or_404(CRMLager, pk=pk)

    if request.method == 'POST':
        # Initialize the form with POST data and the existing CRMLager instance
        lager_form = CRMLagerBestandForm(request.POST, instance=lager)

        if lager_form.is_valid():
            # Save only the 'lagerbestand' field
            lager_form.save()

            # Redirect to the lager overview page after successful update
            return redirect('store:crm_lagerbestand')  # Adjust URL to match your project

    else:
        # Prepopulate the form with the existing CRMLager 'lagerbestand' data
        lager_form = CRMLagerBestandForm(instance=lager)

    return render(request, 'crm/crm-lager-erfassen.html', {
        'lager_form': lager_form,
    })



@staff_member_required
def crm_lager_bearbeiten(request, pk):
    # Fetch the specific CRMLager instance using the primary key (pk)
    lager = get_object_or_404(CRMLager, pk=pk)

    if request.method == 'POST':
        # Initialize the form with POST data and the existing CRMLager instance
        lager_form = CRMLagerForm(request.POST, instance=lager)

        if lager_form.is_valid():
            # Save the updated CRMLager instance
            lager = lager_form.save()

            # Redirect to a lager overview page after successful update
            return redirect('store:crm_lagerbestand')  # Change to the appropriate URL

    else:
        # Prepopulate the form with the existing CRMLager instance data
        lager_form = CRMLagerForm(instance=lager)

    return render(request, 'crm/crm-lager-erfassen.html', {
        'lager_form': lager_form,
    })


@staff_member_required
def crm_lager_löschen(request, pk):
	eintrag = get_object_or_404(CRMLager, pk=pk)
	eintrag.delete()
	messages.info(request, "Der Artikel des Lagers wurde gelöscht.")
	return redirect("store:crm_lagerbestand")	

# CRM Kunden ---------------------------------------------------------------

def crm_new_kunden(request):
    search_query = request.GET.get('search', '')
    if search_query:
             
        kunden = Kunde.objects.filter(
            Q(firmenname__icontains=search_query) | 
            Q(interne_nummer__icontains=search_query) |
            Q(kunde_address__crm_ort__icontains=search_query) |
            Q(kunde_address__crm_strasse__icontains=search_query) |
            Q(kunde_address__crm_kanton__icontains=search_query)
        ).order_by('-id')
    else:
        kunden = Kunde.objects.all().order_by('-interne_nummer')
    
    context = {

        'kunden': kunden,
    }
    
    return render(request, 'crm/crm-kunden.html', context)

def crm_new_kunde_erfassen(request):
    if request.method == 'POST':
        # Initialize forms with POST data
        kunde_form = CRMKundeForm(request.POST)
        address_form = CRMAddressForm(request.POST)

        if kunde_form.is_valid() and address_form.is_valid():
            # First, save the Kunde instance
            kunde = kunde_form.save()  # Save the Kunde form and get the instance
            
            # Now assign the Kunde instance to the CRMAddress form before saving
            address = address_form.save(commit=False)  # Don't save yet
            address.kunde = kunde  # Assign the saved Kunde instance
            address.address_type = 'R'  # Set the address type (or whatever default)
            address.save()  # Now save the CRMAddress instance

            return redirect('store:crm_new_kunden')

    else:
        # Empty forms for GET request
        kunde_form = CRMKundeForm()
        address_form = CRMAddressForm()

    return render(request, 'crm/crm-kunde-erfassen.html', {
        'kunde_form': kunde_form,
        'address_form': address_form,
    })



@staff_member_required
def crm_new_kunde_bearbeiten(request, pk):
    kunde = get_object_or_404(Kunde, pk=pk)
    try:
        address = CRMAddress.objects.get(kunde=kunde)  # Get the related address
    except CRMAddress.DoesNotExist:
        address = None  # Handle the case where the address does not exist

    if request.method == 'POST':
        # Initialize the forms with POST data and existing instances
        kunde_form = CRMKundeForm(request.POST, instance=kunde)
        address_form = CRMAddressForm(request.POST, instance=address)

        if kunde_form.is_valid() and address_form.is_valid():
            # Save the Kunde form and get the updated instance
            kunde = kunde_form.save()

            # Save the updated address, assigning the updated Kunde instance
            address = address_form.save(commit=False)
            address.kunde = kunde  # Ensure the address is still associated with the correct Kunde
            address.address_type = 'R'  # Keep the same address type or update as needed
            address.save()

            return redirect('store:crm_new_kunden')

    else:
        # Prepopulate the forms with the existing Kunde and Address data
        kunde_form = CRMKundeForm(instance=kunde)
        address_form = CRMAddressForm(instance=address)

    return render(request, 'crm/crm-kunde-bearbeiten.html', {
        'kunde_form': kunde_form,
        'address_form': address_form,
    })

@staff_member_required
def cms_crm_adresse_bearbeiten(request, pk):
    # Fetch the Kunde object (the customer)
    kunde = get_object_or_404(Kunde, pk=pk)

    # Try to get the existing address or create a new one for the Kunde
    try:
        address = CRMAddress.objects.get(kunde=kunde)
    except CRMAddress.DoesNotExist:
        address = CRMAddress(kunde=kunde)  # Create a new address with the linked Kunde

    if request.method == "POST":
        form = CRMAddressForm(request.POST, instance=address)
        if form.is_valid():
            # Manually set the Kunde field and address_type to 'R' before saving
            address = form.save(commit=False)
            address.kunde = kunde  # Set the 'kunde' field
            address.address_type = 'R'  # Set the default address_type to 'R'
            address.save()
            messages.success(request, "Address updated successfully.")
            return redirect('store:crm_new_kunden')
        else:
            messages.error(request, "Error updating address.")
    else:
        form = CRMAddressForm(instance=address)

    context = {
        'form': form,
        'kunde': kunde,
    }
    return render(request, 'crm/crm-adresse-bearbeiten.html', context)

@staff_member_required
def cms_crm_kunde_löschen(request, pk):
	eintrag = get_object_or_404(Kunde, pk=pk)
	eintrag.delete()
	messages.info(request, "Der Kunde wurde gelöscht.")
	return redirect("store:crm_new_kunden")	

@staff_member_required
def crm_update_last_service(request, pk):
    # Fetch the specific customer by primary key
    kunde = get_object_or_404(Kunde, pk=pk)  

    if request.method == 'POST':
        # Pass POST data and instance of the Kunde to update
        form = CRMLastService(request.POST, instance=kunde)

        if form.is_valid():
            form.save()  # Save the last_service update
            messages.success(request, "Letzter Service erfolgreich aktualisiert!")
            return redirect('store:crm_new_kunden')  # Redirect after successful save
        else:
            # Handle form validation errors
            messages.error(request, "Fehler beim Aktualisieren des letzten Service.")
    else:
        # Initialize the form with existing data for GET request
        form = CRMLastService(instance=kunde)

    return render(request, 'crm/crm-update-last-service.html', {
        'form': form,
        'kunde': kunde,
    })


# CRM END

# ELEMENTE


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
		form = ElementeCreateForm(request.POST or None, instance=element)
		if form.is_valid():
			form.save()
			return redirect('store:cms_elemente', pk=cpk)

		else:
			messages.error(request, "Error")

	else: 
		form = ElementeCreateForm(request.POST or None, instance=element)

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
#ELEMENTE END

#webshop kunde

def cms_kunden(request):
    search_query = request.GET.get('search', '')
    
    # Retrieve User and Kunde separately, including search functionality
    if search_query:
        users = User.objects.filter(
            Q(profile__firmenname__icontains=search_query) | 
            Q(profile__interne_nummer__icontains=search_query)
        ).order_by('-id')
        
        kunden = Kunde.objects.filter(
            Q(firmenname__icontains=search_query) | 
            Q(interne_nummer__icontains=search_query)
        ).order_by('-id')
    else:
        users = User.objects.all().order_by('-id')
        kunden = Kunde.objects.all().order_by('-id')
    
    context = {
        'users': users,
        'kunden': kunden,
    }
    
    return render(request, 'cms-kunden.html', context)


def cms_kunden_erfassen(request):
    if request.method == "POST":
        kunde_form = KundeEditAdvancedForm(request.POST)
        address_form = AddressForm(request.POST)

        if kunde_form.is_valid() and address_form.is_valid():
            # Save Kunde and Address as needed
            new_user = User.objects.create_user(  # Example user creation
                username=kunde_form.cleaned_data['firmenname'],
                password=User.objects.make_random_password(),
                email=kunde_form.cleaned_data.get('email', '')
            )

            kunde = kunde_form.save(commit=False)
            kunde.user = new_user
            kunde.save()

            address = address_form.save(commit=False)
            address.kunde = kunde
            address.save()

            return redirect('store:cms_kunden')
        else:
            messages.error(request, "Fehler beim Erstellen des Kunden.")

    else:
        kunde_form = KundeEditAdvancedForm()
        address_form = AddressForm()

    return render(request, 'cms-kunden-erfassen.html', {
        'kunde_form': kunde_form,
        'address_form': address_form
    })




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


from django.shortcuts import get_object_or_404
from .models import Kunde, Address

def cms_kunde_bearbeiten(request, pk):
    # Get the Kunde instance
    kunde = get_object_or_404(Kunde, pk=pk)

    # Fetch the address using the user field (since Address is linked to User, not Kunde)
    try:
        address = Address.objects.get(user=kunde.user, address_type='R')  # Assuming 'R' is the main address type
    except Address.DoesNotExist:
        address = None  # Handle case if no address is found

    # Handle POST request and forms
    if request.method == "POST":
        kunde_form = KundeEditAdvancedForm(request.POST, instance=kunde)
        address_form = AddressForm(request.POST, instance=address)

        if kunde_form.is_valid() and address_form.is_valid():
            kunde_form.save()
            address = address_form.save(commit=False)
            address.user = kunde.user  # Make sure the address is linked to the correct user
            address.save()
            return redirect('store:cms_kunden')
        else:
            messages.error(request, "Fehler beim Speichern der Daten.")
    else:
        kunde_form = KundeEditAdvancedForm(instance=kunde)
        address_form = AddressForm(instance=address)

    context = {
        'kunde_form': kunde_form,
        'address_form': address_form,
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