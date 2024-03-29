from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from kingadmin import app_setup

app_setup.kingadmin_auto_discover()

from kingadmin.sites import site

print('site', site.enable_admins)

def acc_login(request):
    error_msg = ''
    if request.method == 'POST':
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        #user是一个对象
        #验证
        user = authenticate(username=username,password=password)
        if user:
            #登录（已生成session）
            login(request, user)
            #如果有next值就获取next值，没有就跳转到首页
            return redirect(request.GET.get('next','/kingadmin/'))
        else:
            error_msg = '用户名或密码错误！'

    return render(request,'kingadmin/login.html',{'error_msg':error_msg})


def acc_logout(request):
    logout(request)
    return redirect("/login/")

def app_index(request):
    return render(request, 'kingadmin/app_index.html', {'site': site})

def get_filter_result(request,querysets):
    filter_conditions = {}
    #获取过滤的字段
    for key,val in request.GET.items():
        if key in ('page', 'o', '_q'): continue
        if val:
            filter_conditions[key] = val
    #返回过滤后的数据
    return querysets.filter(**filter_conditions),filter_conditions

@login_required
def table_obj_list(request, app_name, model_name):
    '''取出指定model里的数据返回给前端'''
    #拿到admin_class后，通过它找到拿到model
    admin_class = site.enable_admins[app_name][model_name]
    querysets = admin_class.model.objects.all()
    querysets,filter_conditions = get_filter_result(request,querysets)
    admin_class.filter_conditions = filter_conditions

    # 搜索
    querysets = get_searched_result(request, querysets, admin_class)
    # 排序
    querysets, sorted_column = get_orderby_result(request, querysets, admin_class)

    admin_class.search_key = request.GET.get('_q', '')
    paginator = Paginator(querysets, 2)
    page = request.GET.get('page')
    try:
        querysets = paginator.page(page)
    except PageNotAnInteger:
        querysets = paginator.page(1)
    except EmptyPage:
        querysets = paginator.page(paginator.num_pages)

    return render(request, 'kingadmin/table_obj_list.html',{'querysets':querysets,'admin_class':admin_class, 'sorted_column': sorted_column})

def get_orderby_result(request,querysets,admin_class):
    '''排序'''
    current_ordered_column = {}
    #通过前端获取到要排序的字段的索引（是个字符串）
    orderby_index = request.GET.get('o')
    print('1', orderby_index)
    if orderby_index:
        print(orderby_index)
        #通过索引找到要排序的字段,因为索引有可能是负数也有可能是负数，要用绝对值，否则负值的时候取到了其它字段了
        orderby_key = admin_class.list_display[abs(int(orderby_index))]
        #记录下当前是按什么排序字段的
        current_ordered_column[orderby_key] = orderby_index
        if orderby_index.startswith('-'):
            orderby_key = '-' + orderby_key

        return querysets.order_by(orderby_key),current_ordered_column
    else:
        return querysets,current_ordered_column

from django.db.models import Q

def get_searched_result(request,querysets,admin_class):
    '''搜索'''

    search_key = request.GET.get('_q')
    if search_key:
        q = Q()
        q.connector = 'OR'

        for search_field in admin_class.search_fields:
            q.children.append(("%s__contains"%search_field,search_key))

        return querysets.filter(q)
    return querysets
