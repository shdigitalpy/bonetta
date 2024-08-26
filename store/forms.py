from django import forms
from .models import *
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template

PAYMENT_CHOICES = (
	('R', 'Rechnung*'),
	('V', 'Vorkasse (2% Skonto)'),
	)

COUNTRY_CHOICES = [
	('S', 'Schweiz'),
	('D', 'Deutschland'),
	('A', 'Österreich'),

	]

class ElementeObjekteCreateForm(forms.ModelForm):
	class Meta:
		model = Objekte
		fields = ('name', 'serie', 'modell', 'typ' )
		labels = {
			'name': "Marke",
			'serie' : "Typ",
			'modell' : "Modell/Code",
			'typ' : "Serien-Nr.",
			
		}
		widgets = {
			
			'name': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':''}),
			'serie': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':''}),
			'modell': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':''}),
			'typ': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':''}),
			
		}


class InternalKundeForm(forms.ModelForm):
    class Meta:
        model = Kunde
        fields = ['firmenname', 'interne_nummer']

        widgets = {
			
			'firmenname': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':''}),
			'interne_nummer': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':''}),
			
				
			}

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['lieferung_strasse', 'lieferung_nr', 'lieferung_ort']


class InseratJobsCreateForm(forms.ModelForm):
	class Meta:
		model = JobsMarketplace
		fields = ('category','title','datejob','kindof','pensum', 'jobdescription', 'requirements','language','res_description','contact_person', 'place','region'  )

		labels = {
			'title' : "Titel des Eintrags:",
			'jobdescription' : "Job Beschreibung",
			'category' : "Kategorie",
			'requirements' : "Anforderungen",
			'res_description' : "Restaurant Beschreibung",
			'contact_person' : "Kontaktperson",
			'language' : "Sprachen",
			'place' : "Adresse",
			'datejob' : "Stellenantritt",
			'kindof' : "Anstellungsart",
			'pensum' : "Pensum",
			'region' : "Region"
		}
		
		widgets = {
			
			'title': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. Küchenchef'}),
			'jobdescription': forms.Textarea(attrs={

				'class': 'form-control col-6',
				'placeholder':'Beschreibung Aufgaben'}),
			'datejob': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. per sofort oder nach Vereinbarung'}),
			'kindof': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. Dauerstelle/Teilzeitstelle'}),
			'pensum': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. 100%'}),
			'language': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. Deutsch, Englisch erwünscht'}),
			'category' : forms.Select(attrs={
				'class': 'form-control col-6',
				}),
			'requirements': forms.Textarea(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. Kochlehre und Erfahrung in ähnlicher führender Position'}),
			'res_description': forms.Textarea(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. Bestens frequentierter Betrieb.'}),
			'contact_person': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. Herr Markus Müller, Geschäftsführer'}),
			'place': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. Landstrasse 4, 8447 Dachsen'}),
			'region' : forms.Select(attrs={
				'class': 'form-control col-6',
				}),

			
		}



class ProductMarkeLinkForm(forms.Form):
    item_marke = forms.ModelChoiceField(queryset=Marke.objects.all())


class InseratCreateForm(forms.ModelForm):
	class Meta:
		model = Marketplace
		fields = ('category','numberof', 'title', 'price', 'description', 'condition', 'marke_ins', 'typ_marke_ins', 'place','image','image1','image2','anonym_ins'  )

		labels = {
			'title' : "Titel des Eintrags:",
			'numberof' : "Stückzahl",
			'price' : "Preis",
			'description' : "Beschreibung",
			'condition' : "Zustand",
			'place' : "Standort",
			'image' : "Bild",
			'image1' : "Bild",
			'image2' : "Bild",
			'category' : "Kategorie",
			'anonym_ins' : "Veröffentlichung Adresse & Angaben",
			'marke_ins' : "Marke",
			'typ_marke_ins' : "Typ Bezeichnung"


		}
		

		widgets = {
			
			'title': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':'z.B. Küchenmaschine'}),
			'marke_ins': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':'Markenname'}),
			'typ_marke_ins': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':'Typ Bezeichnung'}),
			'numberof': forms.NumberInput(attrs={
				'class': 'form-control col-3',
				'placeholder':'Stückzahl'}),

			'price': forms.NumberInput(attrs={
				'class': 'form-control',
				'placeholder':'z.B. 100'}),
			'description': forms.Textarea(attrs={
				'maxlength': '100',
				'rows': '3',
				'class': 'form-control col-3',
				'placeholder':''}),
			'condition': forms.Select(attrs={
				'class': 'form-control',
				}),
			'place': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':'Wo'}),
			'image' : forms.FileInput(attrs={
				'class': 'form-control',
				}),
			'image1' : forms.FileInput(attrs={
				'class': 'form-control',
				}),
			'image2' : forms.FileInput(attrs={
				'class': 'form-control',
				}),
			'category' : forms.Select(attrs={
				'class': 'form-control',
				}),

			'anonym_ins' : forms.Select(attrs={
				'class': 'form-control',
				}),
		}

class CheckoutForm(forms.Form):
	rechnung_firmenname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	rechnung_vorname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	rechnung_nachname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))
	rechnung_strasse = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	rechnung_nr = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	rechnung_ort = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	rechnung_land = CountryField(blank_label='(Land auswählen)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
	rechnung_plz = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	lieferung_strasse = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	lieferung_nr = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	lieferung_ort = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	lieferung_land = CountryField(blank_label='(Land auswählen)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
	lieferung_plz = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))

	firmenname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	vorname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	nachname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	different_shipping_address = forms.BooleanField(required=False)
	use_other_billing = forms.BooleanField(required=False)
	use_default_shipping = forms.BooleanField(required=False)



class KundeCreateForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('username', 'email', 'password')
		widgets = {
			
			'username': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'email': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'password': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'first_name': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'last_name': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
		}

class CheckoutForm(forms.Form):
	rechnung_firmenname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	rechnung_vorname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	rechnung_nachname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))
	rechnung_strasse = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	rechnung_nr = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	rechnung_ort = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	rechnung_land = CountryField(blank_label='(Land auswählen)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
	rechnung_plz = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	lieferung_strasse = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	lieferung_nr = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	lieferung_ort = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))
	lieferung_land = CountryField(blank_label='(Land auswählen)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
	lieferung_plz = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': ''
		}))

	firmenname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	vorname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	nachname = forms.CharField(required=False, widget=forms.TextInput(attrs={
		'class': 'form-control',
		'placeholder': '',
		}))

	different_shipping_address = forms.BooleanField(required=False)
	use_other_billing = forms.BooleanField(required=False)
	use_default_shipping = forms.BooleanField(required=False)


class PaymentForm(forms.Form):
	payment_option = forms.ChoiceField(
				label='',
		        required=True,
		        widget=forms.RadioSelect(attrs={
						'class': 'list-inline',

						}),
		        choices=PAYMENT_CHOICES,
    )


class RegistrationForm(SignupForm):
	username = forms.CharField(max_length=500, required=True, label="",
					widget=forms.TextInput(attrs={
						'placeholder': 'Benutzername',
						'class': 'form-control',
						}),
					help_text='Bitte einen gültigen Benutzernamen eingeben'
					)

	first_name = forms.CharField(max_length=500, required=True, label="",
					widget=forms.TextInput(attrs={
						'placeholder': 'Vorname',
						'class': 'form-control',
						}),
					help_text='Bitte einen gültigen Vornamen eingeben')

	last_name = forms.CharField(max_length=500, required=True, label="",
					widget=forms.TextInput(attrs={
						'placeholder': 'Nachname',
						'class': 'form-control',
						}),
					help_text='Bitte einen gültigen Nachnamen eingeben')

	email = forms.EmailField(max_length=500, required=True, label="",
					widget=forms.EmailInput(attrs={
						'placeholder': 'E-Mail Adresse',
						'required': True, 
						'class': 'form-control',
						'type': 'email'
						}),
					help_text='Bitte eine gültige E-Mail Adresse eingeben')

	firmenname = forms.CharField(max_length=500, required=False, label="",
					widget=forms.TextInput(attrs={
						'placeholder': 'Firmenname',
						'class': 'form-control'

						}))

	strasse = forms.CharField(max_length=500, required=True, label="Adresse",
					widget=forms.TextInput(attrs={
						'placeholder': 'Strasse',
						'class': 'form-control'

						}),
					help_text='Bitte eine gültige Strasse eingeben')

	nr = forms.CharField(max_length=500, required=True, label="",
					widget=forms.TextInput(attrs={
						'placeholder': 'Nr.',
						'class': 'form-control'

						}),
					help_text='Bitte eine gültige Strassen-Nr. eingeben')

	plz = forms.CharField(max_length=500, required=True, label="",
					widget=forms.TextInput(attrs={
						'placeholder': 'PLZ',
						'class': 'form-control'

						}))

	ort = forms.CharField(max_length=500, required=True, label="",
					widget=forms.TextInput(attrs={
						'placeholder': 'Ort',
						'class': 'form-control'

						}),
					help_text='Bitte einen gültigen Ort eingeben')

	phone = forms.CharField(max_length=500, required=True, label="",
					widget=forms.TextInput(attrs={
						'placeholder': 'Telefon- oder Mobile-Nr.',
						'class': 'form-control'

						}),
					help_text='Bitte eine gültige Telefon-Nr. eingeben')

	mobile = forms.CharField(max_length=500, required=False, label="",
					widget=forms.TextInput(attrs={
						'placeholder': 'Mobile-Nr.',
						'class': 'form-control'

						}))

	land = CountryField().formfield(
					widget=forms.Select(attrs={
						'class': 'form-control'

						}),
					help_text='Bitte ein gültiges Land auswählen')
	newsletter = forms.BooleanField(required=False)

	def __init__(self, *args, **kwargs):
		super(RegistrationForm, self).__init__(*args, **kwargs)
		self.fields['email'].label = ""
		self.fields['password1'].label = "Passwort:"
		self.fields['password2'].label = "Passwort (wiederholen):"
		self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Passwort'})
		self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Passwort wiederholen'})
		

	def signup(self, request, user):
		user.username = self.cleaned_data['username']
		user.email = self.cleaned_data['email']
		user.password1 = self.cleaned_data['password1']
		user.password2 = self.cleaned_data['password2']
		user.save()
		return user

	def save(self, request):
		user = super(RegistrationForm, self).save(request)
		kunde, created = Kunde.objects.get_or_create(user=user)
		kunde.firmenname = self.cleaned_data['firmenname']
		kunde.newsletter = self.cleaned_data['newsletter']
		kunde.phone = self.cleaned_data['phone']
		kunde.mobile = self.cleaned_data['mobile']
		kunde.rabatt = 0
		kunde.save()
		address, created = Address.objects.get_or_create(user=user)
		address.user.first_name = self.cleaned_data['first_name']
		address.user.last_name = self.cleaned_data['last_name']
		address.rechnung_strasse = self.cleaned_data['strasse']
		address.rechnung_nr = self.cleaned_data['nr']
		address.rechnung_ort = self.cleaned_data['ort']
		address.rechnung_land = self.cleaned_data['land']
		address.rechnung_plz = self.cleaned_data['plz']
		address.address_type = "B"
		address.save()
		#email
		firmenname = self.cleaned_data['firmenname']
		username = user.username
		phone = self.cleaned_data['phone']
		mobile = self.cleaned_data['mobile']
		plz = self.cleaned_data['plz']
		ort = self.cleaned_data['ort']
		subject = 'Registration Neuer Kunde'
		template = render_to_string('shop/registration-email.html', {
			
			'firmenname': firmenname, 
			'username': username,
			'phone': phone,
			'mobile': mobile,
			'plz': plz,
			'ort': ort,			
			 })
		
		#send email for order
		email = ''
		email = EmailMessage(
			subject,
			template,
			email,
			['bestellungen@gastrodichtung.ch', 'livio.bonetta@geboshop.ch', 'sandro@sh-digital.ch'],
		)

		email.fail_silently=False
		email.content_subtype = "html"
		email.send()
		return user



class AddressForm(forms.ModelForm):
	class Meta:
		model = Address  # Your model
		fields = (
			'rechnung_strasse',
			'rechnung_nr',
			'rechnung_plz',
			'rechnung_ort',
			'rechnung_land',
			'address_type'
			
			 )
		labels = {
			'rechnung_strasse' : "Strasse:",
			'rechnung_nr' : "Nr.",
			'rechnung_ort' : "Ort",
			'rechnung_land' : "Land",
			'rechnung_plz' : "PLZ",
			'address_type' : "Adresse-Typ:"

		}
		widgets = {
			'rechnung_strasse': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'Strasse'}),
			'rechnung_nr': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'Nr.'}),
			'rechnung_ort': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'Ort'}),
			'rechnung_land': forms.Select(attrs={
				'class': 'form-control',
				}),
			'rechnung_plz': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'PLZ'}),
			'address_type': forms.Select(attrs={
				'class': 'form-control',
				}),
		}


class ShippingAddressForm(forms.ModelForm):
	class Meta:
		model = ShippingAddress  # Your model
		fields = (
			'lieferung_strasse',
			'lieferung_nr',
			'lieferung_plz',
			'lieferung_ort',
			'lieferung_land',
			
			 )
		labels = {
			'lieferung_strasse' : "Strasse:",
			'lieferung_nr' : "Nr.",
			'lieferung_ort' : "Ort",
			'lieferung_land' : "Land",
			'lieferung_plz' : "PLZ",

		}
		widgets = {
			'lieferung_strasse': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'Strasse'}),
			'lieferung_nr': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'Nr.'}),
			'lieferung_ort': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'Ort'}),
			'lieferung_land': forms.Select(attrs={
				'class': 'form-control',
				}),
			'lieferung_plz': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'PLZ'}),
		}



class KundeEditForm(forms.ModelForm):
	class Meta:
		model = User
		fields = (
			'username',
			'first_name',
			'last_name',
			'email',
			'date_joined',
			'is_active'
			)
		widgets = {
			
			'username': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'first_name': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'last_name': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'email': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'password': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'date_joined': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'readonly':'readonly'}),
		}

class KundeEditAdvancedForm(forms.ModelForm):
	class Meta:
		model = Kunde
		fields = (
			'firmenname',
			'interne_nummer',
			'rabatt',
			'newsletter',
			'phone',
			'mobile',
			'birthday'

			)
		widgets = {
			
			'firmenname': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'interne_nummer': forms.NumberInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'rabatt': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'newsletter': forms.Select(attrs={
				'class': 'form-control col-3',}),
			'phone': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'mobile': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'birthday': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
		}

class ElementeCreateForm(forms.ModelForm):
	class Meta:
		model = Elemente
		fields = ('kuehlposition', 'elementnr', 'bemerkung', 'dichtungen', 'aussenbreite', 'aussenhöhe' )
		labels = {
			'kunde': "Kunde",
			'elementnr' : "Element-Nr.",
			'kuehlposition' : "Kühlposition",
			'dichtung_masse' : "Dichtungsmasse",
			'bemerkung' : "Kühlunterbau",
			'aussenbreite' : "Aussenmass Breite",
			'aussenhöhe' : "Aussenmass Höhe"
		}
		widgets = {
			'dichtungen': forms.Select(attrs={
				'class': 'form-control col-6'}),
			'elementnr': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'Eine ganze Zahl eingeben'}),
			'aussenbreite': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. 380'}),
			'aussenhöhe': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. 440'}),
			'kuehlposition': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. Küche UG'}),
			'bemerkung': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':''}),
			'kunde': forms.CheckboxSelectMultiple(attrs={
				'class': 'elementcheckbox',
				'required': 'True'
				}),
		}

	def __init__(self, *args, **kwargs):
		super(ElementeCreateForm, self).__init__(*args, **kwargs)
		self.fields['dichtungen'].queryset = Item.objects.filter(kategorie__name__contains='PVC')

class ElementeEditForm(forms.ModelForm):
	class Meta:
		model = Elemente
		fields = ('kuehlposition', 'elementnr', 'bemerkung', 'dichtungen', 'aussenbreite', 'aussenhöhe' )
		labels = {
			'elementnr' : "Element-Nr.",
			'kuehlposition' : "Kühlposition",
			'dichtung_masse' : "Dichtungsmasse",
			'bemerkung' : "Kühlunterbau",
			'aussenbreite' : "Aussenmass Breite",
			'aussenhöhe' : "Aussenmass Höhe"
		}
		widgets = {
			'dichtungen': forms.Select(attrs={
				'class': 'form-control col-6'}),
			'elementnr': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'Eine ganze Zahl eingeben'}),
			'aussenbreite': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. 380'}),
			'aussenhöhe': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. 440'}),
			'kuehlposition': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. Küche UG'}),
			'bemerkung': forms.TextInput(attrs={
				'class': 'form-control col-6',
				'placeholder':''}),
			'kunde': forms.CheckboxSelectMultiple(attrs={
				'class': 'elementcheckbox',
				
				}),
		}


class ProduktCreateForm(forms.ModelForm):
	class Meta:
		model = Item
		fields = (
			'sortierung',
			'subkategorie',
			'titel',
			'artikelnr',
			'montage',
			'lieferung',
			'farbe',
			'preis', 
			'preis2', 
			'preis3', 
			'preis4',
			'preis5',
			'preis6',
			'preis7',
			'beschreibung',
			'titelbild', 
			'slug',
			'material', 
			'nut', 
			'falz',
			'falzluft',
			'fuge',
			'glasdicke',
			'hersteller',

			
			
			)

		labels = {
			
			'sortierung': "Sortierung",
			'titel' : "Bezeichnung",
			'artikelnr' : "Artikel-Nr",
			'lieferung' : "Lieferung",
			'montage' : "Typ",
			'farbe' : "Farbe",
			'preis': "Preis 1 (PVC bis 2m / Gummi & Stahlzargen usw. bis 25m / Dusch bis 5 Stück / Zubehör)", 
			'preis2': "Preis 2 (PVC ab 2m / Gummi & Stahlzargen usw. ab 25m / Dusch ab 5 Stück)", 
			'preis3': "Preis 3 (PVC ab 4m / Gummi & Stahlzargen usw. ab 50m / Dusch ab 10 Stück)", 
			'preis4': "Preis 4 (Gummi & Stahlzargen usw. ab 100m / Dusch ab 25 Stück)",
			'preis5': "Preis 5 (Gummi & Stahlzargen usw. ab 200m / Dusch ab 50 Stück)",
			'preis6': "Preis 6 (Gummi & Stahlzargen usw. ab 500m)",
			'preis7': "Preis 7 (nur Stahlzargen usw. ab 1000m)",
			'beschreibung' : "Bemerkung",
			'slug': "URL",
			'nut': "Nut:",
			'falzluft': "Falzluft:",
			'falz': "Falz:",
			'fuge': "Fuge:",
			'glasdicke': "Glasdicke:",
			'material': "Material:",
			'hersteller': "Hersteller:",
		}

		widgets = {
			'sortierung': forms.TextInput(attrs={
				'class': 'form-control',
				}),
			'artikelnr': forms.TextInput(attrs={
				'class': 'form-control',
				}),
			'kategorie': forms.Select(attrs={
				'class': 'form-control',
				}),
			'subkategorie': forms.Select(attrs={
				'class': 'form-control',
				}),
			'titel': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'artikelnr': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'lieferung': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'montage': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'farbe': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis2': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis3': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis4': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis5': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis6': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis7': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			
			'beschreibung': forms.Textarea(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'titelbild' : forms.FileInput(attrs={
				'class': 'form-control',
				}),
			
			'slug': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder': ''}),

			'nut': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'falz': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'falzluft': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'fuge': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'glasdicke': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'material': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			
			'hersteller': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
		}
		

class ProduktEditForm(forms.ModelForm):
	class Meta:
		model = Item
		fields = (
			'sortierung',
			'kategorie',
			'subkategorie',
			'titel',
			'artikelnr',
			'montage',
			'lieferung',
			'farbe',
			'preis', 
			'preis2', 
			'preis3', 
			'preis4',
			'preis5',
			'preis6',
			'preis7',
			'beschreibung',
			'titelbild', 
			'slug',
			'material', 
			'nut', 
			'falz',
			'falzluft',
			'fuge',
			'glasdicke',
			'hersteller',

			
			
			)

		labels = {
			
			'sortierung': "Sortierung",
			'titel' : "Bezeichnung",
			'artikelnr' : "Artikel-Nr",
			'lieferung' : "Lieferung",
			'montage' : "Typ",
			'farbe' : "Farbe",
			'preis': "Preis 1 (PVC bis 2m / Gummi & Stahlzargen usw. bis 25m / Dusch bis 5 Stück / Zubehör)", 
			'preis2': "Preis 2 (PVC ab 2m / Gummi & Stahlzargen usw. ab 25m / Dusch ab 5 Stück)", 
			'preis3': "Preis 3 (PVC ab 4m / Gummi & Stahlzargen usw. ab 50m / Dusch ab 10 Stück)", 
			'preis4': "Preis 4 (Gummi & Stahlzargen usw. ab 100m / Dusch ab 25 Stück)",
			'preis5': "Preis 5 (Gummi & Stahlzargen usw. ab 200m / Dusch ab 50 Stück)",
			'preis6': "Preis 6 (Gummi & Stahlzargen usw. ab 500m)",
			'preis7': "Preis 7 (nur Stahlzargen usw. ab 1000m)",
			'beschreibung' : "Bemerkung",
			'slug': "URL",
			'nut': "Nut:",
			'falzluft': "Falzluft:",
			'falz': "Falz:",
			'fuge': "Fuge:",
			'glasdicke': "Glasdicke:",
			'material': "Material:",
			'hersteller': "Hersteller:",
		}

		widgets = {
			'sortierung': forms.TextInput(attrs={
				'class': 'form-control',
				}),
			'artikelnr': forms.TextInput(attrs={
				'class': 'form-control',
				}),
			'kategorie': forms.Select(attrs={
				'class': 'form-control',
				}),
			'subkategorie': forms.Select(attrs={
				'class': 'form-control',
				}),
			'titel': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'artikelnr': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'lieferung': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'montage': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'farbe': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis2': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis3': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis4': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis5': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis6': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			'preis7': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			
			'beschreibung': forms.Textarea(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'titelbild' : forms.FileInput(attrs={
				'class': 'form-control',
				}),
			
			'slug': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder': ''}),

			'nut': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'falz': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'falzluft': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'fuge': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'glasdicke': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),

			'material': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
			
			'hersteller': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':''}),
		}
		



class VersandkostenCreateForm(forms.ModelForm):
	class Meta:
		model = ShippingCost
		fields = ('__all__')
		labels = {
			'price_from' : "Warenkorb von",
			'price_to' : "Warenkorb bis",
			'shipping_price' : "CHF Versandkosten",
		}
		widgets = {
			
			'price_from': forms.NumberInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'Betrag von'}),
			'price_to': forms.NumberInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'Betrag bis',
				}),
			'shipping_price': forms.NumberInput(attrs={
				'class': 'form-control col-6',
				'placeholder':'z.B. 18',
				}),
		}

class AussenmassForm(forms.ModelForm):
	class Meta:
		model = OrderItem  # Your model
		fields = ('aussenbreite', 'aussenhöhe')
		widgets = {
			'aussenbreite': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'z.B. 800mm'}),
			'aussenhöhe': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder':'z.B. 500mm'})
		}


class MarkeChangeForm(forms.ModelForm):
	class Meta:
		model = Marke
		fields = (
			'name',
			'slug',
			'markepic',
			'marketext',
			)
		widgets = {
			
			'name': forms.TextInput(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
			'markepic' : forms.FileInput(attrs={
				'class': 'form-control',
				}),
			
			'slug': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder': ''}),
			'marketext': forms.Textarea(attrs={
				'class': 'form-control col-3',
				'placeholder':''}),
		}