from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_extensions.db.fields import AutoSlugField
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.utils.text import slugify

ADDRESS_CHOICES = (
    ('B', 'Rechnungsadresse'),
    ('S', 'Lieferadresse'),
)

PAYMENT_CHOICES = (
	('R', 'Rechnung*'),
	('V', 'Vorkasse (2% Skonto)'),
	)

CONDITION_CHOICES = (
	('G', 'Gebraucht'),
	('N', 'Neu')
	)


class MP_Category(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255)

	class Meta:
		ordering = ['id']
		verbose_name = 'MP_Kategorie'
		verbose_name_plural = 'MP_Kategorien'

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('home')

		
class Marketplace(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL,null=True, blank=True, on_delete=models.CASCADE)
	title = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255)
	price = models.FloatField(null=True, blank=True,)
	description = models.CharField(max_length=500, default='')
	condition = models.CharField(max_length=255, choices=CONDITION_CHOICES, default="G")
	place = models.CharField(max_length=255, null=True, blank=True)
	image = models.ImageField(null=True, blank=True, upload_to="inserate/")
	image1 = models.ImageField(null=True, blank=True, upload_to="inserate/")
	image2 = models.ImageField(null=True, blank=True, upload_to="inserate/")
	add_date = models.DateTimeField(auto_now_add=True)
	category = models.ForeignKey(MP_Category, related_name='mp_category', default=None, on_delete=models.SET_NULL, null=True, blank=True)
	is_active = models.BooleanField(default=False)

	class Meta:
		ordering = ['add_date']
		verbose_name = 'Marketplace'
		verbose_name_plural = 'Marketplaces'

	def mp_firmenname(self):
		if self.user.profile.firmenname:
			mp_firmenname = self.user.profile.firmenname
			return mp_firmenname 
		else:
			mp_firmenname = self.user.username 
			return mp_firmenname

	def save(self, *args, **kwargs):
		self.slug = slugify(self.title)
		super(Marketplace, self).save(*args, **kwargs)

	def __str__(self):
		return self.title


class Subcategory(models.Model):
	sub_name = models.CharField(max_length=255)
	sub_slug = models.SlugField(max_length=255)

	class Meta:
		ordering = ['sub_name']
		verbose_name = 'Subkategorie'
		verbose_name_plural = 'Subkategorien'

	def __str__(self):
		return self.sub_name


class Category(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255)
	categorypic = models.ImageField(null=True, blank=True, upload_to="produktbilder/")

	class Meta:
		ordering = ['id']
		verbose_name = 'Kategorie'
		verbose_name_plural = 'Kategorien'

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('home')


class Marke(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255)
	markepic = models.ImageField(null=True, blank=True, upload_to="markebilder/")
	marketext = models.TextField(blank=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Marke'
		verbose_name_plural = 'Marken'

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('home')



class Item(models.Model):
	titel = models.CharField(max_length=255)
	preis = models.FloatField()
	preis2 = models.FloatField(null=True, blank=True,)
	preis3 = models.FloatField(null=True, blank=True,)
	preis4 = models.FloatField(null=True, blank=True,)
	preis5 = models.FloatField(null=True, blank=True,)
	preis6 = models.FloatField(null=True, blank=True,)
	preis7 = models.FloatField(null=True, blank=True,)
	kurzbeschreibung = models.CharField(max_length=500, default='')
	beschreibung = models.CharField(max_length=500, default='')
	lieferung = models.CharField(max_length=255, null=True, blank=True,default="ca. 5 bis 7 Tage")
	montage = models.CharField(max_length=255, null=True, blank=True,)
	kategorie = models.ForeignKey(Category, default=1, on_delete=models.SET_NULL, null=True, blank=True)
	subkategorie = models.ForeignKey(Subcategory, default=None, on_delete=models.SET_NULL, null=True, blank=True)
	titelbild = models.ImageField(null=True, blank=True, upload_to="produktbilder/")
	slug = models.SlugField(max_length=255)
	artikelnr = models.CharField(max_length=255)
	farbe = models.CharField(max_length=255, null=True, blank=True,)
	nut = models.CharField(max_length=255, null=True, blank=True,)
	falz = models.CharField(max_length=255, null=True, blank=True,)
	falzluft = models.CharField(max_length=255, null=True, blank=True,)
	fuge = models.CharField(max_length=255, null=True, blank=True,)
	glasdicke = models.CharField(max_length=255, null=True, blank=True,)
	material = models.CharField(max_length=255, null=True, blank=True,)
	hersteller = models.CharField(max_length=255, null=True, blank=True,)
	sortierung = models.IntegerField(null=True, blank=True)
	marke = models.ForeignKey(Marke, related_name='item_marke', default=None, on_delete=models.SET_NULL, null=True, blank=True)

	class Meta:
		verbose_name = 'Produkte'
		verbose_name_plural = 'Produkte'
		ordering = ['sortierung']

	def __str__(self):
		return str(self.kategorie) + ' ' + str(self.subkategorie) + ' ' + str(self.artikelnr)

	def get_absolute_url(self):
		return reverse('store:pdescription', kwargs={"slug": self.slug})

	def get_remove_from_cart_url(self):
		return reverse('store:remove_from_cart', kwargs={"slug": self.slug})


class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	aussenbreite = models.IntegerField(null=True, blank=True, default=250)
	aussenhöhe = models.IntegerField(null=True, blank=True, default=250)
	element = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return f"{str(self.pk)} / {self.quantity} Stück von Artikel-Nr. {self.item.artikelnr} {self.item.titel} / AB {self.aussenbreite} AH {self.aussenhöhe} / CHF {self.item.preis} pro Stück"

	def get_add_to_cart_url(self):
		return reverse('store:add_to_cart', kwargs={"slug": self.item.slug, "pk": self.pk})

	def get_add_to_cart_url_myd(self):
		return reverse('store:add_to_cart_myd', kwargs={"slug": self.item.slug, "pk": self.pk})

	def get_laufmeter_total(self):
		return (self.aussenbreite * 2 / 1000) + (self.aussenhöhe * 2 / 1000)

	def get_stueck_price_gummi(self):
		if self.quantity >= 25:
			if self.quantity < 50:
				return self.item.preis2
			else:
				if self.quantity >= 50:
					if self.quantity < 100:
						return self.item.preis3
					else:
						if self.quantity >=100:
							if self.quantity < 200:
								return self.item.preis4
							else:
								if self.quantity >=200:
									if self.quantity < 500:
										return self.item.preis5
									else:
										if self.quantity >=500:
											return self.item.preis6
		else:
			return self.item.preis

	def get_stueck_price(self):
		if self.quantity >= 5:
			if self.quantity < 10:
				return self.item.preis2
			else:
				if self.quantity >= 10:
					if self.quantity < 25:
						return self.item.preis3
					else:
						if self.quantity >=25:
							if self.quantity < 50:
								return self.item.preis4
							else:
								if self.quantity >=50:
									return self.item.preis5
		else:
			return self.item.preis

	def get_meter_price(self):
		if self.quantity >= 25:
			if self.quantity < 50:
				return self.item.preis2
			else:
				if self.quantity >= 50:
					if self.quantity < 100:
						return self.item.preis3
					else:
						if self.quantity >=100:
							if self.quantity < 200:
								return self.item.preis4
							else:
								if self.quantity >=200:
									if self.quantity < 500:
										return self.item.preis5
									else:
										if self.quantity >=500:
											if self.quantity < 1000:
												return self.item.preis6
											else:
												if self.quantity >=1000:
													return self.item.preis7
											
		else:
			return self.item.preis

	def get_price(self):
		if self.item.kategorie.name == 'Weitere Dichtungen':
			if self.item.subkategorie.sub_name == 'Duschdichtungen':
				return self.get_stueck_price()
			else:
				return self.get_meter_price()

		else:
			if self.item.kategorie.name == 'Gummidichtung' or self.item.kategorie.name == 'EPDM/Moosgummi':
				return self.get_stueck_price_gummi()
			else:
				if self.get_laufmeter_total() >= 2:
					if self.get_laufmeter_total() < 4:
						return self.item.preis2
					else: 
						return self.item.preis3
				else:
					return self.item.preis	

	def get_total_pre(self):
		return self.quantity  * self.get_price()
	
	def get_total_item_price(self):
		return self.quantity  * self.get_price() * ((self.aussenbreite * 2 / 1000) + (self.aussenhöhe * 2 / 1000))

	def get_final_price(self):
		return self.get_total_item_price()

	def get_total_item_price_pvc(self):
		return self.get_total_item_price() / self.quantity

	def get_total_item_price_pvc_total(self):
		return self.get_total_item_price_pvc() * self.quantity 

class ShippingCost(models.Model):
	price_from = models.FloatField(null=True, blank=True,)
	price_to = models.FloatField(null=True, blank=True,)
	shipping_price = models.FloatField(null=True, blank=True,)

	def __str__(self):
		return 'Von CHF ' + str(self.price_from) + ' bis CHF ' + str(self.price_to) + ' Versand: CHF ' + str(self.shipping_price)

class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	items = models.ManyToManyField(OrderItem)
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	billing_address = models.ForeignKey(
		'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
	shipping_address = models.ForeignKey(
		'ShippingAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
	payment = models.BooleanField(default=False)
	payment_method = models.CharField(max_length=255, choices=PAYMENT_CHOICES, default="R")
	shippingcost = models.FloatField(null=True, blank=True,default=0)
	discount = models.FloatField(null=True, blank=True)
	discount_pct = models.FloatField(null=True, blank=True)
	skonto = models.FloatField(null=True, blank=True)
	pre_total = models.FloatField(null=True, blank=True)
	order_mwst = models.FloatField(null=True, blank=True)
	total = models.FloatField(null=True, blank=True)

	class Meta:
		verbose_name = 'Bestellung'
		verbose_name_plural = 'Bestellungen'

	def __str__(self):
		return self.user.username + ' ' + str(self.start_date) + ' ' + str(self.ordered)

	def get_payment_method(self):
		return [i[1] for i in Order._meta.get_field('payment_method').choices if i[0] == self.payment_method][0]

	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		return total

	def get_shipping(self):
		get_shipping = self.shippingcost
		return get_shipping

	def get_total_product_and_shipping(self):
		get_total_product_and_shipping = self.get_total()+ self.get_shipping()
		return get_total_product_and_shipping
	
	def get_total_pre_mwst_withoutskonto(self):
		get_total_pre_mwst_withoutskonto = self.get_total_product_and_shipping() - self.get_rabatt()
		return get_total_pre_mwst_withoutskonto

	def get_total_mwst_warenkorb(self):
		get_total_mwst_warenkorb = self.get_total_pre_mwst_withoutskonto() * 1.077
		return get_total_mwst_warenkorb

	def get_pre_mwst_warenkorb(self):
		get_pre_mwst_warenkorb = self.get_total_mwst_warenkorb() - self.get_total_pre_mwst_withoutskonto()
		return get_pre_mwst_warenkorb

	def get_skonto(self):
		if self.payment_method == 'V':
			skonto = 0.02
			get_skonto = skonto * self.get_total_pre_mwst_withoutskonto()
			return get_skonto
		else: 
			get_skonto = 0
			return get_skonto

	def rabatt(self):
		rabatt = self.user.profile.rabatt / 100
		return rabatt 

	def get_rabatt(self):
		rabatt = self.user.profile.rabatt
		get_rabatt = self.get_total() * self.rabatt()
		return get_rabatt

	def get_total_pre_mwst(self):
		get_total_pre_mwst = self.get_total_product_and_shipping() - self.get_rabatt() - self.get_skonto()
		return get_total_pre_mwst

	def mwst(self):
		mwst = self.grandtotal() - self.get_total_pre_mwst()
		return mwst

	def grandtotal(self):
		grandtotal = self.get_total_pre_mwst() * 1.077
		return grandtotal

class Address(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name ='address', on_delete=models.CASCADE)
	rechnung_strasse = models.CharField(max_length=255)
	rechnung_nr = models.CharField(max_length=255)
	rechnung_ort = models.CharField(max_length=255)
	rechnung_land = CountryField(multiple=False)
	rechnung_plz = models.CharField(max_length=255)
	address_type = models.CharField(max_length=500, choices=ADDRESS_CHOICES)

	class Meta:
		verbose_name = 'Rechnungsadresse'
		verbose_name_plural = 'Rechnungsadressen'

	def __str__(self):
		return self.user.username + ' ' + str(self.rechnung_strasse) + ' '+ str(self.rechnung_nr) + ', ' + str(self.rechnung_plz) + ' '+ str(self.rechnung_ort)


class ShippingAddress(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name ='shipping_address', on_delete=models.CASCADE)
	lieferung_strasse = models.CharField(max_length=255)
	lieferung_nr = models.CharField(max_length=255)
	lieferung_ort = models.CharField(max_length=255)
	lieferung_land = CountryField(multiple=False)
	lieferung_plz = models.CharField(max_length=255)
	address_type = models.CharField(max_length=500, choices=ADDRESS_CHOICES)
	vorname = models.CharField(max_length=255, null=True, blank=True)
	nachname = models.CharField(max_length=255, null=True, blank=True)
	firmenname = models.CharField(max_length=255, null=True, blank=True)

	class Meta:
		verbose_name = 'Lieferadresse'
		verbose_name_plural = 'Lieferadressen'

	def __str__(self):
		return self.user.username + ' ' + str(self.lieferung_strasse) + ' '+ str(self.lieferung_nr) + ', ' + str(self.lieferung_plz) + ' '+ str(self.lieferung_ort)


class Kunde(models.Model):
	user = models.OneToOneField(User, unique=True, related_name ='profile', on_delete=models.CASCADE)
	firmenname = models.CharField(max_length=255, null=True, blank=True)
	rabatt = models.FloatField(null=True, blank=True)
	newsletter = models.BooleanField(null=True, blank=True)
	mobile = models.CharField(max_length=255, null=True, blank=True) 
	phone = models.CharField(max_length=255, null=True, blank=True) 
	birthday = models.CharField(max_length=255, null=True, blank=True)
	interne_nummer = models.IntegerField(null=True, blank=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Kunde'
		verbose_name_plural = 'Kunden'

	def __str__(self):
		return self.firmenname

	def get_absolute_url(self):
		return reverse('store:cms_kunde_bearbeiten', kwargs={'pk': self.pk})

	def get_absolute_address_url(self):
		return reverse('store:cms_kundenadresse_bearbeiten', kwargs={'pk': self.pk})

	def get_absolute_elemente_url(self):
		return reverse('store:cms_elemente', kwargs={'pk': self.pk})


class Elemente(models.Model):
	dichtungen = models.ForeignKey(
		'Item', on_delete=models.SET_NULL, blank=True, null=True)
	elementnr = models.IntegerField(null=True, blank=True) 
	kuehlposition = models.CharField(max_length=255)
	bemerkung = models.CharField(max_length=255)
	kunde = models.ManyToManyField(Kunde, related_name='kunden_elemente', blank=True)
	aussenbreite = models.IntegerField(null=True, blank=True)
	aussenhöhe = models.IntegerField(null=True, blank=True)

	class Meta:
		ordering = ['elementnr']
		verbose_name = 'Element'
		verbose_name_plural = 'Elemente'

	def __str__(self):
		return str(self.kunde) + ' ' + self.kuehlposition + ' ' + self.bemerkung


