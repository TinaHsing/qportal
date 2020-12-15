from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.urls import reverse
from django.db.models import Sum, F, Func
# Create your models here.

class pnCategory(models.Model):
	category = models.CharField(max_length = 10)
	user = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, blank=True)
	date = models.DateField(null = True, blank = True)
	def __str__(self):
		return self.category

class partNumber(models.Model):

	Pid = models.AutoField(primary_key=True)
	name = models.CharField(max_length = 80, help_text='check partNumber rule for detail')
	location = models.CharField(max_length = 15, blank = True, null =True)
	category = models.CharField(max_length = 10)
	level = models.PositiveIntegerField(default = 0)
	discription = models.TextField(help_text='must input key paramter discription here', null=True, blank = True)
	buylink = models.CharField(max_length = 200, help_text ='input the purchasing link', blank = True)
	date = models.DateField(null = True, blank = True) 
	user = models.ForeignKey(User, on_delete = models.SET_NULL, null = True, blank=True )
	def __str__(self):
		return self.name

class bomDefine(models.Model):
	product = models.ForeignKey(partNumber,on_delete = models.CASCADE, blank = True, null =True)	
	bomserial= models.AutoField(primary_key= True)
	discription = models.CharField(max_length = 100, blank=True, null= True)
	user = models.ForeignKey(User, on_delete = models.SET_NULL, null= True, blank = True)
	date = models.DateField(null=True, blank = True )

	def __str__(self):
		return self.product.name

class BomElement(models.Model):
	bf= models.ForeignKey(bomDefine, on_delete = models.CASCADE, blank = True, null =True) #bom belongs to what product
	part = models.ForeignKey(partNumber, related_name = "element", on_delete = models.CASCADE, blank = True, null =True)
	unitQty = models.IntegerField(default =1)
	schPN = models.CharField(max_length = 1000, blank=True, null= True)
	user = models.ForeignKey(User, on_delete = models.SET_NULL, null= True, blank = True)
	date = models.DateField(null=True, blank = True )
	def __str__(self):
		return self.part.name

class partNote(models.Model):
	part = models.ForeignKey(partNumber, on_delete= models.CASCADE, blank=True, null=True)
	value = models.CharField(max_length = 15, blank = True, null = True)
	package = models.CharField(max_length = 15, blank = True, null = True)
	param2 = models.CharField(max_length = 15, blank = True, null = True)
	addBuylink = models.CharField(max_length = 100, blank = True, null = True)
	param1 = models.CharField(max_length = 15, blank = True, null = True)
	def __str__(self):
		return self.part.name

class elePrice(models.Model):
	partNumber = models.ForeignKey(partNumber, on_delete = models.CASCADE, blank = True, null =True)
	price = models.DecimalField(max_digits = 6, decimal_places =2 )
	user = models.ForeignKey(User, on_delete = models.SET_NULL, null= True, blank = True)
	date = models.DateField(null=True, blank = True )
	def __str__(self):
		return self.partNumber.name

class QtyReason(models.Model):
	reason = models.CharField(max_length = 10, default = "purchasing")
	def __str__(self):
		return self.reason

class pnQty(models.Model):
	partNumber = models.ForeignKey(partNumber, on_delete = models.CASCADE, blank = True, null =True)
	Qty = models.IntegerField(default=0)
	reason = models.ForeignKey(QtyReason, on_delete = models.CASCADE, blank = True, null =True)
	user = models.ForeignKey(User, on_delete = models.SET_NULL, null= True, blank = True)
	date = models.DateField(null=True, blank = True )
	untestQty = models.IntegerField(default=0)
	def __str__(self):
		return self.partNumber.name

class planerElement(models.Model):
	user = models.ForeignKey(User, on_delete = models.SET_NULL, null= True, blank = True)
	bf = models.ForeignKey(bomDefine, on_delete = models.CASCADE, blank = True, null =True)
	produceQty = models.IntegerField(default = 1)

	def __str__(self):
		return self.user.username

class purchaseList(models.Model):
	plserial = models.AutoField(primary_key=True)
	partNumber = models.ForeignKey(partNumber, on_delete = models.CASCADE, blank = True, null =True)
	Qty = models.IntegerField(default = 0)
	user = models.ForeignKey(User,related_name="user", on_delete = models.SET_NULL, null= True, blank = True)
	reqDate = models.DateField(null=True, blank = True)
	status = models.BooleanField(default= True)
	closeDate = models.DateField(null=True, blank = True)
	def __str__(self):
		return self.partNumber.name

class customer(models.Model):
	cid = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 30)
	phone = models.CharField(max_length = 15)
	add = models.CharField(max_length = 60,null=True, blank = True)
	vax = models.CharField(max_length = 8 ,null=True, blank = True)
	def __str__(self):
		return self.name

class mpList(models.Model):
	mpSerial = models.AutoField(primary_key = True)
	partNumber = models.ForeignKey(partNumber, on_delete = models.CASCADE, blank = True, null =True)
	Qty = models.IntegerField(default = 0)
	customer = models.ForeignKey(customer, on_delete = models.CASCADE, blank = True, null =True)
	reqDate = models.DateField()
	status = models.BooleanField(default = True)
	closeDate = models.DateField(null=True, blank = True)
	def __str__(self):
		return self.partNumber.name


class ccnList(models.Model):
	ccnSerial = models.AutoField(primary_key = True)
	partNumber = models.ForeignKey(partNumber, on_delete = models.CASCADE, blank = True, null =True)
	serialNumber = models.CharField(max_length = 15)
	customer = models.ForeignKey(customer, on_delete = models.CASCADE, blank = True, null =True)
	reqDate =  models.DateField()
	status = models.BooleanField(default = True)
	failure = models.TextField(help_text='input failure phenomenon', null=True, blank = True)
	rootCause = models.TextField(help_text='input the rootCause of failure', null=True, blank = True)
	closeDate = models.DateField(null=True, blank = True)
	closeEng = models.ForeignKey(User, on_delete = models.SET_NULL, null= True, blank = True)
	def __str__(self):
		return self.partNumber.name

class software(models.Model):
	name = models.CharField(max_length = 15)
	discription = models.CharField(max_length = 100)
	history = models.TextField(help_text ='reversion history', null=True, blank = True)
	return self.name









	

