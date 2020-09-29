from django.shortcuts import render, redirect
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
#from django.views.generic import ListView
from .models import partNumber, pnCategory, BomElement, QtyReason, pnQty, elePrice
from .models import planerElement
from django.db.models import Sum, F, Func
from .forms import uploadBomForm
from datetime import date
import csv


# Create your views here.
def erpindex(request):
	return render(request, 'erpindex.html')

def viewPartNumber(request):
	category_list = partNumber.objects.values('category').distinct()
	#category_list = pnCategory.objects.all()
	#print(cate_list)
	context = {'category_list':category_list}
	 
	if 'pnKW' in request.GET:
		out = request.GET
		pnKW =out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW)
			if cate != "ALL":
				partnumber_list = partnumber_list.filter(category=cate)
			
			#context.update({'partnumber_list':partnumber_list})
			
	
		elif cate !="ALL":
			partnumber_list = partNumber.objects.filter(category=cate)
			#context.update({'partnumber_list':partnumber_list})
		outlist =[]
		for pt in partnumber_list:
			temp=pt.pnqty_set.aggregate(Sum('Qty'))
			curQty = temp.get('Qty__sum')
			outlist.append([pt.name, curQty, pt.location, pt.discription, pt.buylink])
		context.update({'table': outlist})
		print(outlist)
	
	return render(request, 'viewPartNumber.html', context)


@login_required
def addCategory(request):
	if 'category' in request.POST:
		if request.user.is_authenticated:
			user = request.user
			category = request.POST['category']
			pnCategory.objects.create(category=category, user = user, date=date.today())
			return render(request, 'addCategory.html', {'done':'ok'})	
	return render(request, 'addCategory.html',{'failed':'failed'})

@login_required
def addPartNumber(request):
	category_list = pnCategory.objects.values('category').distinct()
	context = {'category_list':category_list, 'failed':'failed' }
	name =""
	location =""
	discription=""
	link=""
	if request.POST:
		if request.user.is_authenticated:
			user = request.user
			if request.POST['partNumber']:
				name = request.POST.get('partNumber', False)
			
			if request.POST['location']:
				location = request.POST['location']

			category = request.POST['category']
			level = request.POST['level']
			
			if request.POST['discription']:
				discription = request.POST['discription']

			if request.POST['link']:
				link = request.POST['link']
		
		partNumber.objects.create(name = name, location = location, level = level, \
			category = category, discription = discription, buylink = link, \
			user = user, date = date.today())
		context = {'category_list':category_list, 'done':'ok' }

	return render(request, 'addPartNumber.html', context)

def viewBomList(request):
	partnumber_list = partNumber.objects.exclude(level =0)
	if request.POST:
		productKW = request.POST['productKW']
		if productKW != "":
			partnumber_list = partnumber_list.filter(name__contains = productKW)
			print(partnumber_list)
	context ={'partnumber_list':partnumber_list}
	return render(request, "viewBomList.html", context)	

@login_required
def editBomList(request, Pid):
	product = partNumber.objects.get(Pid=Pid)
	context ={'product':product}
	pnlevel = product.level

	
	category_list = partNumber.objects.values('category').distinct()
	context.update({'category_list':category_list})

	element = product.bomelement_set.all()
	if element.count() != 0:
		print(element)
		context.update({'element':element})

	if request.POST:
		if 'pnKW' in request.POST:
			out = request.POST
			pnKW =out['pnKW']
			cate = out['category']
			if pnKW !="":
				partnumber_list = partNumber.objects.filter(level__lt= pnlevel).filter(name__contains= pnKW)
				
				if cate != "ALL":
					partnumber_list = partnumber_list.filter(category=cate)
				
				context.update({'partnumber_list':partnumber_list})
	
			elif cate !="ALL":
				partnumber_list = partNumber.objects.filter(level__lt= pnlevel).filter(category=cate)
				context.update({'partnumber_list':partnumber_list})

	return render(request, 'editBomList.html', context)

@login_required
def addElement(request, Pid, Bid):
	product = partNumber.objects.get(Pid=Pid)
	part = partNumber.objects.get(Pid = Bid)
	element = BomElement.objects.filter(product = product).filter(part=part)
	print(element)
	context={'product':product}
	context.update({'part':part})
	#element = product.bomelement_set.filter(Bid = Bid)
	if element.count():
		element = BomElement.objects.filter(product = product).get(part= part)
		context.update({'element':element})
		print(context)
		if request.POST:
			qty = request.POST['unitQty']
			schPN = request.POST['schPN']
			if qty == "0":
				element.delete()
				print("delete")
			else:
				element.unitQty = qty 
				element.schPN = schPN
				print("save")
				element.save()
			path = '/erp/BOM/'+str(Pid)+'/'
			return redirect(path)

		return render(request, 'addElement.html', context)
	else:
		if request.POST:
			user = request.user
			qty = request.POST['unitQty']
			schPN = request.POST['schPN']
			BomElement.objects.create(product= product, part = part , \
				unitQty = qty, schPN =schPN, user = user, date=date.today())
			path = '/erp/BOM/'+str(Pid)+'/'
			return redirect(path)
	return render(request, 'addElement.html', context)

def uploadBom(request, Pid):
	if request.POST:
		product = partNumber.objects.get(Pid=Pid)
		form = uploadBomForm(request.POST, request.FILES)
		if form.is_valid():
			bom = request.FILES['file']
			BomElement.objects.filter(product=product).delete()
			#data = csv.reader(open(bom), delimiter=",")
			data = bom.read()
			rows = data.split(b'\n')
			print(rows)
			for row in rows:
				row = row.decode()
				out = row.split(',')

				part = partNumber.objects.filter(name=out[0])
				if part.count():
					element = BomElement.objects.create(product = product, part=part[0])
					element.unitQty = out[1]
					element.schPN = out[2]
					element.user = request.user
					element.date = date.today()
					element.save()
				else:
					return render(request, 'uploadFaild.html')
		else:
			form = uploadBomForm()
	else:
		form = uploadBomForm()
	return render(request, 'uploadCSV.html', {'form':form})

def purchasing(request):
	category_list = partNumber.objects.values('category').distinct()
	context = {'category_list':category_list}
	 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW =out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW)
			if cate != "ALL":
				partnumber_list = partnumber_list.filter(category=cate)
			
			context.update({'partnumber_list':partnumber_list})
	
		elif cate !="ALL":
			partnumber_list = partNumber.objects.filter(category=cate)
			context.update({'partnumber_list':partnumber_list})
			

	return render(request, 'purchasing.html', context)

@login_required
def addPurchasing(request, Pid):
	product = partNumber.objects.get(Pid=Pid)
	reason = QtyReason.objects.get(reason="purchasing")
	user = request.user
	if request.POST:
		user = request.user
		qty = request.POST['qty']
		price = request.POST['price']
		if product.level == 0:
			pnQty.objects.create(partNumber = product, Qty = qty,\
				reason = reason, user = user, date = date.today())
		else:
			pnQty.objects.create(partNumber = product, Qty = qty,\
				reason = reason, user = user, date = date.today())
		elePrice.objects.create(partNumber = product, price = price, user = user, date= date.today() )
		return redirect('purchasing')
	return render(request, 'addPurchasing.html')

def discard(request):
	category_list = partNumber.objects.values('category').distinct()
	context = {'category_list':category_list}
	 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW =out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW)
			if cate != "ALL":
				partnumber_list = partnumber_list.filter(category=cate)
			
			context.update({'partnumber_list':partnumber_list})
	
		elif cate !="ALL":
			partnumber_list = partNumber.objects.filter(category=cate)
			context.update({'partnumber_list':partnumber_list})

	return render(request, 'discard.html', context)

def addDiscard(request, Pid):
	product = partNumber.objects.get(Pid=Pid)
	
	user = request.user
	
	context ={'product':product}
	if request.POST:
		disQty = int(request.POST['qty'])*(-1)
		temp = request.POST['reason']
		reason = QtyReason.objects.get(reason=temp)
		pnQty.objects.create(partNumber = product, Qty = disQty,\
				reason = reason, user = user, date = date.today())
		
		return redirect('discard')

	return render(request, 'addDiscard.html',context)

@login_required
def planer(request):
	user = request.user
	planer_list = planerElement.objects.filter(user = user)
	#test = partNumber.objects.filter(planerelement__user = user)
	if planer_list.count():
		context = {'planer_list':planer_list}

	else:
		context = {'no_list': "no_list"}

	if request.POST:

		out = request.POST
		pnKW =out['pnKW']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW).exclude(planerelement__user=user).filter(level__gt=0)
			context.update({'partnumber_list':partnumber_list})
	return render(request, 'planer.html', context)
@login_required
def addPlaner(request, Pid):
	user=request.user
	part=partNumber.objects.get(Pid=Pid)
	context = {'part':part}
	planer_list = planerElement.objects.filter(user = user).filter(product__Pid=Pid)
	if planer_list.count():
		pl = planer_list[0]
		context.update({'planer':pl})
	else:
		pl = planerElement.objects.create(user = user, product = part)
	if request.POST:
		qty = request.POST['produceQty']
		#print("qty" = qty)
		if int(qty) == 0 :
			pl.delete()

		else:
			pl.produceQty = qty
			pl.save()

		plout = planerElement.objects.filter(user = user)
		context = {'planer_list':plout}
		path ='/erp/planer/'
		return redirect(path, context) 
	return render(request, 'addPlaner.html', context)

def PdCalculate(request):
	user = request.user
	plset = planerElement.objects.filter(user=user)
	pdtotal = BomElement.objects.none()
	outlist =[]
	for pl in plset:
		pdqty = pl.produceQty
		blset = pl.product.bomelement_set.all()
		for ele in blset:
			partP=partNumber.objects.get(Pid=ele.part.Pid).pnqty_set.aggregate(Sum('Qty'))
			curQty = partP.get('Qty__sum')
			if curQty== None:
				curQty = 0
			ttpdqty = ele.unitQty*pdqty
			buyqty = max(ttpdqty - curQty, 0) 
			outlist.append([ele.part.name, ele.part.Pid, curQty, ttpdqty , buyqty, ele.part.buylink] )
	outlist = sorted(outlist, key = lambda l:l[1] )
	preid = -1
	i = 0
	outlist2 =[]
	for temp in outlist:
		if temp[1] == preid:
			outlist2[i-1][3] = temp[3]+outlist2[i-1][3]
			outlist2[i-1][4] = temp[4]+outlist2[i-1][4
			]
		else:
			outlist2.append(temp)
		preid =temp[1]
		i=i+1
	context ={'table':outlist2}
	return render(request,'pdCalculate.html', context)

def PdRecord(request):
	category_list = partNumber.objects.values('category').distinct()
	context = {'category_list':category_list}
	 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW =out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(level__gt=0).filter(name__contains= pnKW)
			if cate != "ALL":
				partnumber_list = partnumber_list.filter(category=cate)
			
			context.update({'pd_list':partnumber_list})
	
		elif cate !="ALL":
			partnumber_list = partNumber.objects.filter(level__gt=0).filter(name__contains= pnKW)
			context.update({'pd_list':partnumber_list})

	return render(request, 'pdRecord.html', context)

def addPdRecord(request,Pid):
	product = partNumber.objects.get(Pid=Pid)
	user = request.user
	reason = QtyReason.objects.get(reason="production")
	context ={'product':product}
	if request.POST:
		pdQty = int(request.POST['qty'])
		inout = request.POST['inout']
		pnQty.objects.create(partNumber = product, Qty = pdQty,\
				reason = reason, user = user, date = date.today())
		if inout == "outside":
			bomeleset = BomElement.objects.filter(product = product)
			for ele in bomeleset:
				consqty = ele.unitQty*pdQty*(-1)
				pnQty.objects.create(partNumber = ele.part, Qty = consqty,\
				reason = reason, user = user, date = date.today())

	return render(request, 'addPdRecord.html', context)

def uploadPO(request):
	form = uploadBomForm()
	if form.is_valid():
		pocsv = request.FILES['file']
		data = pocsv.read()
		rows = data.split(b'\n')
		reason = QtyReason.objects.get(reason='purchasing')
		for row in rows:
			row = row.decode()
			out = row.split(',')
			part = partNumber.objects.filter(name=out[0])
			if part.count():
				ele = pnQty.objects.create(partNumber=part[0], reason = reason, Qty=int(out[1]), user = request.usr, data = data.today())
			else:
				return render(request, 'uploadFaild.html')
	return render(request, 'uploadCSV.html', {'form':form})
