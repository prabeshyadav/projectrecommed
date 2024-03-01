
from django.contrib.auth.views import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic.base import TemplateView
import pandas as pd
from src.Recommend import Recommend
from django.http import JsonResponse, HttpResponse
import json
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from .forms import SignupForm

def home(request):
    return render(request, 'home.html')


class RecommendView(TemplateView):
    template_name = 'detail.html'

    def get(self, *args, **kwargs):
        user_data_order_dict = dict(self.request.GET)

        category = self.request.GET.get('category', 'default_category')
        if category == 'default_category':
            raise ValueError('Category is required in the request parameters.')

        user_dict = {}
        for k, v in user_data_order_dict.items():
         if v and k == 'age':
            try:
             user_dict[k] = self.quantify_age(int(v[0]))
            except ValueError:
             user_dict[k] = 0
         elif v:
             try:
                user_dict[k] = int(v[0])
             except ValueError:
                user_dict[k] = 0

        pd_dataframe = pd.DataFrame.from_dict([user_dict])

        similar = Recommend(pd_dataframe, category)
        data = similar.getData()

        context = super().get_context_data()
        context['similar_jobs'] = data

        return render(self.request, self.template_name, context)

    def quantify_age(self, age):
        try:
            age = int(age)
            if age > 0:
                return 1 if age > 40 else 2 if age > 35 else 3 if age > 30 else 4 if age > 25 else 5
            else:
                # Handle the case where 'age' is not a valid positive integer
                return 0
        except ValueError:
            # Handle the case where 'age' is not a valid integer
            return 0
    



def reco(request):
    if request.method == 'GET':
        user_data_order_dict = dict(request.GET)
        category = request.GET.get('category', 'default_category')
        if category == 'default_category':
            raise ValueError('Category is required in the request parameters.')

        user_dict = {}
        for k, v in user_data_order_dict.items():
            if v and k == 'age':
                try:
                    user_dict[k] = quantify_age(int(v[0]))
                except ValueError:
                    user_dict[k] = 0
            elif v:
                user_dict[k] = int(v[0])

        pd_dataframe = pd.DataFrame.from_dict([user_dict])

        similar = Recommend(pd_dataframe, category)
        data = similar.getData()

        new_data = json.dumps(data, default=str)

        return JsonResponse(data, safe=False)




class LoginView(View):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

        return render(request, self.template_name)





class RegisterView(FormView):
    template_name = 'register.html'
    form_class = SignupForm
    success_url = reverse_lazy('login')  # Redirect to login page upon successful registration

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Account created successfully. You can now log in.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please check the form and try again.')
        return super().form_invalid(form)
