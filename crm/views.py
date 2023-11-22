from django.shortcuts import render,redirect
from django.views.generic import View
from crm.forms import EmployeeModelForms,RegistrationForm,LoginForm
from crm.models import Employees
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils.decorators import method_decorator

def sign_in_required(fn):
    def wrapper(request,*args,**kwargs):
        if not  request.user.is_authenticated:                   
              messages.error(request,"Invalid Session")
              return redirect("signin")
        else:
             return fn(request,*args,**kwargs)
    return wrapper

@method_decorator(sign_in_required,name="dispatch")
class EmployeeCreateView(View):
    def get(self,request,*args,**kwargs):
        form=EmployeeModelForms()
        return render(request,"emp_add.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=EmployeeModelForms(request.POST,files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"employee has been added")
            # Employees.objects.create(**form.cleaned_data)
            print("created")
            return render(request,"emp_add.html",{"form":form})
        else:
            messages.error(request,"failed to add employee")
            return render(request,"emp_add.html",{"form":form})
        
@method_decorator(sign_in_required,name="dispatch")        
class EmployeeListView(View):
    def get(self,request,*args,**kwargs):
          qs=Employees.objects.all()
          departments=Employees.objects.all().values_list("department",flat=True).distinct()
          print(departments)
          if "department" in request.GET:
              dept=request.GET.get("department")
              qs=qs.filter(department=dept)

          return render(request,"emp_list.html",{"data":qs,"departments":departments})
       

      
    def post(self,request,*args,**kwargs):
        name=request.POST.get("box")
        qs=Employees.objects.filter(name__icontains=name)
        return render(request,"emp_list.html",{"data":qs})

@method_decorator(sign_in_required,name="dispatch")   
class EmployeeDetailView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Employees.objects.get(id=id)
        return render(request,"emp_detail.html",{"data":qs})
    
@method_decorator(sign_in_required,name="dispatch")
class EmployeeDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Employees.objects.get(id=id).delete()
        messages.success(request,"deleted") 
        return redirect("emp-all")

@method_decorator(sign_in_required,name="dispatch")
class EmployeeUpdateView(View):

    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        obj=Employees.objects.get(id=id)
        form=EmployeeModelForms(instance=obj)
        return render(request,"emp_edit.html",{"form":form})
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        obj=Employees.objects.get(id=id)
        form=EmployeeModelForms(request.POST,instance=obj,files=request.FILES) 
        if form.is_valid():
            form.save()
            messages.success(request,"updated")
            return redirect("emp-details",pk=id)
        else:
            messages.error(request,"failed to update")
            return render(request,"emp_edit.html")


class SignUpView(View):
    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"register.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)  
            # form.save()
            messages.success(request,"Created")
            # print("saved")
            return render(request,"register.html",{"form":form})
        else:
            # print("failed")
             messages.error(request,"Failed")
             return render(request,"register.html",{"form":form})
        
class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"login.html",{"form":form})

    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)

        if form.is_valid():
            user_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            print(user_name,pwd) 
            user_obj=authenticate(request,username=user_name,password=pwd)
            if user_obj:
                print("valid")
                login(request,user_obj)
                return redirect("emp-all")
        messages.error(request,"Invalid credential")
        return render(request,"login.html",{"form":form})
        
@method_decorator(sign_in_required,name="dispatch")
class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")

