from django.shortcuts import render, redirect
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
#from django.views.generic import ListView
from .models import partNumber, pnCategory, BomElement, QtyReason, pnQty, elePrice
from .models import planerElement, partNote, bomDefine, purchaseList, mpList
from .models import customer, ccnList, software, endProduct, testlink
from django.db.models import Sum, F, Func
from .forms import uploadFileForm, createSoftwareForm, createCustomerForm, updateCustomerForm
from datetime import date
from django.http import FileResponse
#import csv

P_FINAN_LEVEL = 10

# Create your views here.
def erpindex(request):
	return render(request, 'erpindex.html')

def round(num):
	text = '%.2f'%float(num)
	new = float(text)
	return new

def viewPartNumber(request):
	category_list = pnCategory.objects.all().order_by('category')
	context = {'category_list':category_list}	 
	if 'pnKW' in request.GET:
		out = request.GET
		pnKW = out['pnKW']
		category = out['category']
		context.update({'category':category})
		package = out['package']
		context.update({'package':package})
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains = pnKW).order_by('name')
			if category != "ALL":
				cate = pnCategory.objects.get(category = category)
				partnumber_list = partnumber_list.filter(category = cate)
		elif category != "ALL":
			cate = pnCategory.objects.get(category = category)
			partnumber_list = partNumber.objects.filter(category = cate).order_by('name')
			#context.update({'partnumber_list':partnumber_list})
			if (category == 'C') or (category == 'R'):
				context.update({'show_package':'show_package'})
				if (package == '0402') or (package == '0603') or (package == '0805'):
					partnumber_list = partnumber_list.filter(name__contains = package)
				elif (package == 'other'):
					partnumber_list = partnumber_list.exclude(name__contains = '0402')
					partnumber_list = partnumber_list.exclude(name__contains = '0603')
					partnumber_list = partnumber_list.exclude(name__contains = '0805')
		else:
			context.update({'emptyKW':'emptyKW'})
			return render(request, 'viewPartNumber.html', context)

		outlist =[]
		for pt in partnumber_list:
			temp = pt.pnqty_set.aggregate(Sum('Qty'), Sum('untestQty'))
			curQty = temp.get('Qty__sum')
			utQty = temp.get('untestQty__sum')

			temp2 = pt.eleprice_set.order_by('-date')
			if temp2.count():
				price = temp2[0].price
			else:
				price = "None"

			if pt.buylink.find("http") == 0:
				buy_type = "http"
			else:
				buy_type = "text"

			outlist.append([pt.name, curQty, utQty, price, pt.location, pt.discription, pt.buylink, pt.Pid, buy_type])
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
		ptnote = partNote.objects.create(part = pt)
	category_list = pnCategory.objects.all().order_by('category')
	context = {'part':pt, 'ptnote':ptnote, 'cate':category_list }
	# print("["+str(pt.category)+"]")
	if request.POST:
		if request.user.is_authenticated:
			pt.user = request.user
			pt.date = date.today()
			if request.POST['location']:
				pt.location = request.POST['location']
			if request.POST['category']:
				cate = pnCategory.objects.get(category = request.POST['category'])
				pt.category = cate
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
	category_list = pnCategory.objects.values('category').order_by('category').distinct()
	context = {'category_list':category_list }
	if 'category' in request.POST:
		if request.user.is_authenticated:
			user = request.user
			category = request.POST['category'].upper()
			if (category == ''):
				context.update({'empty':'empty'})
				return render(request, 'addCategory.html', context)
			else:
				exist = pnCategory.objects.filter(category = category).count()
				if exist:
					context.update({'exist':'exist'})
					return render(request, 'addCategory.html', context)
				else:
					pnCategory.objects.create(category=category, user = user, date=date.today())
					context.update({'done':'done'})
					return render(request, 'addCategory.html', context)
	context.update({'failed':'failed'})
	return render(request, 'addCategory.html', context)

@login_required
def addPartNumber(request):
	category_list = pnCategory.objects.values('category').order_by('category').distinct()
	context = {'category_list':category_list }
	name = ""
	location = ""
	discription = ""
	link = ""
	if request.POST:
		if request.user.is_authenticated:
			user = request.user
			if request.POST['partNumber']:
				name = request.POST['partNumber']
			if request.POST['location']:
				location = request.POST['location']

			category = pnCategory.objects.get(category = request.POST['category'])
			level = request.POST['level']
			
			if request.POST['discription']:
				discription = request.POST['discription']
			if request.POST['link']:
				link = request.POST['link']

		if name == "":
			context.update({'nameEmpty':'nameEmpty'})
		elif location == "":
			context.update({'locationEmpty':'locationEmpty'})
		elif discription == "":
			context.update({'discriptionEmpty':'discriptionEmpty'})
		else:
			exist = partNumber.objects.filter(name__iexact = name).count()
			if exist:
				context.update({'nameExist':'nameExist'})
			else:
				partNumber.objects.create(name = name, location = location, level = level, \
				category = category, discription = discription, buylink = link, \
				user = user, date = date.today())
				context.update({'done':'ok'})

	return render(request, 'addPartNumber.html', context)

def viewBomList(request):
	partnumber_list = partNumber.objects.exclude(level = 0).order_by('name')
	if request.POST:
		productKW = request.POST['productKW']
		if productKW != "":
			partnumber_list = partnumber_list.filter(name__contains = productKW)

	context = {'partnumber_list':partnumber_list}
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
	product = partNumber.objects.get(Pid = Pid)
	context = {'pname':product.name}
	if request.POST:
		discription = request.POST['discription'].upper()
		if discription:
			if bomDefine.objects.filter(product=product).filter(discription = discription).count():
				context.update({'repeatDis':'repeatDis'})
				return render(request, 'newBomDefine.html', context)
			bomDefine.objects.create(product=product, discription = discription,\
				user = request.user, date = date.today())
			path = "/erp/BOM/"+str(product.Pid)+"/"
			return redirect(path)
		context.update({'emptyDisp':'emptyDisp'})
	return render(request, 'newBomDefine.html', context)

@login_required
def editBomList(request, Pid, Serial):
	product = partNumber.objects.get(Pid=Pid)
	bf = product.bomdefine_set.get(bomserial = Serial)
	element = bf.bomelement_set.all()
	total = element.count()
	context = {'bomdefine':bf}
	category_list = pnCategory.objects.all().order_by('category')
	context.update({'category_list':category_list})
	context.update({'total':total})
	if request.POST:
		if 'pnKW' in request.POST:
			out = request.POST
			pnKW = out['pnKW']
			cate = out['category']
			if pnKW !="":
				partnumber_list = partNumber.objects.filter(name__contains = pnKW)
				if cate != "ALL":
					cate = pnCategory.objects.get(category = out['category'])
					partnumber_list = partnumber_list.filter(category=cate)
				context.update({'partnumber_list':partnumber_list})
			elif cate !="ALL":
				cate = pnCategory.objects.get(category = out['category'])
				partnumber_list = partNumber.objects.filter(category=cate)
				context.update({'partnumber_list':partnumber_list})

	if ( total > 0 ):
		context.update({'element':element})
	
	return render(request, 'editBomList.html', context)

@login_required
def addElement(request, Pid, Serial, Bid):
	product = partNumber.objects.get(Pid=Pid)
	bf = bomDefine.objects.get(product=product, bomserial = Serial)
	part = partNumber.objects.get(Pid = Bid)
	#element = BomElement.objects.filter(bf = bf).filter(part=part)
	context = {'product':product}
	context.update({'part':part})
	context.update({'discription':bf.discription})
	element = bf.bomelement_set.filter(part=part)
	if element.count():
		element = element[0]
		context.update({'element':element})
		if request.POST:
			qty = request.POST['unitQty']
			schPN = request.POST['schPN']
			if (qty == ""):
				context.update({'empty':'empty'})
				return render(request, 'addElement.html', context)
			elif (qty == "0"):
				element.delete()
			else:
				element.unitQty = int(qty) 
				element.schPN = schPN
				element.user = request.user
				element.date = date.today()
				element.save()
			#path = '/erp/BOM/'+str(Pid)+'/'
			path = '/erp/BOM/'+str(Pid)+'/'+str(Serial)+'/'
			#print(path)
			#return redirect(path)
			return redirect(path)
		else:
			return render(request, 'addElement.html', context)
	elif request.POST:
		user = request.user
		qty = request.POST['unitQty']
		schPN = request.POST['schPN']
		if (qty == "") or (qty == "0"):
			context.update({'empty':'empty'})
			return render(request, 'addElement.html', context)
		else:
			BomElement.objects.create(bf = bf, part = part , \
				unitQty = qty, schPN =schPN, user = user, date=date.today())
			path = '/erp/BOM/'+str(Pid)+'/'+str(Serial)+'/'
			return redirect(path)
	else:
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
			context = {'done':'done'}
			done_list = []
			exist_list = []
			for row in rows:
				row = row.decode()
				out = row.split(';')
				len_of_out = len(out)
				p_name = out[0]
				if (len_of_out == 6) or (len_of_out == 11):
					exist = partNumber.objects.filter(name__iexact = p_name).count()
					if exist:
						context.update({'exist':'exist'})
						exist_list.append(p_name)
						context.update({'exist_list':exist_list})
					else:
						done_list.append(p_name)
						context.update({'done_list':done_list})
						new_cate = out[2].upper()
						cate, _ = pnCategory.objects.get_or_create(category = new_cate)

						pt = partNumber.objects.create(name = p_name, location = out[1], \
							category = cate, level = int(out[3]), discription = out[4], \
							buylink = out[5], date = today, user = user)
						if len(out) == 11:
							partNote.objects.create(part = pt, value = out[6], \
								package = out[7], addBuylink = out[8], param1 = out[9], param2 = out[10])
				elif (len_of_out > 1):
					context.update({'format':'format'})
			return render(request, 'uploadFaild.html', context)
		else:
			form = uploadFileForm()
	else:
		form = uploadFileForm()
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
			context = {'done':'done'}
			done_list = []
			nexist_list = []
			for row in rows:
				row = row.decode()
				out = row.split(';')
				len_of_out = len(out)
				if (len_of_out == 3):
					p_name = out[0]
					part = partNumber.objects.filter(name__iexact = p_name)
					if (part.count()):
						done_list.append(p_name)
						context.update({'done_list':done_list})
						part = part[0]
						element = BomElement.objects.create(bf = bf, part=part)
						element.unitQty = int(out[1])
						element.schPN = out[2]
						element.user = request.user
						element.date = date.today()
						element.save()
					else:
						context.update({'not_exist':'not_exist'})
						nexist_list.append(p_name)
						context.update({'nexist_list':nexist_list})
				elif (len_of_out > 1):
					context.update({'format':'format'})
			return render(request, 'uploadFaild.html', context)
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
		if priceset.count():
			price = float(priceset[0].price)
		else:
			price = 0

		subtotal = float(ele.unitQty*price)
		subtotal = round(subtotal)
		outlist.append([ele.part.name, price, ele.unitQty, subtotal])
		total = total+subtotal

	for subout in outlist:
		# print(subout)
		if total:
			ratio = "{:2.2f}".format(100*subout[3]/total)+"%"
			subout.append(ratio)
		else:
			subout.append('0%')
	# print(outlist)
	if len(outlist):
		total = round(total)
		outlist.append(["total","--","--",total,"100%"])
		context={'cost':outlist}
	else:
		context={'None':"None"}
	return render(request, 'cost.html', context)

def purchasing(request):
	category_list = pnCategory.objects.all().order_by('category')
	context = {'category_list':category_list}
	 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW = out['pnKW']
		cate = out['category']
		
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW).filter(level = 0)
			if cate != "ALL":
				cate = pnCategory.objects.get(category = out['category'])
				partnumber_list = partnumber_list.filter(category=cate).filter(level = 0)
			context.update({'partnumber_list':partnumber_list})
		elif cate !="ALL":
			cate = pnCategory.objects.get(category = out['category'])
			partnumber_list = partNumber.objects.filter(category=cate).filter(level = 0)
			context.update({'partnumber_list':partnumber_list})
		else:
			context.update({'emptyKW':'emptyKW'})
			return render(request, 'purchasing.html', context)

		if partnumber_list.count():
			outlist = []
			for pt in partnumber_list:
				temp = pt.pnqty_set.aggregate(Sum('Qty'))
				curQty = temp.get('Qty__sum')
				temp2 = pt.eleprice_set.order_by('-date')
				if temp2.count():
					temp2 = temp2[0]
					outlist.append([pt.name, curQty, pt.location, pt.discription, pt.Pid])
				else:
					outlist.append([pt.name, curQty, pt.location, pt.discription, pt.Pid])	
			context.update({'table': outlist})

	return render(request, 'purchasing.html', context)

@login_required
def addPurchasing(request, Pid):
	product = partNumber.objects.get(Pid=Pid)
	reason, _ = QtyReason.objects.get_or_create(reason="purchasing")
	user = request.user
	context = {'product':product}

	if request.POST:
		user = request.user
		qty = request.POST['qty']
		price = request.POST['price']

		if (qty == '') or (price == ''):
			return render(request, 'addPurchasing.html', context)
		else:
			if product.level == 0:
				pnQty.objects.create(partNumber = product, Qty = qty,\
					reason = reason, user = user, date = date.today())
			else:
				pnQty.objects.create(partNumber = product, Qty = qty,\
					reason = reason, user = user, date = date.today())
			price = round(price)
			elePrice.objects.create(partNumber = product, price = price, user = user, date= date.today() )
			return redirect('purchasing')

	return render(request, 'addPurchasing.html', context)

def discard(request):
	category_list = pnCategory.objects.all().order_by('category')
	context = {'category_list':category_list}
	 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW = out['pnKW']
		cate = out['category']

		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW)
			if cate != "ALL":
				cate = pnCategory.objects.get(category = out['category'])
				partnumber_list = partnumber_list.filter(category=cate)
		elif cate !="ALL":
			cate = pnCategory.objects.get(category = out['category'])
			partnumber_list = partNumber.objects.filter(category=cate)
		else:
			return render(request, 'discard.html', context)
		
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
	context = {'product':product}
	if request.POST:
		if request.POST['qty']:
			disQty = int(request.POST['qty']) #*(-1)
			temp = request.POST['reason']
			reason, _ = QtyReason.objects.get_or_create(reason=temp)
			pnQty.objects.create(partNumber = product, Qty = disQty,\
					reason = reason, user = user, date = date.today())
			return redirect('discard')
		else:
			context.update({'qtyError':'qtyError'})

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
		pnKW = out['pnKW']
		if pnKW !="":
			#partnumber_list = partNumber.objects.filter(name__contains= pnKW).exclude(planerelement__user=user).filter(level__gt=0)
			bf = bomDefine.objects.filter(product__name__contains = pnKW).filter(product__level__gt =0)
			# print(bf)
			context.update({'bf':bf})

	return render(request, 'planer.html', context)

@login_required
def addPlaner(request, bomserial):
	user = request.user
	bf = bomDefine.objects.get(bomserial = bomserial)
	# part=partNumber.objects.get(Pid=Pid)
	context = {'part':bf.product.name}
	context.update({'bf':bf.discription})
	# print(context)
	planer_list = planerElement.objects.filter(user = user).filter(bf__bomserial = bomserial)
	#print(planer_list)

	if planer_list.count():
		pl = planer_list[0]
		context.update({'planer':pl})
	else:
		pl = planerElement.objects.create(user = user)
		pl.bf = bf
		pl.save()
		context.update({'planer':pl})

	if request.POST:
		qty = request.POST['produceQty']
		#print("qty" = qty)
		if (qty == ""):
			context.update({'empty':'empty'})
			return render(request, 'addPlaner.html', context)
		elif (qty == "0"):
			pl.delete()
		else:
			pl.produceQty = int(qty)
			# print(pl)
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
	outlist = []
	for pl in plset:
		pdqty = pl.produceQty
		#pdproduct = pl.bf.product
		bomserial = pl.bf.bomserial 
		blset = bomDefine.objects.get(bomserial= bomserial).bomelement_set.all()
		#blset = pl.product.bomelement_set.all()
		total = blset.count()
		if (total > 0):
			for ele in blset:
				partP=partNumber.objects.get(Pid=ele.part.Pid).pnqty_set.aggregate(Sum('Qty'), Sum('untestQty'))
				curQty = partP.get('Qty__sum')
				utQty = partP.get('untestQty__sum')
				if curQty== None:
					curQty = 0
				ttpdqty = ele.unitQty*pdqty
				# buyqty = max(ttpdqty - curQty, 0)
				if ele.part.buylink.find("http") == 0:
					buy_type = "http"
				else:
					buy_type = "text"
				outlist.append([ele.part.name, ele.part.Pid, curQty, utQty, ttpdqty , 0 , ele.part.buylink, buy_type, ele.part.location] )

	total = len(outlist)
	context = {'total':total}

	if (total > 0):
		outlist = sorted(outlist, key = lambda l:l[1] )
		preid = -1
		i = 0
		outlist2 = []
		for temp in outlist:
			if temp[3] == None:
					temp[3] = 0 
			
			if temp[1] == preid:
				outlist2[i-1][3] = temp[3] + outlist2[i-1][3]
				outlist2[i-1][4] = temp[4] + outlist2[i-1][4]
			else:
				outlist2.append(temp)
				i=i+1
			
			preid = temp[1]
			outlist2[i-1][5] = max(outlist2[i-1][4]-outlist2[i-1][2], 0)
			
		context.update({'table':outlist2})
		return render(request,'pdCalculate.html', context)
	return render(request,'pdCalculate.html')

def PdRecord(request):
	#category_list = pnCategory.objects.all()

	cate= partNumber.objects.filter(level__gt=0).values_list('category', flat = True).distinct()
	category_list = pnCategory.objects.filter(id__in=cate)
	#filter(level__gt=0).select_related('category')
	# print(category_list)
	#category_list = pnCategory.objects..disinct()
	context = {'category_list':category_list}
	 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW = out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(level__gt=0).filter(name__contains= pnKW)
			if cate != "ALL":
				cate = pnCategory.objects.get(category = out['category'])
				partnumber_list = partnumber_list.filter(category=cate)
		elif cate !="ALL":
			cate = pnCategory.objects.get(category = out['category'])
			partnumber_list = partNumber.objects.filter(level__gt=0).filter(name__contains= pnKW).filter(category=cate)
		else:
			return render(request, 'pdRecord.html', context)
		
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
	reason, _ = QtyReason.objects.get_or_create(reason="production")
	context = {'bf':bf}
	cate, _ = pnCategory.objects.get_or_create(category ="PCBA")
	eleset = BomElement.objects.filter(bf__in= bf).filter(part__level__gt=0) # 檢查物料中有沒有level >=0
	pcbaCount = eleset.count()
	if pcbaCount: # 撈出有序號的產品 並且將網頁的Qty設成1
		endP = endProduct.objects.none()
		for ele in eleset:
			endP = endP | endProduct.objects.filter(part=ele.part).filter(status = "tested")
		
		context.update({'endProduct':endP})
		context.update({'lockQty':"lockQty"})
		# print(context)

	if request.POST:
		if not request.POST['serial']:
			context.update({'serialEmpty':'serialEmpty'})
			return render(request, 'addPdRecord.html', context)
		serial_start = int(request.POST['serial'])
		bomtype = request.POST.get('bomtype', "inside")
		# 產生新的endProduct  如果有子產品的話登錄子產品序號
		if pcbaCount:
			pdQty = 1
			selected = request.POST.getlist('checklist')
			for ele in eleset:
				bomQty = ele.unitQty
				inputQty = endProduct.objects.filter(part = ele.part).filter(serial__in= selected).count()
				if inputQty != bomQty:
					context.update({'serialNotMatch':'serialNotMatch'})
					return render(request, 'addPdRecord.html', context)
			ep = endProduct.objects.filter(serial = serial_start)
			if ep.count():
				context.update({'serial_exist':'serial_exist'})
				return render(request, 'addPdRecord.html', context)
			if bomtype=="inside":
				context.update({'selectBOM':'selectBOM'})
				return render(request, 'addPdRecord.html', context)

			mep =endProduct.objects.create(part = product,\
				serial = serial_start, mDate = date.today(), mUser = user)#新增母產品 但未設定bom
			
			for serial_number in selected: # 將子序號設定到母產品
				ep = endProduct.objects.get(serial = serial_number)
				ep.sDate = date.today()
				ep.sUser = user
				ep.status = "used"
				ep.save()
				mep.subProduct.add(ep)
			
			bf2 = bf.get(bomserial=int(bomtype))
			bomeleset = bf2.bomelement_set.all()
			totalcost = 0
			for ele in bomeleset:
				priceset = ele.part.eleprice_set.order_by('-date')
				if priceset.count():
					price = float(priceset[0].price)
				else:
					price = 0
				subtotal = float(ele.unitQty*price)
				totalcost = totalcost + subtotal
				consqty = ele.unitQty*(-1)
				pnQty.objects.create(partNumber = ele.part, Qty = consqty,\
				reason = reason, user = user, date = date.today())
			mep.bom = bf2
			totalcost = round(totalcost)
			elePrice.objects.create(partNumber=product, price = totalcost, user = user, date = date.today())				
			mep.save()
		else:
			pdQty = int(request.POST['qty'])
			if bomtype != "inside":
				bf2 = bf.get(bomserial=int(bomtype))
				bomeleset = bf2.bomelement_set.all()
				cost = request.POST['cost']
				if (cost == ''):
					cost = 0
					unitCost = 0
				else:
					manufactureCost = float(cost)
					unitCost = manufactureCost/float(pdQty)
				totalcost = unitCost
				for ele in bomeleset:
					priceset = ele.part.eleprice_set.order_by('-date')
					if priceset.count():
						price = float(priceset[0].price)
					else:
						price = 0
					subtotal = float(ele.unitQty*price)
					totalcost = totalcost +subtotal
					consqty = ele.unitQty*pdQty*(-1)
					pnQty.objects.create(partNumber = ele.part, Qty = consqty,\
					reason = reason, user = user, date = date.today())
				for i in range(pdQty): #設定產品但未指定bom
					ep = endProduct.objects.filter(serial = serial_start+i)
					if ep.count():
						context.update({'serial_exist':'serial_exist'})
						# print("exist")
						return render(request, 'addPdRecord.html', context)
					mep = endProduct.objects.create(part = product,\
							serial= serial_start+i, mUser = user, mDate = date.today(), bom = bf2)
				totalcost = round(totalcost)
				elePrice.objects.create(partNumber=product, price = totalcost, user = user, date = date.today())
			else:
				for i in range(pdQty): #設定產品但未指定bom
					ep = endProduct.objects.filter(serial = serial_start+i)
					if ep.count():
						context.update({'serial_exist':'serial_exist'})
						# print("exist")
						return render(request, 'addPdRecord.html', context)
					endProduct.objects.create(part = product,\
							serial= serial_start+i, mUser = user, mDate = date.today())

		pnQty.objects.create(partNumber = product, untestQty = pdQty,\
				Qty= 0, reason = reason, user = user, date = date.today())
	temp = product.pnqty_set.aggregate(Sum('Qty'), Sum('untestQty'))
	curQty = temp.get('Qty__sum')
	utQty = temp.get('untestQty__sum')
	pdinfo = [product.name, product.discription, curQty, utQty]
	context.update({'pdinfo':pdinfo})
	return render(request, 'addPdRecord.html', context)

@login_required
def uploadPO(request):
	form = uploadFileForm(request.POST, request.FILES)
	if request.POST:
		if form.is_valid():
			pocsv = request.FILES['file']
			user = request.user
			# print("UploadPO")
			data = pocsv.read()
			rows = data.split(b'\n')
			reason, _ = QtyReason.objects.get_or_create(reason='purchasing')
			context = {'done':'done'}
			done_list = []
			nexist_list = []
			for row in rows:
				row = row.decode()
				out = row.split(';')
				# print(out)
				len_of_out = len(out)
				if (len_of_out == 3):
					p_name = out[0]
					part = partNumber.objects.filter(name__iexact=p_name)
					if (part.count()):
						done_list.append(p_name)
						context.update({'done_list':done_list})
						part = part[0]
						ele = pnQty.objects.create(partNumber=part, reason = reason, Qty=int(out[1]), user = request.user, date = date.today())
						out_price = round(float(out[2]))
						price = elePrice.objects.create(partNumber = part, price = out_price, user = user, date= date.today() )
					else:
						context.update({'not_exist':'not_exist'})
						nexist_list.append(p_name)
						context.update({'nexist_list':nexist_list})
				elif (len_of_out > 1):
					context.update({'format':'format'})
			return render(request, 'uploadFaild.html', context)
		else:
			form = uploadFileForm()
	else:
		form = uploadFileForm()
	return render(request, 'uploadCSV.html', {'form':form})

def testRecord(request):
	cate= partNumber.objects.filter(level__gt=0).values_list('category', flat = True).distinct()
	category_list = pnCategory.objects.filter(id__in=cate)

	context = {'category_list':category_list}
	 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW = out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(level__gt=0).filter(name__contains= pnKW)
			if cate != "ALL":
				cate = pnCategory.objects.get(category = out['category'])
				partnumber_list = partnumber_list.filter(category=cate)
			
			context.update({'pd_list':partnumber_list})
	
		elif cate !="ALL":
			cate = pnCategory.objects.get(category = out['category'])
			partnumber_list = partNumber.objects.filter(level__gt=0).filter(name__contains= pnKW)
			context.update({'pd_list':partnumber_list})

	return render(request, 'testRecord.html', context)

@login_required
def addTestRecord(request, Pid):
	product = partNumber.objects.get(Pid=Pid)
	user = request.user
	reason, _ = QtyReason.objects.get_or_create(reason="testing")
	context = {'product':product}
	eptest = endProduct.objects.filter(part = product).filter(status = "tested")
	context.update({'eptest':eptest})
	epuntest = endProduct.objects.filter(part = product).filter(status = "untested")
	context.update({'epuntest':epuntest})
	pt_link = testlink.objects.filter(pn = product)
	if pt_link.count():
		print(pt_link[0].testurl)
		context.update({'testurl':pt_link[0].testurl})
	software = product.software.all()
	if software.count():
		context.update({'software':software})
	if request.POST:
		serial = int(request.POST.get('serial',"0"))
		if not serial:
			context.update({"serialEmpty":"serialEmpty"})
			return render(request, 'addTestRecord.html', context)
		ep = endProduct.objects.get(serial = serial)
		swlist = request.POST.getlist('software')
		if software.count() and len(swlist) == 0:
			context.update({"softwareEmpty":"softwareEmpty"})
			return render(request, 'addTestRecord.html', context)
		for sw in swlist:
			ep.software.add(sw)
		if serial:
			ep.tDate = date.today()
			ep.tUser = user

			if request.POST.get('result', "failed") == "passed":
				ep.status = "tested"
				pnQty.objects.create(partNumber = product, untestQty = -1,\
						Qty = 1, reason = reason, user = user, date = date.today())
				ep.save()
			else:
				failure = request.POST['reason']
				if (failure == ''):
					context.update({'ferror':'ferror'})
				else:
					ep.status = "discard"
					pnQty.objects.create(partNumber = product, untestQty = -1,\
						reason = reason, user = user, date = date.today())
					ccnList.objects.create(endp = ep, failure = failure, reqDate = date.today(), status = True  )
				ep.save()
		else:
			context.update({'error':'error'})

	return render(request, 'addTestRecord.html', context)

@login_required
def viewPurchaseList(request):
	category_list = pnCategory.objects.all().order_by('category')
	context = {'category_list':category_list} 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW = out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW).filter(level=0)
			if cate != "ALL":
				cate = pnCategory.objects.get(category = out['category'])
				partnumber_list = partnumber_list.filter(category=cate)
		elif cate !="ALL":
			cate = pnCategory.objects.get(category = out['category'])
			partnumber_list = partNumber.objects.filter(category=cate).filter(level=0)
		else:
			return render(request, 'purchaseList.html', context)
		# print(partnumber_list)
		outlist = []

		for pt in partnumber_list:
			temp = pt.pnqty_set.aggregate(Sum('Qty'), Sum('untestQty'))
			curQty = temp.get('Qty__sum')
			temp2 = pt.eleprice_set.order_by('-date')
			if temp2.count():
				temp2 = temp2[0]
				outlist.append([pt.name, pt.discription, pt.buylink,curQty,temp2.price, pt.location , pt.Pid])
			else:
				outlist.append([pt.name,  pt.discription, pt.buylink, curQty,"None", pt.location ,pt.Pid])
		
		context.update({'table': outlist})

	pl = purchaseList.objects.filter(status=True)
	outlist = []
	
	for pt in pl:
		outlist.append([pt.partNumber.name, pt.partNumber.discription, pt.partNumber.buylink, pt.Qty, pt.user, pt.reqDate, pt.plserial])
	
	context.update({'pl':outlist})
	return render(request, 'purchaseList.html', context)

@login_required
def addPurchaseList(request,Pid):
	product = partNumber.objects.get(Pid=Pid)
	context = {'product':product}
	user = request.user	
	if request.POST:
		Qty = int(request.POST['qty'])
		# print(Qty)
		purchaseList.objects.create(partNumber= product, Qty= Qty, user = user, reqDate = date.today(), status = True)
		return redirect('/erp/puraseList/')
	return render(request,'addPurchaseList.html', context)

def closePurchaseList(request, serial):
	pl = purchaseList.objects.get(plserial= serial)
	pl.status = False
	pl.closeDate = date.today()
	pl.save()
	return redirect('/erp/puraseList/')

def addSales(request, Pid):
	part = partNumber.objects.get(Pid = Pid)
	context = {'product':part}

	endp = endProduct.objects.filter(part = part).filter(status="tested")

	customer_list = customer.objects.all()
	
	context.update({'customer':customer_list})
	# print(context)
	context.update({'endp':endp})
	
	if endp.count():
		context.update({'serial':endp})
	if request.POST:
		serial = int(request.POST.get('serial','0'))
		if serial:
			name = request.POST['customer']
			cus = customer_list.get(name=name)
			endp = endp.get(serial = serial)
			endp.status= "sold"
			endp.sDate = date.today()
			endp.sUser = request.user
			endp.customer = cus 
			endp.save()
			reason = QtyReason.objects.get(reason="sold")
			pnQty.objects.create(partNumber = part, Qty= -1 \
						, reason = reason, user = request.user, date = date.today())
		else:
			context.update({'failed':'failed'})
	return render(request, 'addSales.html', context)

def viewMpList(request):
	cate= partNumber.objects.filter(level__gt=0).values_list('category', flat = True).distinct()
	category_list = pnCategory.objects.filter(id__in=cate)
	context = {'category_list':category_list} 
	if 'pnKW' in request.POST:
		out = request.POST
		pnKW = out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW).exclude(level=0)
			if cate != "ALL":
				cate = pnCategory.objects.get(category = out['category'])
				partnumber_list = partnumber_list.filter(category=cate)	
		elif cate !="ALL":
			cate = pnCategory.objects.get(category = out['category'])
			partnumber_list = partNumber.objects.filter(category=cate).exclude(level=0)
		else:
			return render(request, 'mpList.html', context)

		outlist =[]
		for pt in partnumber_list:
			temp=pt.pnqty_set.aggregate(Sum('Qty'), Sum('untestQty'))
			curQty = temp.get('Qty__sum')
			utQty = temp.get('untestQty')	
			outlist.append([pt.name, pt.discription, curQty, utQty , pt.location, pt.Pid])
		context.update({'table': outlist})
	pl = mpList.objects.filter(status=True)
	outlist =[]
	for part in pl:
		outlist.append([part.partNumber.name, part.partNumber.discription, part.Qty , part.customer, part.reqDate, part.mpSerial])
	context.update({'pl':outlist})
	return render(request, 'mpList.html', context)

def addMpList(request,Pid):
	customer_list = customer.objects.all()
	product = partNumber.objects.get(Pid=Pid)
	context = {'product':product}
	context.update({'customer_list':customer_list})
		
	if request.POST:
		cus = request.POST['customer']
		Qty = int(request.POST['qty'])
		if cus != 'None':
			user = customer_list.get(name = cus)
			mpList.objects.create(partNumber= product, Qty= Qty, customer = user, reqDate = date.today(), status = True)
		else:
			mpList.objects.create(partNumber= product, Qty= Qty, reqDate = date.today(), status = True)
		
		return redirect('/erp/mpList/')
	return render(request,'addMpList.html', context)

def closeMpList(request, serial):
	pl = mpList.objects.get(mpSerial= serial)
	pl.status = False
	pl.closeDate = date.today()
	pl.save()
	pid = pl.partNumber.Pid
	path = '/erp/production/'+str(pid)+'/'
	return redirect(path)

def viewCCNList(request):
	pl = ccnList.objects.filter(status=True)
	# print(pl)
	outlist = []
	context = {}
	for ccn in pl:
		if (ccn.endp != None):
			software = ccn.endp.software.all()
			outlist.append([ccn.endp.part.name, ccn.endp.customer, ccn.endp.serial,\
			software ,ccn.reqDate, ccn.failure, ccn.ccnSerial] )
		else:
			software = []
			software.append(ccn.software.name)
			outlist.append([None, None, None,\
			software, ccn.reqDate, ccn.failure, ccn.ccnSerial] )

	context.update({'pl':outlist})
	return render(request,'ccnList.html', context)

def addCCNList(request):
	# customer_list = customer.objects.all()
	# context = {'customer_list':customer_list}
	software_list = software.objects.filter(pc = True)
	context = {'software_list':software_list}

	if request.POST:
		# cus = request.POST['customer']
		serial = request.POST['serial']
		SwVer = request.POST['SwVer']
		failure = request.POST['failure']
		if (serial != ''):
			endp = endProduct.objects.filter(serial = serial)
			# user = customer_list.get(name = cus)
			if endp.count():
				endp = endp[0]
				ccnList.objects.create(endp = endp , failure = failure, \
					reqDate = date.today(), status = True)
			else:
				context.update({'cus_error':"cus_error"})
		elif (SwVer != ''):
			sw = software_list.get(name = SwVer)
			ccnList.objects.create(software = sw , failure = failure, \
				reqDate = date.today(), status = True)
		return redirect('/erp/ccnList/')
	return render(request,'addCCNList.html', context)

@login_required
def closeCCN(request, serial):
	pl = ccnList.objects.get(ccnSerial= serial)
	# context = {'ccn_list':pl}
	outlist = []
	if (pl.endp != None):
		outlist.append(pl.endp.part.name) 
		outlist.append(pl.endp.customer)
		outlist.append(pl.endp.serial)
	else:
		outlist.append(None) 
		outlist.append(None)
		outlist.append(None)
	outlist.append(pl.software)
	outlist.append(pl.reqDate)
	outlist.append(pl.failure) 
	outlist.append(pl.ccnSerial)
	context={'part':outlist}
	if request.POST:
		if request.user.is_authenticated:
			pl.rootCause = request.POST['rootCause']
			pl.status = False
			pl.closeDate = date.today()
			pl.closeEng = request.user
			pl.save()
			return redirect('/erp/ccnList')

	return render(request,'closeCCN.html', context)

def viewSoftware(request):
	category_list = pnCategory.objects.all().order_by('category')
	context = {'category_list':category_list} 
	if request.POST:
		out = request.POST
		pnKW = out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW).exclude(level=0)
			if cate != "ALL":
				cate = pnCategory.objects.get(category = out['category'])
				partnumber_list = partnumber_list.filter(category=cate)		
		elif cate !="ALL":
			cate = pnCategory.objects.get(category = out['category'])
			partnumber_list = partNumber.objects.filter(category=cate).exclude(level=0)
		else:
			return render(request,'viewSoftware.html', context)
		context.update({'partnumber_list': partnumber_list})
	return render(request,'viewSoftware.html', context)

def viewSales(request):
	category_list = pnCategory.objects.all().order_by('category')
	context = {'category_list':category_list} 
	if request.POST:
		out = request.POST
		pnKW = out['pnKW']
		cate = out['category']
		if pnKW !="":
			partnumber_list = partNumber.objects.filter(name__contains= pnKW).exclude(level=0)
			if cate != "ALL":
				cate = pnCategory.objects.get(category = out['category'])
				partnumber_list = partnumber_list.filter(category=cate)
		elif cate !="ALL":
			cate = pnCategory.objects.get(category = out['category'])
			partnumber_list = partNumber.objects.filter(category=cate).exclude(level=0)
		else:
			return render(request,'viewSales.html', context)
		context.update({'partnumber_list': partnumber_list})
	return render(request,'viewSales.html', context)


def addSoftware(request, Pid):
	part = partNumber.objects.get(Pid = Pid)
	context = {'part':part}
	sw_in_part = part.software.all()
	sw_out_part = software.objects.exclude(Sid__in = sw_in_part)
	if (part.level == 10):
		sw_out_part = sw_out_part.filter(pc = True)
	else:
		sw_out_part = sw_out_part.filter(pc = False)
	context.update({'sw_in_part':sw_in_part})
	context.update({'sw_out_part':sw_out_part})
	return render(request,'addSoftware.html', context)

def softwareToPd(request, Pid, Sid):
	part = partNumber.objects.get(Pid = Pid)
	sw = software.objects.get(Sid = Sid)
	part.software.add(sw)
	part.save()
	path = '/erp/software/'+str(Pid)+'/'
	return redirect(path)

def tracking(request):
	context = {}
	if request.POST:
		serial = request.POST['serial']
		if (serial != ''):
			serial = int(serial)
			endp = endProduct.objects.filter(serial = serial)
			if endp.count():
				endp = endp[0]
				context.update({'endp':endp})
				subplist = endp.subProduct.all()
				software = endp.software.all()
				if (endp.customer):
					customer = endp.customer.name
				fromsub = endProduct.objects.filter(subProduct=endp)
				# print(fromsub)
				context.update({'fromsub':fromsub })
				context.update({'subplist':subplist})
				context.update({'software':software})
				if (endp.customer):
					context.update({'customer':customer})

	return render(request, 'viewTracking.html', context)

def exportPartNumber(request):
	fp = open("partlist.csv","w")
	pnlist = partNumber.objects.all()
	for pn in pnlist:
		#名稱; 位置; 分類; 生產等級; 描述; 購買連結; 數值; 封裝; 第二購買連結;備註1; 備註2\n
		fp.write(pn.name +";"+ pn.location +";" + pn.category.category +";" +str(pn.level) +";" + pn.discription +";" + pn.buylink)
		pnNote = partNote.objects.filter(part = pn)
		if pnNote.count():
			pnNote = pnNote[0]
			if pnNote.value:
				value = pnNote.value
			else:
				value =""
			if pnNote.package:
				package = pnNote.package
			else:
				package =""
			if pnNote.addBuylink:
				addBuylink = pnNote.addBuylink
			else:
				addBuylink =""
			if pnNote.param1:
				param1 = pnNote.param1
			else:
				param1 =""
			if pnNote.param2:
				param2 = pnNote.param2
			else:
				param2 =""
			fp.write(";" + value + ";"+ package +";" + addBuylink +";" + param1 +";"+ param2 +"\n")
		else:
			fp.write(";;;;;\n")
	fp.close()
	fp = open("partlist.csv","rb")
	response = FileResponse(fp)
	return response

def exportBom(request, Pid, Serial):
	product = partNumber.objects.get(Pid=Pid)
	bf = bomDefine.objects.get(bomserial = Serial)
	element = bf.bomelement_set.all()
	fname = product.name +"_"+ bf.discription +".csv"
	fp = open(fname,"w")
	for ele in element:
		fp.write(ele.part.name+";" + str(ele.unitQty) +";"+ ele.schPN)
	fp.close()
	fp = open(fname,"rb")
	response = FileResponse(fp)
	return response

def createSoftware(request):
	template_name = 'createSoftware.html'
	form = createSoftwareForm(request.POST or None)

	context = {'form':form}
	context.update({'status':"add_new"})

	if form.is_valid():
		software.objects.create(name = form.cleaned_data.get('name'), \
			pc = form.cleaned_data.get('pc'), \
			discription = form.cleaned_data.get('discription'), \
			history = form.cleaned_data.get('history'))
		context.update({'status':"add_ok"})

	return render(request, template_name, context)

def createCustomer(request):
	template_name = 'createCustomer.html'
	form = createCustomerForm(request.POST or None)

	context = {'form':form}
	context.update({'status':"add_new"})

	if form.is_valid():
		customer.objects.create(name = form.cleaned_data.get('name'),\
			contact = form.cleaned_data.get('contact'),\
			vax = form.cleaned_data.get('vax') ,\
			email = form.cleaned_data.get('email'),\
			phone = form.cleaned_data.get('phone'),\
			mobile = form.cleaned_data.get('mobile'),\
			fax = form.cleaned_data.get('fax'),\
			add = form.cleaned_data.get('add'),\
			other = form.cleaned_data.get('other') )
		context.update({'status':"add_ok"})
	return render(request, template_name, context)

def viewCustomer(request):
	context = {}
	if request.POST:
		out = request.POST
		cn = out['customer']
		if cn !="":
			cus = customer.objects.filter(name__contains = cn)
			context.update({'customer_list':cus})
	return render(request, 'viewCustomer.html', context)

def editCustomer(request, cid):
	template_name = 'createCustomer.html'
	cus = customer.objects.get(cid = cid)
	cus_data = {'name':cus.name,'vax':cus.vax,'contact':cus.contact,'email':cus.email,\
	'phone':cus.phone,'mobile':cus.mobile,'fax':cus.fax,'add':cus.add,'other':cus.other}
	form = updateCustomerForm(initial = cus_data, data = request.POST or None)

	context = {'form':form}
	context.update({'status':"update_old"})

	if form.is_valid():
		cus.name = form.cleaned_data.get('name')
		cus.vax = form.cleaned_data.get('vax')
		cus.contact = form.cleaned_data.get('contact')
		cus.email = form.cleaned_data.get('email')
		cus.phone = form.cleaned_data.get('phone')
		cus.mobile = form.cleaned_data.get('mobile')
		cus.fax = form.cleaned_data.get('fax')
		cus.add = form.cleaned_data.get('add')
		cus.other = form.cleaned_data.get('other')
		cus.save()
		context.update({'status':"edit_ok"})
	return render(request, template_name, context)

def viewBomOfPart(request, Pid):
	template_name = 'viewBomOfPart.html'
	product = partNumber.objects.get(Pid = Pid)
	context = {'pname':product.name}
	element = BomElement.objects.filter(part = product)
	context.update({'element':element})
	return render(request, template_name, context)

def addTestLink(request):
	template_name = 'addTestLink.html'
	partNumber_list = partNumber.objects.filter(level__gt=0)
	context = {'pnlist':partNumber_list}

	if request.POST:
		pname = request.POST['partnumber']
		# print(pname)
		testurl = request.POST['testurl']
		# print(testurl)
		pt = partNumber.objects.get(name = pname)
		pt_link = testlink.objects.filter(pn = pt)
		if (pt_link.count() > 0):
			pt_link = testlink.objects.get(pn = pt)
			pt_link.testurl = testurl
			pt_link.save()
			context.update({'edit_done':'edit_done'})
		else:
			testlink.objects.create(pn = pt, testurl = testurl)
			context.update({'add_done':'add_done'})

	return render(request, template_name, context)

