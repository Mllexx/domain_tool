from django.http import JsonResponse, Http404
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CompanyForm, DomainForm, UserForm
from .models import Company, Domain
from django.db.models import Q
from django.views import View
import requests, json, logging
from django.contrib import messages
from datetime import date
from .models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

def index(request):
    return render(request, "index.html")

@login_required(login_url="signin")
def dashboard(request):
    active_domains = Domain.objects.filter(expiry_date__gte=date.today()).count()
    expired_domains = Domain.objects.filter(expiry_date__lt=date.today()).count()

    context = {
        'active_domains': active_domains,
        'expired_domains': expired_domains,
        'domains': Domain.objects.all(),
    }

    return render(request, 'dashboard.html', context)

def signin(request):
    msg = ""
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if the user exists with the given email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        # Check if the user exists and is not active
        if user and not user.is_active:
            msg = "Account inactive! Contact admin"
        else:
            # Attempt to authenticate the user
            user = authenticate(request, username=email, password=password)

            # Check if authentication was successful and user is active
            if user and user.is_active:
                # Print all fields of the user
                login(request, user)

                if "next" in request.POST:
                    return redirect(request.POST.get("next"))
                return redirect("dashboard")
            else:
                msg = "Invalid credentials"

    context = {"msg": msg}
    return render(request, "signin.html", context)

# def signup(request):
    
#     form = UserCreationForm()
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             # login starts here
#             username = request.POST['username'] 
#             password = request.POST['password1']
#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect("index")
#     context = {"form":form}
#     return render(request, "signup.html", context)

def signout(request):
    logout(request)
    return redirect("index")

def list_users(request):
    users = User.objects.all()
    return render(request, 'users_list.html', {'users': users})

@login_required(login_url="signin")
def add_user(request, user_id=None):
    # If user_id is provided, fetch the user instance for update; otherwise, create a new instance
    user = get_object_or_404(User, pk=user_id) if user_id else None

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            # Check if the username and email already exist for other users
            existing_username = User.objects.exclude(pk=user.pk).filter(username=user.username).exists()
            existing_email = User.objects.exclude(pk=user.pk).filter(email=user.email).exists()

            # Check if there are conflicts with the username or email
            if existing_username:
                form.add_error('username', 'User with this Username already available.')
            if existing_email:
                form.add_error('email', 'User with this Email already available.')

            if not existing_username and not existing_email:
                # Get the role from the form's cleaned_data
                role = form.cleaned_data['role']
                status = form.cleaned_data['status']
                
                # Set the role-specific attributes based on the selected role
                if role == 'admin':
                    user.is_admin = True
                elif role == 'user':
                    user.is_user = True

                # Set the is_active attribute based on the status field
                user.is_active = status
                
                user.save()

                # Determine if the user was added or updated and display the appropriate message
                if user_id:
                    messages.success(request, 'User Updated successfully!')
                else:
                    messages.success(request, 'User Added successfully!')

                # Redirect to the user management section for administrators
                return redirect('users')  # Change 'user_management' to the URL for managing users
    else:
        # If it's an update, populate the form with the existing user data
        form = UserForm(instance=user)

    return render(request, 'add_user.html', {'form': form, 'user': user})

@login_required(login_url="signin")
def company_list(request, id=0):
    if request.method == "GET":
        if id==0:
            form = CompanyForm()
        else:
            company = Company.objects.get(pk=id)
            form = CompanyForm(instance=company)
        return render(request, "manage_company.html",{'form':form})
    else:
        if id == 0:
            form = CompanyForm(request.POST)
        else:
            company = Company.objects.get(pk=id)   
            form = CompanyForm(request.POST,instance=company) 
        if form.is_valid():
            form.save()
            messages.success(request, 'Company Added!')
            context = {'companies': Company.objects.all()}
        return render(request, "company_list.html", context)
    
@login_required(login_url="signin")
def companies(request):
    context = {'companies': Company.objects.all()} 
    return render(request,"company_list.html", context)

def company_delete(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    if request.method == 'POST':
        company.delete()
        messages.error(request, 'Company deleted!')
        return redirect('lists')  # Redirect to the appropriate URL after deletion
    
    # Handle other HTTP methods (GET, etc.) as needed
    
    # Optionally, you can provide a response here for other HTTP methods
    return redirect('lists')

@login_required(login_url="signin")
def domain(request):
    context = {'domains': Domain.objects.all()}
    return render(request, "manage_domain.html", context)

@login_required(login_url="signin")
def domain_status(request):
    context = {'domains': Domain.objects.all()}
    return render(request, "domain_status.html", context)

@login_required(login_url="signin")
def domain_list(request):
    if request.method == "GET":
        form = DomainForm()
        return render(request, "add_domain.html",{'form':form})
    else:
        form = DomainForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Domain Added!')
            context = {'domains': Domain.objects.all()}
        return render(request, "manage_domain.html", context)

def lookup(request):
    if request.method == 'POST':
        form = DomainForm(request.POST)
        
        if form.is_valid():
            try:
                domain_value = form.cleaned_data['name']
                
                print(f"Domain Value: {domain_value}")

                # Your API token for whoisjsonapi.com
                api_token = 'FQcwBdbvYkjMHFZ6B4HEVnOovTnS07CUqRnR26NAJcxWCx6yTNrfUzN9YUzE_eC'
                
                # Construct the API URL
                api_url = f'https://whoisjsonapi.com/v1/{domain_value}'
                print(f"api_url: {api_url}")
                # Set the headers for the request
                headers = {

                    'Authorization': f'Bearer {api_token}',
                }
                
                # Send a GET request to the API with headers and timeout
                response = requests.get(api_url, headers=headers)
                
                # Check if the API request was successful
                response.raise_for_status()
                
                # Parse the JSON response
                data = response.json()
                
                print(f"API Response: {response.content}")
                
                # Extract relevant information
                domain_info = data.get('domain', {})
                registration_date = domain_info.get('created_date', '')
                expiry_date = domain_info.get('expiration_date', '')
                
                print(f"Creation Date: {registration_date}")
                print(f"Expiration Date: {expiry_date}")

                # Return the relevant data as JSON
                return JsonResponse({
                    'status': 'success',
                    'registration_date': registration_date,
                    'expiry_date': expiry_date,
                })
            
            except requests.RequestException as e:
                # Handle API request error
                return JsonResponse({'error': f'Failed to retrieve data from the API. Error: {e}'}, status=500)
            
            except Exception as e:
                # Handle other exceptions
                return JsonResponse({'error': f'An unexpected error occurred: {e}'}, status=500)
        
        else:
            # Handle form validation errors
            return JsonResponse({'error': 'Form validation error.'}, status=400)
    
    else:
        return JsonResponse({'error': 'This view is for handling POST requests only.'}, status=400)
    
class DomainUpdateView(View):
    def get(self, request, *args, **kwargs):
        domain_name = self.kwargs.get('domain_name')
        api_token = 'FQcwBdbvYkjMHFZ6B4HEVnOovTnS07CUqRnR26NAJcxWCx6yTNrfUzN9YUzE_eC'  # Replace with your actual API token

        # Print the URL before making the API request
        print(f'Requesting API for domain: {domain_name}')
        api_url = f'https://whoisjsonapi.com/v1/{domain_name}'
        print(f"api_url: {api_url}")

        # Set the headers for the request
        headers = {
             'Authorization': f'Bearer {api_token}',
        }

        try:
            # Make the API request
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Check if the API request was successful

            # Parse the JSON response
            data = response.json()
            print(f"API Response: {response.content}")

            # Check if the response has the expected structure
            if 'domain' not in data or 'registrar' not in data:
                raise ValueError('Invalid response structure')

            # Extract relevant information
            
            registrar_info = data['registrar']
            
            # Include the registrar's name in the response
            registrar_name = registrar_info.get('name', 'N/A')

            # Respond with the formatted updated_date and registrar's name
            return JsonResponse({ 'registrar_name': registrar_name})

        except requests.exceptions.RequestException as e:
            # Handle request exceptions
            print(f'Error for {domain_name}: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)

        except ValueError as e:
            # Handle invalid response structure
            print(f'Error for {domain_name}: {str(e)}')
            return JsonResponse({'error': str(e)}, status=500)
        

def domain_delete(request, domain_id):
    domain = get_object_or_404(Domain, id=domain_id)
    
    if request.method == 'POST':
        # Check if the related Company exists
        try:
            company = domain.company
        except Company.DoesNotExist:
            # Redirect or handle the case where the related Company doesn't exist
            return redirect('domain')  # Adjust the target according to your URL structure

        domain.delete()
        messages.error(request, 'Domain deleted!')
        return redirect('domain')  # Redirect to the appropriate URL after deletion
    
    # Handle other HTTP methods (GET, etc.) as needed
    
    # Optionally, you can provide a response here for other HTTP methods
    return redirect('domain')
        
class ActiveUserRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and not self.request.user.is_active:
            return self.handle_inactive_user()
        return super().dispatch(request, *args, **kwargs)

    def handle_inactive_user(self):
        return redirect('inactive_account')

class MyRestrictedView(ActiveUserRequiredMixin, TemplateView):
    template_name = 'inactive.html'        