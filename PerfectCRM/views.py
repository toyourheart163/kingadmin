# PerfectCRM/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.decorators import login_required


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
            login(request,user)
            return redirect(request.GET.get('next', '/crm/'))
        else:
            error_msg = '用户名或密码错误！'
    return render(request,'login.html', {'error_msg': error_msg})

def acc_logout(request):
    logout(request)
    return redirect("/login/")

@login_required
def dashboard(request):

    return render(request,'crm/dashboard.html')
