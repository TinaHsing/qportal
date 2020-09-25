from django.shortcuts import render, redirect
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
#from django.views.generic import ListView
from .models import partNumber, pnCategory, BomElement, QtyReason, pnQty, elePrice
from .models import planerElement
from django.db.models import Sum, F, Func
from .forms import uploadBom
from datetime import date

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
			
			context.update({'partnumber_list':partnumber_list})
			return render(request, 'viewPartNumber.html', context)
	
		elif cate !="ALL":
			partnumber_list = partNumber.objects.filter(category=cate)
			context.update({'partnumber_list':partnumber_list})
			return render(request, 'viewPartNumber.html', context)
		else:

			return render(request, 'viewPartNumber.html', context)

	else:
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
	print("hello~~")
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
	reason = reason = QtyReason.objects.get(reason="discard")
	context ={'product':product}
	if request.POST:
		disQty = int(request.POST['qty'])*(-1)
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
			if cate != "ALL":filter(category=cate)
			context.update({'pd_list':partnumber_list})

	return render(request, 'pdRecord.html', context)





