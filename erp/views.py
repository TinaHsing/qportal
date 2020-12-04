from django.shortcuts import render, redirect
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
#from django.views.generic import ListView
from .models import partNumber, pnCategory, BomElement, QtyReason, pnQty, elePrice
from .models import planerElement, partNote, bomDefine, purchaseList
from django.db.models import Sum, F, Func
from .forms import uploadFileForm
from datetime import date
import csv


# Create your views here.
def erpindex(request):
	return render(request, 'erpindex.html')

def viewPartNumber(request):
	category_list = partNumber.objects.values('category').distinct()
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
			temp=pt.pnqty_set.aggregate(Sum('Qty'), Sum('untestQty'))
			curQty = temp.get('Qty__sum')
			utQty = temp.get('untestQty__sum')
			temp2 = pt.eleprice_set.order_by('-date')
			if temp2.count():
				temp2 = temp2[0]
				outlist.append([pt.name, curQty, utQty, temp2.price, pt.location, pt.discription, pt.buylink, pt.Pid])
			else:
				outlist.append([pt.name, curQty, utQty, "None", pt.location, pt.discription, pt.buylink, pt.Pid])
		
		context.update({'table': outlist})
	
	return render(request, 'viewPartNumber.html', context)


@login_required
def editPartNumber(request, Pid):
	pt = partNumber.objects.get(Pid=Pid)
	#ptnote = partNote.objects.get_or_create(part = pt)
	ptnote = partNote.objects.filter(part = pt)
	if ptnote.count():
		ptnote = ptnote[0]
	else:
		ptnote=partNote.objects.create(part = pt)
	category_list = pnCategory.objects.all()
	context ={'part':pt, 'ptnote':ptnote, 'cate':category_list }
	if request.POST:
		if request.user.is_authenticated:
			pt.user = request.user
			pt.date = date.today()
			if request.POST['location']:
				pt.location = request.POST['location']
			if request.POST['category']:
				pt.category = request.POST['category']
			if request.POST['level']:
				pt.level = request.POST['level']
			if request.POST['discription']: 
				pt.discription = request.POST['discription']
			if request.POST['buylink']:
				pt.buylink = request.POST['buylink']
			if 'ptvalue'in request.POST:
				ptnote.value = request.POST['ptvalue']

			if request.POST['package']:
				ptnote.package = request.POST['package']
			if request.POST['param2']:
				ptnote.param2 = request.POST['param2']
			if request.POST['addBuylink']:
				ptnote.addBuylink = request.POST['addBuylink']
			if request.POST['param1']:
				ptnote.param1 = request.POST['param1']
			pt.save()
			ptnote.save()
		return redirect('viewPartNumber')
	return render(request, 'editPartNumber.html', context)
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
				name = request.POST['partNumber']
			
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

	context ={'partnumber_list':partnumber_list}
	return render(request, "viewBomList.html", context)	
def viewBomDefine(request, Pid):
	product = partNumber.objects.get(Pid = Pid)
	bomdefine = product.bomdefine_set.all().order_by('bomserial')
	index = bomdefine.count()
	context = {'product':product, 'index':index}
	if index:
		context.update({'bomdefine':bomdefine})

	return render(request, 'viewBomDefine.html', context)
@login_required
def newBomDefine(request, Pid):
	product = partNumber.objects.get(Pid= Pid)
	serial = product.bomdefine_set.all().count()
	if request.POST:
		discription = request.POST['discription']
		bomDefine.objects.create(product=product, bomserial=serial, discription = discription,\
			user = request.user, date = date.today())
		path = "/erp/BOM/"+str(product.Pid)+"/"
		return redirect(path)
	return render(request, 'newBomDefine.html')
@login_required
def editBomList(request, Pid, Serial):
	product = partNumber.objects.get(Pid=Pid)
	bf = product.bomdefine_set.get(bomserial = Serial)
	element = bf.bomelement_set.all()
	context = {'bomdefine':bf}
	category_list = partNumber.objects.values('category').distinct()
	context.update({'category_list':category_list})
	if request.POST:
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
				partnumber_list = partNumber.objects.filter(level__lt= pnlevel).filter(category=cate)
				context.update({'partnumber_list':partnumber_list})

	if element.count():
		context.update({'element':element})
	return render(request, 'editBomList.html', context)

@login_required
def addElement(request, Pid, Serial, Bid):
	product = partNumber.objects.get(Pid=Pid)
	bf = bomDefine.objects.get(product=product, bomserial = Serial)
	part = partNumber.objects.get(Pid = Bid)
	#element = BomElement.objects.filter(bf = bf).filter(part=part)
	context={'product':product}
	context.update({'part':part})
	element = bf.bomelement_set.filter(part=part)
	if element.count():
		element = element[0]
		context.update({'element':element})
		if request.POST:
			qty = request.POST['unitQty']
			schPN = request.POST['schPN']
			if qty == "0":
				element.delete()
				
			else:
				element.unitQty = qty 
				element.schPN = schPN
				element.user=request.user
				element.date= date.today()
				element.save()
			path = '/erp/BOM/'+str(Pid)+'/'
			return redirect(path)

		return render(request, 'addElement.html', context)
	else:
		if request.POST:
			user = request.user
			qty = request.POST['unitQty']
			schPN = request.POST['schPN']
			BomElement.objects.create(bf = bf, part = part , \
				unitQty = qty, schPN =schPN, user = user, date=date.today())
			path = '/erp/BOM/'+str(Pid)+'/'
			return redirect(path)
	return render(request, 'addElement.html', context)

@login_required
def uploadPart(request):
	if request.POST:
		user = request.user
		today = date.today()
		form = uploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			file = request.FILES['file']
			data = file.read()
			rows = data.split(b'\n')
			for row in rows:
				row=row.decode()
				out = row.split(';')
				if len(out) == 6 or len(out) == 12:
					pt=partNumber.objects.create(name=out[0], location = out[1], \
						category =out[2], level = int(out[3]), discription = out[4], \
						buylink = out[5], date = today, user = user)
					if len(out) == 12:
						partNote.objects.create(part=pt, value=out[7], \
							package=out[8], param2=out[9], addBuylink =out[10], param1 = out[11])
				return render(request, 'uploadFaild.html')
	else:
		form =uploadFileForm()
	return render(request,'uploadCSV.html',{'form':form})

@login_required	
def uploadBom(request, Pid, Serial):
	if request.POST:
		product = partNumber.objects.get(Pid=Pid)
		bf = bomDefine.objects.get(product = product, bomserial = Serial)
		form = uploadFileForm(request.POST, request.FILES)
		if form.is_valid():
			bom = request.FILES['file']
			BomElement.objects.filter(bf=bf).delete()
			data = bom.read()
			rows = data.split(b'\n')
			for row in rows:
				row = row.decode()
				out = row.split(';')
				part = partNumber.objects.filter(name=out[0])
				if part.count():
					element = BomElement.objects.create(bf = bf, part=part[0])
					element.unitQty = out[1]
					element.schPN = out[2]
					element.user = request.user
					element.date = date.today()
					element.save()
				else:
					return render(request, 'uploadFaild.html')
		else:
			form = uploadFileForm()
	else:
		form = uploadFileForm()
	return render(request, 'uploadCSV.html', {'form':form})

def costEvaluation(request, Pid, Serial):
	product = partNumber.objects.get(Pid=Pid)
	bf = bomDefine.objects.get(product = product, bomserial = Serial)
	eleset = bf.bomelement_set.all()
	outlist =[]
	total = 0
	for ele in eleset:
		priceset = ele.part.eleprice_set.order_by('-date')
		for pr in priceset:
			print (pr.price)
		if priceset.count():
			price = float(priceset[0].price)
		else:
			price = 0

		subtotal = float(ele.unitQty*price)
		outlist.append([ele.part.name, price, ele.unitQty, subtotal])
		total = total+subtotal

	for subout in outlist:
		print(subout)
		if total:
			
			ratio = "{:2.2f}".format(100*subout[3]/total)+"%"
			subout.append(ratio)
		else:

			subout.append('0%')
	print(outlist)
	if len(outlist):
		outlist.append(["total","--","--",total,"100%"])
		context={'cost':outlist}
	else:
		context={'None':"None"}
	return render(request, 'cost.html', context)

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
			
		elif cate !="ALL":
			partnumber_list = partNumber.objects.filter(category=cate)
		
		if partnumber_list.count():
			outlist = []
			for part in partnumber_list:
				temp=part.pnqty_set.aggregate(Sum('Qty'))
				curQty = temp.get('Qty__sum') 
				outlist.append([part.name, part.discription, curQty, part.Pid])

		context.update({'outlist':outlist})

	return render(request, 'discard.html', context)

@login_required
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
			#partnumber_list = partNumber.objects.filter(name__contains= pnKW).exclude(planerelement__user=user).filter(level__gt=0)
			bf = bomDefine.objects.filter(product__name__contains = pnKW).filter(product__level__gt =0)
			print(bf)
			context.update({'bf':bf})
	return render(request, 'planer.html', context)
@login_required
def addPlaner(request, bomserial):
	user=request.user
	bf = bomDefine.objects.get(bomserial = bomserial)
	#part=partNumber.objects.get(Pid=Pid)
	#context = {'part':part}
	planer_list = planerElement.objects.filter(user = user).filter(bf__bomserial = bomserial)
	#print(planer_list)
	
	if planer_list.count():
		pl = planer_list[0]
		context=({'planer':pl})
	else:
		pl = planerElement.objects.create(user = user)
		pl.bf = bf
		pl.save()
		context=({'planer':pl})
	if request.POST:
		qty = request.POST['produceQty']
		#print("qty" = qty)
		if int(qty) == 0 :
			pl.delete()

		else:
			pl.produceQty = qty
			print(pl)
			pl.save()

		plout = planerElement.objects.filter(user = user)
		context = {'planer_list':plout}
		path ='/erp/planer/'
		return redirect(path, context) 
	return render(request, 'addPlaner.html', context)
@login_required
def PdCalculate(request):
	user = request.user
	plset = planerElement.objects.filter(user=user)
	pdtotal = BomElement.objects.none()
	outlist =[]
	for pl in plset:
		pdqty = pl.produceQty
		pdproduct = pl.bf.product
		blset = bomDefine.objects.get(product = pdproduct).bomelement_set.all()
		#blset = pl.product.bomelement_set.all()
		if blset.count():
			for ele in blset:
				partP=partNumber.objects.get(Pid=ele.part.Pid).pnqty_set.aggregate(Sum('Qty'))
				curQty = partP.get('Qty__sum')
				if curQty== None:
					curQty = 0
				ttpdqty = ele.unitQty*pdqty
				buyqty = max(ttpdqty - curQty, 0) 
				outlist.append([ele.part.name, ele.part.Pid, curQty, ttpdqty , buyqty, ele.part.buylink] )
	if len(outlist):
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
	return render(request,'pdCalculate.html')

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
		elif cate !="ALL":
			partnumber_list = partNumber.objects.filter(level__gt=0).filter(name__contains= pnKW)
		
		if partnumber_list.count():
			outlist = []
			for part in partnumber_list:
				temp=part.pnqty_set.aggregate(Sum('Qty'),Sum('untestQty'))
				curQty = temp.get('Qty__sum') 
				untestedQty = temp.get('untestQty__sum')
				outlist.append([part.name, part.discription, curQty,untestedQty, part.Pid])

		context.update({'pd_list':outlist})

	return render(request, 'pdRecord.html', context)
@login_required
def addPdRecord(request,Pid):
	product = partNumber.objects.get(Pid=Pid)
	bf = bomDefine.objects.filter(product = product)
	user = request.user
	reason = QtyReason.objects.get(reason="production")
	context ={'bf':bf}
	if request.POST:
		pdQty = int(request.POST['qty'])
		bomtype = request.POST.get('bomtype', "inside")
		pnQty.objects.create(partNumber = product, untestQty = pdQty,\
				Qty= 0, reason = reason, user = user, date = date.today())
		if bomtype != "inside":
			bf2 = bf.get(bomserial=int(bomtype))
			bomeleset = bf2.bomelement_set.all()
			for ele in bomeleset:
				consqty = ele.unitQty*pdQty*(-1)
				pnQty.objects.create(partNumber = ele.part, Qty = consqty,\
				reason = reason, user = user, date = date.today())
	return render(request, 'addPdRecord.html', context)
@login_required
def uploadPO(request):
	form = uploadFileForm()
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

def testRecord(request):
	category_list = partNumber.objects.values('category').distinct()
	print(category_list)
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

	return render(request, 'testRecord.html', context)

@login_required
def addTestRecord(request, Pid):
	product = partNumber.objects.get(Pid=Pid)
	user = request.user
	reason = QtyReason.objects.get(reason="testing")
	context ={'product':product}
	if request.POST:
		Qty = int(request.POST['qty'])
		pnQty.objects.create(partNumber = product, untestQty = ((-1)*Qty),\
				Qty= Qty, reason = reason, user = user, date = date.today())
	return render(request, 'addTestRecord.html', context)

@login_required
def viewPurchaseList(request):
	category_list = partNumber.objects.values('category').distinct()
	context = {'category_list':category_list} 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW =out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW).filter(level=0)
			if cate != "ALL":
				partnumber_list = partnumber_list.filter(category=cate)
			
		elif cate !="ALL":
			partnumber_list = partNumber.objects.filter(category=cate).filter(level=0)
			
		print(partnumber_list)
		outlist =[]
		for pt in partnumber_list:
			temp=pt.pnqty_set.aggregate(Sum('Qty'), Sum('untestQty'))
			curQty = temp.get('Qty__sum')
			temp2 = pt.eleprice_set.order_by('-date')
			if temp2.count():
				temp2 = temp2[0]
				outlist.append([pt.name, curQty,temp2.price, pt.location, pt.discription, pt.Pid])
			else:
				outlist.append([pt.name, curQty,"None", pt.location, pt.discription ,pt.Pid])
		
		context.update({'table': outlist})
	pl = purchaseList.objects.filter(status=True)
	context.update({'pl':pl})
	return render(request, 'purchaseList.html', context)


def addPurchaseList(request,Pid):
	product = partNumber.objects.get(Pid=Pid)
	context ={'product':product}
	user = request.user	
	if request.POST:
		print("hi")
		Qty = int(request.POST['qty'])
		print(Qty)
		purchaseList.objects.create(partNumber= product, Qty= Qty, user = user, reqDate = date.today(), status = True)
		return redirect('/erp/puraseList/')
	return render(request,'addPurchaseList.html', context)

def closePurchaseList(request, serial):
	pl = purchaseList.objects.get(plserial= serial)
	pl.status = False
	pl.save()
	return redirect('/erp/puraseList/')