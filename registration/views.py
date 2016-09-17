from django.forms import forms
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
# Create your views here.
from .forms import RegForm, LogForm, RestaurantForm, FoodForm
from django.contrib import messages
import json
from django.db import connection
import datetime
from .models import Register, Restaurant, FoodItems, Order
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q,Count
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from rpy2.robjects import r
from django.contrib.auth.hashers import make_password
import rpy2.robjects as robjects
from rpy2.robjects import *


def index(request):
    #html= "<html><body><a href=\"reg/\">register</a><br/><a href=\"login/0\">login</a></body></html>"
    return render(request, 'registration/index.html')
def register(request):
    if request.method == "POST":
        form = RegForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if Register.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return redirect(reverse('register'))
            form.save()
            return HttpResponseRedirect("../login/0/")
        else:
            return HttpResponse("Invalid")
    else:
        form = RegForm()
        return render(request, 'registration/register.html',{'form': form})

def login(request, logged_in):
    if logged_in == '1':
        try:
            del request.session['user_id']
        except KeyError:
            pass
    if request.method == "POST":
        form = LogForm(request.POST)
        if form.is_valid():
            uname = form.cleaned_data['uname']
            passw = form.cleaned_data['passw']
            try:
                obj = Register.objects.get(username=uname)
            except Register.DoesNotExist:
                error = "invalid user"
                return render(request, 'registration/login.html', {'error': error, 'form':form})
            if obj.password == passw:
                request.session['user_id'] = obj.id
                request.session['typeofuser'] = obj.typeofuser
                return HttpResponseRedirect('http://127.0.0.1:8000/main/content')
            else:
                error = "pass wrong"
                return render(request, 'registration/login.html', {'error': error, 'form':form})

        else:
            error= "empty fields"
            return render(request, 'registration/login.html',{'error': error,'form':form})
    else:
        if logged_in == '1':
            logged_out_message = "You have logged out"
        else:
            logged_out_message=""
        form = LogForm()
        return render(request, 'registration/login.html',{'logged_out_message': logged_out_message,'logged_in': logged_in, 'form': form})

def content(request):
        if 'user_id' not in request.session:
            return HttpResponseRedirect('http://127.0.0.1:8000/main/login/0')
        session_id = request.session['user_id']
        user = Register.objects.get(pk = session_id)
        typeofuser = user.typeofuser
        if(typeofuser):
            first_time_logged_in = user.first_time_logged_in
            if first_time_logged_in == 1:
                return HttpResponseRedirect('http://127.0.0.1:8000/main/dashboard')
            if request.method == "POST":
                form = RestaurantForm(request.POST)
                if form.is_valid:
                    x = form.save(commit=False)
                    owner_id = request.session['user_id']
                    x.owner_id = owner_id
                    ip_address = get_client_ip(request)
                    x.ip = ip_address
                    x.save()
                    user.first_time_logged_in = 1
                    user.save()
                    return HttpResponseRedirect('http://127.0.0.1:8000/main/dashboard')
                else:
                    error= "empty fields"
                    return render(request, 'registration/content.html',{'error': error,'form':form})
            else:
                form = RestaurantForm()
                return render(request, 'registration/content.html',{'form': form})
        else:
            return HttpResponseRedirect('http://127.0.0.1:8000/main/dashboard')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def dashboard(request):
    if 'user_id' not in request.session:
        return HttpResponseRedirect('../login/0/')
    session_id = request.session['user_id']
    user = Register.objects.get(pk = session_id)
    typeofuser = user.typeofuser
    firstname = user.firstname
    if (typeofuser):
        message = "Owner"
        msg=""
        if request.method =="POST":
            form = FoodForm(request.POST, request.FILES)
            if form.is_valid():
                cat = form.cleaned_data['category']
                time = form.cleaned_data['time']
                prep = form.cleaned_data['preparation']
                cont = form.cleaned_data['content']
                x = form.save(commit=False)
                rest_id = request.session['user_id']
                x.category = cat.category
                x.time = time.time
                x.preparation = prep.preparation
                x.content = cont.content
                x.rest_id = rest_id
                x.save()
                msg="Thanks! Add another"
                return redirect(reverse('dashboard'),{'msg':msg})
            else:
                return redirect(reverse('dashboard'))
        else:
            form = FoodForm()
            return render(request, 'registration/dashboard.html',{'message': message, 'typeofuser': typeofuser, 'firstname': firstname, 'form':form, 'session_id': session_id},)

    else:
        message = "Customer"
        return render(request, 'registration/dashboard.html',{'typeofuser': typeofuser, 'firstname':firstname})


def get_restaurant(request):
   term = request.GET.get('term')
   bslk = Restaurant.objects.filter(name__icontains=term)
   res = []
   for b in bslk:
       dict = {'id':b.id, 'label':b.name, 'value':b.name}
       res.append(dict)
   return HttpResponse(json.dumps(res),'application/json')

def table(request):

    rest_name= request.POST.get("tags","")
    try:
        rest_id = Restaurant.objects.get(name= rest_name).owner_id
        request.session['rest_id_customer_is_in']=rest_id           #used for the view curr_order
    except Restaurant.DoesNotExist:
        error = "Soory! No restaurant found!"
        return redirect(reverse('dashboard'),{'error': error})
    return render(request,'registration/table.html',{'res':rest_id})

def menu(request):
    if request.method == "POST":
        t_num= request.POST.get("tnum","")
        rest_id=request.session['rest_id_customer_is_in']
        request.session['table_num']=t_num
        menu = FoodItems.objects.filter(rest_id=rest_id)







                # recommending favourite food
        # get highest rating
        # find food items with that rating with that user_id in that rest_id
        # if food items>1 select food with max count
        # if food_item category is bread divide its count by 2 to maintain ratio
        # if more than one food items have max count then if one of them is bread don't choose that
        user_id=request.session['user_id']
        uname = Register.objects.get(id=user_id).firstname
        q=Order.objects.filter(user_id=user_id).filter(rest_id=rest_id).values_list('rating')
        if not q:
            norec = "Sorry! No recommendation found. Try ordering food first."
            first_time = True
            return render(request,'registration/menucard.html',{'menu':menu,'norec':norec,'first_time':first_time})
        else:
            first_time = False
            x= max(q)
            ratio_maintainer = FoodItems.objects.filter(Q(category__icontains="Bread") | Q(category__icontains="Snack")).filter(rest_id=rest_id).values_list('name')
            bla = [l[0] for l in ratio_maintainer] #strip brackets
            for y in x:
                max_rating=y
            food_counter={}
            food_items=[]
            recommend=[]
            q=Order.objects.filter(user_id=user_id).filter(rest_id=rest_id).filter(rating=max_rating)
            for p in q:
                food_items.append(p.food_item)

            if len(set(food_items)) <= 1:
                recommend.append(food_items[0])
            else:
                i=0
                for food in food_items:
                    if food in food_counter:
                        food_counter[food]+=1
                    else:
                        food_counter[food]=1
                for x in ratio_maintainer:
                    if x in food_counter:
                        food_counter[x]=food_counter[x]/2
                recommend = sorted(food_counter, key = food_counter.get, reverse = True)

            #Top selling
            i=0
            temp=0
            j=0
            counter=0
            count= Order.objects.filter(rest_id=rest_id).values('food_item').annotate(fcount=Count('food_item'))
            quantities=[d['fcount'] for d in count]
            foods = [d['food_item'] for d in count]
            for x in bla:
                for y in foods:
                    if x==y:
                        quantities[i]=quantities[i]/2
                        counter+=1
                    i+=1
                i=0
            i=0
            for quantity in quantities:
                if quantity>temp:
                    temp=quantity
                    j=i
                i=i+1
            valj=j
            # Top selling based on time
            i=0
            temp=0
            j=0
            counter=0
            img_time= None
            com_time = None
            print_breakfast = None
            message=""
            time = datetime.now().time()
            curr_time = time
            breakfast=[]
            lunch=[]
            snacks=[]
            dinner=[]
            breakfast.append(time.replace(hour=7, minute=0, second=0, microsecond=0))
            breakfast.append(time.replace(hour=10, minute=30, second=0, microsecond=0))
            lunch.append(time.replace(hour=12, minute=30, second=0, microsecond=0))
            lunch.append(time.replace(hour=15, minute=30, second=0, microsecond=0))
            snacks.append(time.replace(hour=16, minute=0, second=0, microsecond=0))
            snacks.append(time.replace(hour=18, minute=0, second=0, microsecond=0))
            dinner.append(time.replace(hour=20, minute=0, second=0, microsecond=0))
            dinner.append(time.replace(hour=23, minute=0, second=0, microsecond=0))

            cursor=connection.cursor()
            cursor.execute('''SELECT registration_order.food_item, registration_fooditems.time FROM registration_order LEFT JOIN registration_fooditems ON registration_order.food_item = registration_fooditems.name WHERE registration_order.rest_id=%s AND registration_fooditems.rest_id=%s''', [rest_id,rest_id])
            all=cursor.fetchall()
            time_cat= dict(all)
            if (curr_time>=breakfast[0]) and (curr_time <= breakfast[1]):
                print_key = "Breakfast"
                time_list=[]
                for key, value in time_cat.items():
                    if 'Breakfast' == value:
                        time_list.append(key)
                boo=[]
                i=0
                for values in time_list:
                    boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
                    if values in bla:
                        boo[i]=boo[i]/2
                    i+=1
                if boo:
                    count= max(boo)
                    dictionary = dict(zip(time_list, boo))
                    for key, values in dictionary.items():
                        if values == count:
                            print_breakfast=key
                    img_time=FoodItems.objects.get(name=print_breakfast).image
                    com_time=FoodItems.objects.get(name=print_breakfast).comment
                else:
                    message = "No breakfast found"

            elif (curr_time>=lunch[0]) and (curr_time<=lunch[1]):
                print_key = "Lunch"
                time_list=[]
                for key, value in time_cat.items():
                    if 'Lunch' == value:
                        time_list.append(key)
                boo=[]
                i=0
                for values in time_list:
                    boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
                    if values in bla:
                        boo[i]=boo[i]/2
                    i+=1
                if boo:
                    count= max(boo)
                    dictionary = dict(zip(time_list, boo))
                    for key, values in dictionary.items():
                        if values == count:
                            print_breakfast=key
                    img_time=FoodItems.objects.get(name=print_breakfast).image
                    com_time=FoodItems.objects.get(name=print_breakfast).comment
                else:
                    print_breakfast="No lunch found"

            elif (curr_time>=snacks[0]) and (curr_time<=snacks[1]):
                print_key = "Snacks"
                time_list=[]
                for key, value in time_cat.items():
                    if 'Snack' == value:
                        time_list.append(key)
                boo=[]
                i=0
                for values in time_list:
                    boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
                    if values in bla:
                        boo[i]=boo[i]/2
                    i+=1
                if boo:
                    count= max(boo)
                    dictionary = dict(zip(time_list, boo))
                    for key, values in dictionary.items():
                        if values == count:
                            print_breakfast=key
                    img_time=FoodItems.objects.get(name=print_breakfast).image
                    com_time=FoodItems.objects.get(name=print_breakfast).comment
                else:
                    print_breakfast="No Snack found"

            elif (curr_time>=dinner[0]) and (curr_time<=dinner[1]):
                print_key="Dinner"
                time_list=[]
                for key, value in time_cat.items():
                    if 'Dinner' == value:
                        time_list.append(key)
                boo=[]
                i=0
                for values in time_list:
                    boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
                    if values in bla:
                        boo[i]=boo[i]/2
                    i+=1
                if boo:
                    count= max(boo)
                    dictionary = dict(zip(time_list, boo))
                    for key, values in dictionary.items():
                        if values == count:
                            print_breakfast=key
                    img_time=FoodItems.objects.get(name=print_breakfast).image
                    com_time=FoodItems.objects.get(name=print_breakfast).comment
                else:
                    print_breakfast="No Dinner found"

            else:
                print_key = "All timers"
                time_list=[]
                for key, value in time_cat.items():
                    if 'All timers' == value:
                        time_list.append(key)
                boo=[]
                i=0
                for values in time_list:
                    boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
                    if values in bla:
                        boo[i]=boo[i]/2
                    i+=1
                if boo:
                    count= max(boo)
                    dictionary = dict(zip(time_list, boo))
                    for key, values in dictionary.items():
                        if values == count:
                            print_breakfast=key
                    img_time=FoodItems.objects.get(name=print_breakfast).image
                    com_time=FoodItems.objects.get(name=print_breakfast).comment
                else:
                    print_breakfast="No All timers found"

            # Recommend foods
            # get max rating
            # get food belonging to same category and same content
            # if null then get food belonging to same category if not null and get food belonging to same content if not null
            r=recommend[0][0]
            d=[]
            similiar_food = []
            img=[]
            imgandcom=[]
            for n in recommend:
                d.append(n)
            for n in d:
                similiar_cat = FoodItems.objects.filter(rest_id=rest_id).get(name=n).category
                similiar_cont = FoodItems.objects.filter(rest_id=rest_id).get(name=n).content
                similiar_foods = FoodItems.objects.filter(rest_id=rest_id).filter(category=similiar_cat).filter(content=similiar_cont).exclude(name=n).values_list('name')

                if similiar_foods:
                    similiar_food.append(similiar_foods[0][0])
                    imgandcom.append(FoodItems.objects.get(name=similiar_foods[0][0]))
                    # com.append(FoodItems.objects.get(name=similiar_foods[0][0].comment))
                similiar_foods1 = FoodItems.objects.filter(rest_id=rest_id).filter(content=similiar_cont).exclude(name=n).values_list('name')
                similiar_foods2 = FoodItems.objects.filter(rest_id=rest_id).filter(category=similiar_cat).exclude(name=n).values_list('name')
                if similiar_foods1:
                    similiar_food.append(similiar_foods1[0][0])
                    imgandcom.append(FoodItems.objects.get(name=similiar_foods1[0][0]))
                    # com.append(FoodItems.objects.get(name=similiar_foods1[0][0].comment))
                if similiar_foods2:
                    similiar_food.append(similiar_foods2[0][0])
                    imgandcom.append(FoodItems.objects.get(name=similiar_foods2[0][0]))
                    # com.append(FoodItems.objects.get(name=similiar_foods2[0][0].comment))
            list1 = dict(zip(similiar_food,imgandcom))
            result={}
            for key,value in list1.items():
                if value not in result.values():
                    result[key] = value

            q= FoodItems.objects.get(name=foods[valj])
            img_top=q.image
            com_top = q.comment
            q= FoodItems.objects.get(name=recommend[0])
            img_rec= q.image
            com_rec= q.comment
            #debug=[]
            #max(debug)





            return render(request,'registration/menucard.html',{'menu':menu,'first_time':first_time,'recommend':recommend[0],'com_top':com_top,'uname':uname, 'com_rec':com_rec, 'img_top':img_top, 'img_rec':img_rec, 'top_selling':foods[valj],'curr_time': curr_time,'com_time':com_time,'breakfast':print_breakfast,'message':message,'img_time':img_time,'print_key':print_key,'list1':list1})

@csrf_exempt
def curr_order(request):
    if request.is_ajax():
        rest_id = request.session['rest_id_customer_is_in']
        user_id =request.session['user_id']
        order = request.POST.getlist('arr[]')
        request.session['foods']=order
        table_num= request.session['table_num']
        for orders in order:
            q = Order(food_item=orders, rest_id= rest_id, done=10, user_id=user_id, rating=0, table_num=table_num)
            q.save()
        response = {'order': order}
        return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
def getOrder(request):
    if 'user_id' not in request.session:
        return HttpResponse('Login first')
    if not request.session['typeofuser']:
        return HttpResponse('Wait for ur food')
    rest_id = request.session['user_id']
    if request.is_ajax():
        delete_item = request.POST.get('item')
        q = Order.objects.filter(rest_id=rest_id).filter(food_item=delete_item).filter(done= 10)[0]
        q.done=12
        q.save()
    else:
        orders = Order.objects.filter(rest_id=rest_id).filter(done=10)
        return render(request, 'registration/orders.html',{'orders': orders})

def rgraph(request):
    if not request.session['typeofuser']:
        return HttpResponse("Hi")
    r = robjects.r
    rest_id =request.session['user_id']
    res = str(rest_id)
    r('library(RMySQL)')
    r('con <- dbConnect(MySQL(),user="root", password="crawlerisation",dbname="register", host="localhost")')
    #r('on.exit(dbDisconnect(con))')
    #r('H <- c(2,3,3,3,4,5,5,5,5,6)')
    #r('counts <- table(H)')
    r('''rs <- dbSendQuery(con, paste("SELECT food_item, count(food_item) as count FROM registration_order where rest_id='''+res+''' group by food_item;"))''')
    r('data <- fetch(rs)')
    #r('huh <- dbHasCompleted(rs)')
    #r('dbClearResult(rs)')
    #r('dbDisconnect(con)')

    r('png(file="C:/Users/Admin/PycharmProjects/Main/registration/images/graph.png")')
    #r('barplot(H,main="sdn", color="rainbow(H)")')
    r('barplot(height=data$count,names.arg = data$food_item, las=2)')
    r('dev.off()')
    image_data = open("C:/Users/Admin/PycharmProjects/Main/registration/images/graph.png", "rb").read()
    response = HttpResponse(image_data, content_type="image/png")
    return response
@csrf_exempt
def isReady(request):
    if request.is_ajax():
        flag=0
        user_id = request.session['user_id']
        rest_id = request.session['rest_id_customer_is_in']
        orders = Order.objects.filter(user_id=user_id).filter(rest_id=rest_id)
        x=[]
        for order in orders:
            x=order.done
        for y in range(x):
            if y == 10:
                flag =1
        return HttpResponse(flag)
@csrf_exempt
def thankYou(request):
    if 'user_id' not in request.session:
        return HttpResponseRedirect('../login/0/')
    orders=request.session['foods']
    unique_orders=list(set(orders))
    return render(request,'registration/thankyou.html',{'unique_orders':unique_orders},)

@csrf_exempt
def complete(request):
    if 'user_id' not in request.session:
        return HttpResponseRedirect('../login/0/')
    if request.is_ajax():
        ratings=request.POST.getlist('arr[]')
        rest_id = request.session['rest_id_customer_is_in']
        user_id =request.session['user_id']
        orders=request.session['foods']
        unique_orders=list(set(orders))
        for (order,rating) in zip(unique_orders,ratings):
            Order.objects.filter(user_id=user_id).filter(rest_id=rest_id).filter(food_item=order).update(rating=rating)
        data=1
        return HttpResponse(json.dumps(data),content_type='application/json')

def recommendation(request):
    # recommending favourite food
    # get highest rating
    # find food items with that rating with that user_id in that rest_id
    # if food items>1 select food with max count
    # if food_item category is bread divide its count by 2 to maintain ratio
    # if more than one food items have max count then if one of them is bread don't choose that
    user_id=request.session['user_id']
    rest_id=request.session['rest_id_customer_is_in']
    uname = Register.objects.get(id=user_id).firstname
    q=Order.objects.filter(user_id=user_id).filter(rest_id=rest_id).values_list('rating')
    x= max(q)
    ratio_maintainer = FoodItems.objects.filter(Q(category__icontains="Bread") | Q(category__icontains="Snack")).filter(rest_id=rest_id).values_list('name')
    bla = [l[0] for l in ratio_maintainer] #strip brackets
    for y in x:
        max_rating=y
    food_counter={}
    food_items=[]
    recommend=[]
    q=Order.objects.filter(user_id=user_id).filter(rest_id=rest_id).filter(rating=max_rating)
    for p in q:
        food_items.append(p.food_item)

    if len(set(food_items)) <= 1:
        recommend.append(food_items[0])
    else:
        i=0
        for food in food_items:
            if food in food_counter:
                food_counter[food]+=1
            else:
                food_counter[food]=1
        for x in ratio_maintainer:
            if x in food_counter:
                food_counter[x]=food_counter[x]/2
        recommend = sorted(food_counter, key = food_counter.get, reverse = True)

    #Top selling
    i=0
    temp=0
    j=0
    counter=0
    count= Order.objects.filter(rest_id=rest_id).values('food_item').annotate(fcount=Count('food_item'))
    quantities=[d['fcount'] for d in count]
    foods = [d['food_item'] for d in count]
    for x in bla:
        for y in foods:
            if x==y:
                quantities[i]=quantities[i]/2
                counter+=1
            i+=1
        i=0
    i=0
    for quantity in quantities:
        if quantity>temp:
            temp=quantity
            j=i
        i=i+1
    valj=j
    # Top selling based on time
    i=0
    temp=0
    j=0
    counter=0
    img_time= None
    com_time = None
    print_breakfast = None
    message=""
    time = datetime.now().time()
    curr_time = time
    breakfast=[]
    lunch=[]
    snacks=[]
    dinner=[]
    breakfast.append(time.replace(hour=7, minute=0, second=0, microsecond=0))
    breakfast.append(time.replace(hour=10, minute=30, second=0, microsecond=0))
    lunch.append(time.replace(hour=12, minute=30, second=0, microsecond=0))
    lunch.append(time.replace(hour=15, minute=30, second=0, microsecond=0))
    snacks.append(time.replace(hour=16, minute=0, second=0, microsecond=0))
    snacks.append(time.replace(hour=18, minute=0, second=0, microsecond=0))
    dinner.append(time.replace(hour=20, minute=0, second=0, microsecond=0))
    dinner.append(time.replace(hour=23, minute=0, second=0, microsecond=0))

    cursor=connection.cursor()
    cursor.execute('''SELECT registration_order.food_item, registration_fooditems.time FROM registration_order LEFT JOIN registration_fooditems ON registration_order.food_item = registration_fooditems.name WHERE registration_order.rest_id=%s AND registration_fooditems.rest_id=%s''', [rest_id,rest_id])
    all=cursor.fetchall()
    time_cat= dict(all)
    if (curr_time>=breakfast[0]) and (curr_time <= breakfast[1]):
        print_key = "Breakfast"
        time_list=[]
        for key, value in time_cat.items():
            if 'Breakfast' == value:
                time_list.append(key)
        boo=[]
        i=0
        for values in time_list:
            boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
            if values in bla:
                boo[i]=boo[i]/2
            i+=1
        if boo:
            count= max(boo)
            dictionary = dict(zip(time_list, boo))
            for key, values in dictionary.items():
                if values == count:
                    print_breakfast=key
            img_time=FoodItems.objects.get(name=print_breakfast).image
            com_time=FoodItems.objects.get(name=print_breakfast).comment
        else:
            message = "No breakfast found"

    elif (curr_time>=lunch[0]) and (curr_time<=lunch[1]):
        print_key = "Lunch"
        time_list=[]
        for key, value in time_cat.items():
            if 'Lunch' == value:
                time_list.append(key)
        boo=[]
        i=0
        for values in time_list:
            boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
            if values in bla:
                boo[i]=boo[i]/2
            i+=1
        if boo:
            count= max(boo)
            dictionary = dict(zip(time_list, boo))
            for key, values in dictionary.items():
                if values == count:
                    print_breakfast=key
            img_time=FoodItems.objects.get(name=print_breakfast).image
            com_time=FoodItems.objects.get(name=print_breakfast).comment
        else:
            print_breakfast="No lunch found"

    elif (curr_time>=snacks[0]) and (curr_time<=snacks[1]):
        print_key = "Snacks"
        time_list=[]
        for key, value in time_cat.items():
            if 'Snack' == value:
                time_list.append(key)
        boo=[]
        i=0
        for values in time_list:
            boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
            if values in bla:
                boo[i]=boo[i]/2
            i+=1
        if boo:
            count= max(boo)
            dictionary = dict(zip(time_list, boo))
            for key, values in dictionary.items():
                if values == count:
                    print_breakfast=key
            img_time=FoodItems.objects.get(name=print_breakfast).image
            com_time=FoodItems.objects.get(name=print_breakfast).comment
        else:
            print_breakfast="No Snack found"

    elif (curr_time>=dinner[0]) and (curr_time<=dinner[1]):
        print_key="Dinner"
        time_list=[]
        for key, value in time_cat.items():
            if 'Dinner' == value:
                time_list.append(key)
        boo=[]
        i=0
        for values in time_list:
            boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
            if values in bla:
                boo[i]=boo[i]/2
            i+=1
        if boo:
            count= max(boo)
            dictionary = dict(zip(time_list, boo))
            for key, values in dictionary.items():
                if values == count:
                    print_breakfast=key
            img_time=FoodItems.objects.get(name=print_breakfast).image
            com_time=FoodItems.objects.get(name=print_breakfast).comment
        else:
            print_breakfast="No Dinner found"

    else:
        print_key = "All timers"
        time_list=[]
        for key, value in time_cat.items():
            if 'All timers' == value:
                time_list.append(key)
        boo=[]
        i=0
        for values in time_list:
            boo.append(Order.objects.filter(food_item=values).filter(rest_id=rest_id).count())
            if values in bla:
                boo[i]=boo[i]/2
            i+=1
        if boo:
            count= max(boo)
            dictionary = dict(zip(time_list, boo))
            for key, values in dictionary.items():
                if values == count:
                    print_breakfast=key
            img_time=FoodItems.objects.get(name=print_breakfast).image
            com_time=FoodItems.objects.get(name=print_breakfast).comment
        else:
            print_breakfast="No All timers found"

    # Recommend foods
    # get max rating
    # get food belonging to same category and same content
    # if null then get food belonging to same category if not null and get food belonging to same content if not null
    r=recommend[0][0]
    d=[]
    similiar_food = []
    img=[]
    imgandcom=[]
    for n in recommend:
        d.append(n)
    for n in d:
        similiar_cat = FoodItems.objects.filter(rest_id=rest_id).get(name=n).category
        similiar_cont = FoodItems.objects.filter(rest_id=rest_id).get(name=n).content
        similiar_foods = FoodItems.objects.filter(rest_id=rest_id).filter(category=similiar_cat).filter(content=similiar_cont).exclude(name=n).values_list('name')

        if similiar_foods:
            similiar_food.append(similiar_foods[0][0])
            imgandcom.append(FoodItems.objects.get(name=similiar_foods[0][0]))
            # com.append(FoodItems.objects.get(name=similiar_foods[0][0].comment))
        similiar_foods1 = FoodItems.objects.filter(rest_id=rest_id).filter(content=similiar_cont).exclude(name=n).values_list('name')
        similiar_foods2 = FoodItems.objects.filter(rest_id=rest_id).filter(category=similiar_cat).exclude(name=n).values_list('name')
        if similiar_foods1:
            similiar_food.append(similiar_foods1[0][0])
            imgandcom.append(FoodItems.objects.get(name=similiar_foods1[0][0]))
            # com.append(FoodItems.objects.get(name=similiar_foods1[0][0].comment))
        if similiar_foods2:
            similiar_food.append(similiar_foods2[0][0])
            imgandcom.append(FoodItems.objects.get(name=similiar_foods2[0][0]))
            # com.append(FoodItems.objects.get(name=similiar_foods2[0][0].comment))
    list1 = dict(zip(similiar_food,imgandcom))
    result={}
    for key,value in list1.items():
        if value not in result.values():
            result[key] = value

    q= FoodItems.objects.get(name=foods[valj])
    img_top=q.image
    com_top = q.comment
    q= FoodItems.objects.get(name=recommend[0])
    img_rec= q.image
    com_rec= q.comment
    # debug=[]
    # max(debug)
    return render(request,'registration/test.html',{'recommend':recommend[0],'com_top':com_top,'uname':uname, 'com_rec':com_rec, 'img_top':img_top, 'img_rec':img_rec, 'top_selling':foods[valj],'curr_time': curr_time,'com_time':com_time,'breakfast':print_breakfast,'message':message,'img_time':img_time,'print_key':print_key,'list1':list1})
