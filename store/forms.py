from django import forms
from .models import *
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from allauth.account.forms import SignupForm
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.core.mail import EmailMessage
from django.template.loader import render_to_string, get_template
from django.core.validators import FileExtensionValidator

PAYMENT_CHOICES = (
    ('R', 'Rechnung*'),
    ('V', 'Vorkasse (2% Skonto)'),
    )

COUNTRY_CHOICES = [
    ('S', 'Schweiz'),
    ('D', 'Deutschland'),
    ('A', 'Österreich'),

    ]

STATUS_CHOICES = [
    ("In Bearbeitung", "In Bearbeitung"),
    ("Versendet", "Versendet"),
    ("Eingang Bestellung", "Eingang Bestellung"),
    ("Auftrag versendet", "Auftrag versendet"),
    ("Montage pendent", "Montage pendent"),
]

class LieferantenStatusForm(forms.ModelForm):
    name = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={
        "class": "form-control"
    }))

    class Meta:
        model = LieferantenStatus
        fields = ['name']

class KundenNrForm(forms.Form):
    kunden_nr = forms.IntegerField(
        label="Kunden-Nr.",
        min_value=1,  # Ensures only positive numbers are allowed
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Kunden-Nr. eingeben"
        })
    )



class ElementeCartItemEditForm(forms.Form):
   
    
    anzahl = forms.IntegerField(
        label="Anzahl",
        min_value=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control col-6",
            "placeholder": "Anzahl eingeben"
        })
    )
    
class ElementeCartItemForm(forms.Form):
    element_nr = forms.IntegerField(  # Now ensures only numbers are entered
        label="Element-Nr.",
        min_value=1,  # Prevents negative or zero values
        widget=forms.NumberInput(attrs={
            "class": "form-control col-6",
            "placeholder": "Element-Nr. eingeben"
        })
    )
    
    anzahl = forms.IntegerField(
        label="Anzahl",
        min_value=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Anzahl eingeben"
        })
    )


# update for Bezeichnung

class BezeichnungForm(forms.ModelForm):
    class Meta:
        model = Bezeichnung
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control col-6', 'placeholder': 'Bezeichnung'}),
        }


class ElementeCreateForm(forms.ModelForm):
    class Meta:
        model = Elemente
        fields = ('artikel', 'kuehlposition', 'elementnr', 'bezeichnung_new', 'bemerkung')

        widgets = {
            'kuehlposition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kühlposition'}),
            'elementnr': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Element-Nr.'}),
            'bezeichnung_new': forms.Select(attrs={'class': 'form-control'}),
            'bemerkung': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Bemerkung'}),
        }

        labels = {
            'bezeichnung_new': 'Bezeichnung',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Setze explizit das Queryset, falls du z. B. filtern willst
        self.fields['bezeichnung_new'].queryset = Bezeichnung.objects.all()

class NettopreisArtikelForm(forms.ModelForm):
    class Meta:
        model = Artikel
        fields = ['nettopreis']
        labels = {
            'nettopreis': "Einkaufspreis (CHF)",
        }
        widgets = {
            'nettopreis': forms.NumberInput(attrs={'class': 'form-control col-6'}),
        }
        
class ArtikelForm(forms.ModelForm):
    class Meta:
        model = Artikel
        fields = [
            'artikelnr', 'name', 
            'aussenbreite', 'aussenhöhe', 'lieferant', 
            'lieferanten_artikelnummern',
            'dichtungstypen',
            'nettopreis', 'preiscode', 
            'zubehoerartikelnr', 
            'bestpreis', 'bestpreis_lieferant'
        ]
        
        labels = {
            'artikelnr': "Artikelnummer",
            'name': "Dichtungstyp",
            'lieferant': "Lieferant",
            'aussenbreite': "Aussenbreite (mm)",
            'aussenhöhe': "Aussenhöhe (mm)",
            'nettopreis': "Einkaufspreis (CHF)",
            'vp': "Verkaufspreis (CHF)",
            'zubehoerartikelnr': "Zubehörartikel-Nr.",
            'lagerbestand': "Lagerbestand",
            'lagerort': "Lagerort",
            'preiscode': "Preiscode",
            'bestpreis': "Bestpreis (CHF)",
            'bestpreis_lieferant': "Bestpreis Lieferant",
            'lieferanten_artikelnummern': "Lieferant-Artikel-Nr",
            'dichtungstypen': "Lieferant-Dichtungstyp",
        }
        
        widgets = {
            'artikelnr': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'name': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'lieferant': forms.Select(attrs={'class': 'form-control col-6'}),
            
            'lagerort': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'aussenbreite': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            'aussenhöhe': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            'nettopreis': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            'vp': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            'zubehoerartikelnr': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'lagerbestand': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            'preiscode': forms.Select(attrs={'class': 'form-control col-6'}),
            'bestpreis': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            'bestpreis_lieferant': forms.Select(attrs={'class': 'form-control col-6'}),
            'lieferanten_artikelnummern': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'dichtungstypen': forms.TextInput(attrs={'class': 'form-control col-6'}),
        }



class PreiscodeForm(forms.ModelForm):
    class Meta:
        model = Preiscode
        fields = ['preiscode', 'faktor', 'transportkosten', 'rabatt', 'preisanpassung']
        labels = {
            'preiscode': "Preiscode",
            'faktor': "Faktor",
            'transportkosten': "Transportkosten",
            'rabatt': "Rabatt",
            'preisanpassung': "Preisanpassung",
        }
        widgets = {
            'preiscode': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'faktor': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            'transportkosten': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            'rabatt': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            'preisanpassung': forms.NumberInput(attrs={'class': 'form-control col-6'}),
        }

class PreiscodeArtikelForm(forms.ModelForm):
    class Meta:
        model = Artikel
        fields = [
            'preiscode'
      
        ]
        
        labels = {
            'preiscode': "Preiscode",
              
        }
        
        widgets = {
            
            'preiscode': forms.Select(attrs={'class': 'form-control col-6'}),
            
        }  

class LagerbestandForm(forms.ModelForm):
    class Meta:
        model = Artikel
        fields = [
            'lagerbestand'
      
        ]
        
        labels = {
            'lagerbestand': "Lagerbestand",
              
        }
        
        widgets = {
            
            'lagerbestand': forms.NumberInput(attrs={'class': 'form-control col-6'}),
            
        }   
class LagerortForm(forms.ModelForm):
    class Meta:
        model = Artikel
        fields = [
            'lagerort' 
            
        ]
        
        labels = {
            'lagerort': "Lagerort",
            
        }
        
        widgets = {
            
            
            'lagerort': forms.TextInput(attrs={'class': 'form-control col-6'}),
            
        }  




class LieferantenForm(forms.ModelForm):
    class Meta:
        model = Lieferanten
        fields = ['number','our_kundennumber','name', 'adresse', 'plz', 'ort','email']

        labels = {
            'number': "Lieferanten-Nr.:",
            'our_kundennumber' : "Unsere Kundennummer",
            'name': "Lieferant",
            'adresse': "Adresse",
            'plz': "PLZ",
            'ort': "Ort",
            'email' : "E-Mail"
        }

        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'our_kundennumber': forms.TextInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'our_kundennumber': forms.TextInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'adresse': forms.TextInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'plz': forms.TextInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'ort': forms.TextInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
        }


class CRMLagerBestandForm(forms.ModelForm):
    class Meta:
        model = CRMLager
        fields = ['lagerbestand']
        
        labels = {

            'lagerbestand': "Lagerbestand",

        }

        widgets = {
            
            
            'lagerbestand': forms.NumberInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            
        }

class CRMLagerForm(forms.ModelForm):
    class Meta:
        model = CRMLager
        fields = ['dichtungstyp','aussenbreite', 'aussenhöhe', 'lagerort', 'lagerbestand', 'marke']
        
        labels = {
            
            'aussenbreite': "Außenbreite (mm)",
            'aussenhöhe': "Außenhöhe (mm)",
            'dichtungstyp': "Dichtungstyp",
            'lagerort': "Lagerort",
            'lagerbestand': "Lagerbestand",
            'marke': "Marke(n)"
        }

        widgets = {
            
            'aussenbreite': forms.NumberInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'aussenhöhe': forms.NumberInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'dichtungstyp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
            'lagerort': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
            'lagerbestand': forms.NumberInput(attrs={
                'class': 'form-control col-6',
                'placeholder': ''
            }),
            'marke': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
        }





class CRMLastService(forms.ModelForm):
    class Meta:
        model = Kunde
        fields = ['last_service']  # Only allow the last_service field
        labels = {
            'last_service': "Letzter Service",
        }
        widgets = {
            'last_service': forms.DateInput(attrs={
                'class': 'form-control col-6',
                'type': 'date',  # This will generate an HTML5 date picker
                'placeholder': 'Wählen Sie ein Datum',
            }),
        }


class CRMKundeForm(forms.ModelForm):
    class Meta:
        model = Kunde
        fields = ['interne_nummer','firmenname', 'zusatz','done']
        labels = {
            'interne_nummer': "Interne Nummer",
            'firmenname': "Betrieb/Firma",
            'vorname': "Vorname",
            'nachname': "Nachname",
            'email': "E-Mail",
            'phone': "Telefon/Handy",
            'zusatz': "Zusatz",
            'done': 'Inventarisiert',
        }
        widgets = {
            'interne_nummer': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'vorname': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'nachname': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'email': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'firmenname': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'phone': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'zusatz': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'done': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left: 10px; margin-top: 7px;'}),
        }

# updated form for part-3
class CRMKundenForm(forms.ModelForm):

    class Meta:
        model = CRMAddress
        fields = (
            'crm_kanton',
        )
        labels = {
            'crm_kanton': "",
        }
        widgets = {
        'crm_kanton': forms.Select(attrs={
            'class': 'form-control col-15',
            'style': 'border-radius: 10px; padding: 10px; margin-top: 10px;'  # Add border-radius via inline CSS
        }),
}

# end of part-3


class CRMAddressForm(forms.ModelForm):
    class Meta:
        model = CRMAddress
        fields = (
            'crm_strasse',
            
            'crm_plz',
            'crm_ort',
            'crm_kanton',  # Dropdown for Kanton
        )
        labels = {
            'crm_strasse': "Adresse",
            'crm_nr': "Nr.",
            'crm_plz': "PLZ",
            'crm_ort': "Ort",
            'crm_kanton': "Kanton",
        }
        widgets = {
            'crm_strasse': forms.TextInput(attrs={
                'class': 'form-control col-6',
            }),
            'crm_nr': forms.TextInput(attrs={
                'class': 'form-control col-6',
            }),
            'crm_plz': forms.TextInput(attrs={
                'class': 'form-control col-6',
            }),
            'crm_ort': forms.TextInput(attrs={
                'class': 'form-control col-6',
            }),
            'crm_kanton': forms.Select(attrs={
                'class': 'form-control col-6',  # Dropdown for Kanton
            }),
        }



class CRMKundeRestForm(forms.ModelForm):
    class Meta:
        model = Kunde
        fields = ['vorname', 'nachname', 'phone','email',]
        labels = {
            'interne_nummer': "Interne-Nr.",
            'firmenname': "Betrieb/Firma",
            'vorname': "Vorname",
            'nachname': "Nachname",
            'email': "E-Mail",
            
            'phone': "Telefon/Handy",
            'zusatz': "Zusatz",
        }
        widgets = {
            'interne_nummer': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'vorname': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'nachname': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'email': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'firmenname': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'phone': forms.TextInput(attrs={'class': 'form-control col-6'}),
            'zusatz': forms.TextInput(attrs={'class': 'form-control col-6'}),
        }


class ElementeObjekteCreateForm(forms.ModelForm):
    class Meta:
        model = Objekte
        fields = ('name', 'serie', 'modell', 'typ','lieferant')
        labels = {
            'name': "Marke",
            'serie' : "Typ",
            'modell' : "Modell/Code",
            'typ' : "Serien-Nr.",
            'lieferant' : "Lieferant",
            
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
            'lieferant': forms.Select(attrs={
                'class': 'form-control col-6',  # Dropdown for Kanton
                
            }),
            
        }



class ProductMarkeLinkForm(forms.Form):
    item_marke = forms.ModelChoiceField(queryset=Marke.objects.all())



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
        fields = ('username', 'email', 'password', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control col-3',
                'placeholder': ''
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control col-3',
                'placeholder': ''
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control col-3',
                'placeholder': ''
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control col-3',
                'placeholder': ''
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control col-3',
                'placeholder': ''
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
    # KEINE Definition von 'password1' oder 'password2' hier! Allauth macht das.

    username = forms.CharField(
        max_length=500, required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': 'Benutzername', 'class': 'form-control'}),
        help_text='Bitte einen gültigen Benutzernamen eingeben'
    )
    first_name = forms.CharField(
        max_length=500, required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': 'Vorname', 'class': 'form-control'}),
        help_text='Bitte einen gültigen Vornamen eingeben'
    )
    last_name = forms.CharField(
        max_length=500, required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': 'Nachname', 'class': 'form-control'}),
        help_text='Bitte einen gültigen Nachnamen eingeben'
    )
    email = forms.EmailField( # Lassen Sie diese Definition, wenn Sie das label="" beibehalten wollen
        max_length=500, required=True, label="",
        widget=forms.EmailInput(attrs={'placeholder': 'E-Mail Adresse', 'class': 'form-control', 'type': 'email'}),
        help_text='Bitte eine gültige E-Mail Adresse eingeben'
    )
    firmenname = forms.CharField(
        max_length=500, required=False, label="",
        widget=forms.TextInput(attrs={'placeholder': 'Firmenname', 'class': 'form-control'})
    )
    strasse = forms.CharField(
        max_length=500, required=True, label="Adresse",
        widget=forms.TextInput(attrs={'placeholder': 'Strasse', 'class': 'form-control'}),
        help_text='Bitte eine gültige Strasse eingeben'
    )
    nr = forms.CharField(
        max_length=500, required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': 'Nr.', 'class': 'form-control'}),
        help_text='Bitte eine gültige Strassen-Nr. eingeben'
    )
    plz = forms.CharField(
        max_length=500, required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': 'PLZ', 'class': 'form-control'})
    )
    ort = forms.CharField(
        max_length=500, required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': 'Ort', 'class': 'form-control'}),
        help_text='Bitte einen gültigen Ort eingeben'
    )
    phone = forms.CharField(
        max_length=500, required=True, label="",
        widget=forms.TextInput(attrs={'placeholder': 'Telefon- oder Mobile-Nr.', 'class': 'form-control'}),
        help_text='Bitte eine gültige Telefon-Nr. eingeben'
    )
    mobile = forms.CharField(
        max_length=500, required=False, label="",
        widget=forms.TextInput(attrs={'placeholder': 'Mobile-Nr.', 'class': 'form-control'})
    )
    land = CountryField().formfield(
        required=True, # War im HTML als required markiert
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Bitte ein gültiges Land auswählen'
    )
    newsletter = forms.BooleanField(required=False, label="Newsletter")

    # NEU hinzugefügt, falls Sie diese verwenden wollen:
    CUSTOMER_TYPE_CHOICES = [
        ('privat', 'Privatkunde'),
        ('geschaeft', 'Geschäftskunde'),
        ('wieder', 'Wiederverkäufer'),
    ]
    customer_type = forms.ChoiceField(
        choices=CUSTOMER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Kundentyp *",
        required=True
    )

    hr_auszug = forms.FileField(
        label="Handelsregisterauszug hochladen",
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png'])],
        help_text="Nur PDF-, JPG- oder PNG-Dateien erlaubt."
    )


    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = ""
        
        # ANPASSUNG: Hier verwenden wir wieder 'password1' und 'password2'
        if 'password1' in self.fields:
            self.fields['password1'].label = "Passwort:"
            self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Passwort'})
        
        if 'password2' in self.fields:
            self.fields['password2'].label = "Passwort (wiederholen):"
            self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Passwort wiederholen'})

        # Initialisieren Sie hier auch die Platzhalter und Klassen für andere Felder,
        # falls dies nicht bereits in ihrer Definition geschieht und Sie es einheitlich möchten
        # Beispiel:
        # self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Benutzername'})
        # ... für alle anderen Felder, die Sie so anpassen möchten

    def signup(self, request, user):
        # ANPASSUNG: Hier die cleaned_data['password1'] verwenden
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])
        user.save()
        return user

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save() # User speichern, nachdem first/last_name gesetzt wurden

        try:
            kunde, created = Kunde.objects.get_or_create(user=user)
            kunde.firmenname = self.cleaned_data.get('firmenname', '') or 'Privatperson'
            kunde.newsletter = self.cleaned_data.get('newsletter', False)
            kunde.phone = self.cleaned_data['phone']
            kunde.mobile = self.cleaned_data.get('mobile', '')
            kunde.vorname = self.cleaned_data['first_name'] # Redundant, aber wenn Sie es brauchen
            kunde.nachname = self.cleaned_data['last_name'] # Redundant, aber wenn Sie es brauchen
            kunde.email = self.cleaned_data['email'] # Redundant, aber wenn Sie es brauchen
            kunde.rabatt = 0
            kunde.customer_type = self.cleaned_data['customer_type'] # Speichern des Kundentyps
            hr_auszug_file = self.cleaned_data.get('hr_auszug')
            if hr_auszug_file:
                kunde.hr_auszug = hr_auszug_file
            kunde.save()

            address = Address.objects.create(
                user=user,
                rechnung_strasse=self.cleaned_data['strasse'],
                rechnung_nr=self.cleaned_data['nr'],
                rechnung_ort=self.cleaned_data['ort'],
                rechnung_land=self.cleaned_data['land'],
                rechnung_plz=self.cleaned_data['plz'],
                address_type="B"
            )
            address.save()

            # E-Mail Versand-Logik (wie gehabt)
            # ...
            subject = 'Registration Neuer Kunde'
            template = render_to_string('shop/registration-email.html', {
                'firmenname': kunde.firmenname,
                'username': user.username, # Oder user.get_username()
                'phone': kunde.phone,
                'mobile': kunde.mobile,
                'plz': address.rechnung_plz,
                'ort': address.rechnung_ort,
                'email': user.email,
                'strasse': address.rechnung_strasse,
                'nr': address.rechnung_nr,
                'land': address.rechnung_land.name,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'customer_type': kunde.get_customer_type_display(), # Wichtig: get_customer_type_display() für den lesbaren Wert
                'hr_auszug_filename': kunde.hr_auszug.name if kunde.hr_auszug else None,
                'hr_auszug_url': kunde.hr_auszug.url if kunde.hr_auszug else None,
            })

            to_emails = ['livio.bonetta@geboshop.ch']
            bcc_emails = ['sandro@sh-digital.ch']

            email = EmailMessage(
                subject,
                template,
                'noreply@ihredomain.ch',
                to=to_emails,
                bcc=bcc_emails
            )
            email.content_subtype = "html"
            email.fail_silently = False
            email.send()

        except Exception as e:
            print(f"Error processing registration: {e}")
            raise

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
                'class': 'form-control',
                'placeholder':''}),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
            'password': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
            'date_joined': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly':'readonly'}),
        }

class KundeEditAdvancedForm(forms.ModelForm):
    class Meta:
        model = Kunde
        fields = (
            'interne_nummer',
            'firmenname',
            'rabatt',
            'newsletter',
            'phone',
            'mobile',
            'birthday'

            )
        labels = {
            'phone': "Telefon",
            
        }
        widgets = {
            
            'firmenname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
            'interne_nummer': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
            'rabatt': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
            'newsletter': forms.Select(attrs={
                'class': 'form-control',}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
            'birthday': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder':''}),
        }
    
class CRMKundeEditModelForm(forms.ModelForm):
    class Meta:
        model = Kunde
        fields = (
            'vorname',
            'nachname',
            'email',
            'interne_nummer',
            'firmenname',
            'rabatt',
            'phone',
            'mobile',
            'birthday'

            )
        labels = {
            'vorname': "Vorname",
            'nachname': "Nachname",
            'email': "E-Mail",
            'interne_nummer': "Nr.",
            'firmenname': "Firmenname",
            'rabatt': "Rabatt %",
            'phone': "Telefon",
            'mobile': "Mobile-Nr",
            'birthday': "Geburtsdatum"

            }
        widgets = {
        'vorname': forms.TextInput(attrs={
                'class': 'form-control col-3',
                'placeholder':''}),
        'nachname': forms.TextInput(attrs={
                'class': 'form-control col-3',
                'placeholder':''}),
        'email': forms.TextInput(attrs={
                'class': 'form-control col-3',
                'placeholder':''}),
            
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


class PVCForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            
            
            'artikelnr',
            'montage',
            'lieferung',
            'farbe',
            'preis', 
            'preis2', 
            'preis3', 
            
            'beschreibung',
            'titelbild', 
            'slug',
            'material', 
            
            'hersteller',

            
            
            )

        labels = {
            
            
            'artikelnr' : "Artikel-Nr z.B. 100",
            'lieferung' : "Lieferung",
            'montage' : "Typ z.B. geschraubt",
            'farbe' : "Farbe",
            'preis': "Preis 1 (bis 2m)", 
            'preis2': "Preis 2 (ab 2m)", 
            'preis3': "Preis 3 (ab 4m)", 
            'beschreibung' : "Bemerkung",
            'slug': "URL/Webadresse",
            'material': "Material z.B. PVC:",
            'hersteller': "Hersteller:",
        }

        widgets = {
            
       
            'kategorie': forms.Select(attrs={
                'class': 'form-control',
                }),
            'subkategorie': forms.Select(attrs={
                'class': 'form-control',
                }),

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

            
            'beschreibung': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder':''}),

            'titelbild' : forms.FileInput(attrs={
                'class': 'form-control',
                }),
            
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ''}),

          

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
            'bestseller',
        )
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
            'markepic': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'marketext': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': ''
            }),
            'bestseller': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'transform: scale(1.1); cursor: pointer;'
            }),
        }

          


# Bezeichnung   

class BezeichnungForm(forms.ModelForm):
    class Meta:
        model = Bezeichnung
        fields = ['name']
        labels = {
            'name': "Bezeichnung"
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control col-6',
                'placeholder': 'Bezeichnung eingeben'
            })
        }



class BestellungForm(forms.ModelForm):
    YES_NO_CHOICES = [
        (True, 'Ja'),
        (False, 'Nein'),
    ]

    montage = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Montage'
    )

    class Meta:
        model = Elemente_Bestellungen
        fields = ['montage', 'wer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['wer'].initial = 'lager'  # Set default choice

    def save(self, commit=False):
        instance = super().save(commit=False)
        if not instance.pk:
            instance.status = 'offen'
        return instance





