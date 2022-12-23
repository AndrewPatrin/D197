from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView


from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.contrib import messages
from main.decorators import user_not_authenticated
from .forms import UserRegistrationForm, BaseRegisterForm, LoginForm, AccountActivationForm
from .models import CustomUser
from main.models import UserOneTimeCode


# def activate(request, uidb64, token):
#     User = get_user_model()
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         print(uid)
#         user = User.objects.get(pk=uid)
#     except:
#         user = None
#
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#
#         messages.success(
#             request, "Your email is confirmed. Account is activated.")
#         return redirect('/login/')
#     else:
#         messages.error(request, "Activation link is invalid!")
#     return redirect('/login/')
# def activate(request, uidb64, token):
#     User = get_user_model()
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except:
#         user = None
#
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#
#         messages.success(
#             request, "Your email is confirmed. Account is activated.")
#         return redirect('/login/')
#     else:
#         messages.error(request, "Activation link is invalid!")
#     return redirect('/login/')

#
@login_required
def logout_user(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('/login/')

# def activateEmail(request, user, to_email):
#     mail_subject = "Activate your user account."
#     message = render_to_string("user/email/email_confirmation_message.html", {
#         'user': user.username,
#         'domain': get_current_site(request).domain + ':8000',
#         'uid': urlsafe_base64_encode(force_bytes(user.pk)),
#         'token': account_activation_token.make_token(user),
#         "protocol": 'https' if request.is_secure() else 'http'
#     })
#     email = EmailMessage(mail_subject, message, to=[to_email])
#     if email.send():
#         messages.success(request, f'Hello <b>{user}</b>, please go to you email <b>{to_email}</b> and click on \
#                 received activation link to confirm and complete the registration.')
#     else:
#         messages.error(
#             request, f'Sending email to {to_email} failed, check if you typed it correctly.')

def activateEmail(request, token, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("user/email/email_onetimecode_message.html", {
        'user': user.username,
        'domain': get_current_site(request).domain + ':8000',
        'token': token,
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Hello <b>{user}</b>, A one-time code was sent to your email <b>{user.email}<b>.\
                Enter your email and received code bellow to activate your account.')
    else:
        messages.error(
            request, f'Sending email to {to_email} failed, check if you typed it correctly.')

def login_user(request):
    if request.user.is_authenticated:
        return redirect('/posts/')

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
                return redirect('/posts/')
        else:
            messages.error(request, "Invalid username or password or account wasn't activated")

    form = LoginForm()

    return render(
        request=request,
        template_name="user/login.html",
        context={"form": form}
    )

@method_decorator(user_not_authenticated, name='dispatch')
class BaseRegisterView(CreateView):
    model = CustomUser
    form_class = BaseRegisterForm
    success_url = '/activate/'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        token = account_activation_token.make_token(user)
        code = UserOneTimeCode.objects.create(code=token, user=user, email=user.email)
        code.save()
        activateEmail(self.request, token, user, form.cleaned_data['email'])
        return super().form_valid(form)

def accountActivate(request, backend='django.contrib.auth.backends.ModelBackend'):
    if request.user.is_authenticated:
        return redirect('/posts/')

    if request.method == 'POST':
        form = AccountActivationForm(request.POST)
        if form.is_valid():
            try:
                onetimecodeobj = UserOneTimeCode.objects.get(email=form.cleaned_data['email'])
            except:
                messages.error(
                    request, "Account on this email address has been already activated or hasn't been registered yet")
                return redirect('/activate/')

            if onetimecodeobj and onetimecodeobj.code == '':
                onetimecodeobj.delete()
                user = CustomUser.objects.get(email=form.cleaned_data['email'])
                token = account_activation_token.make_token(user)
                code = UserOneTimeCode.objects.create(code=token, user=user, email=user.email)
                code.save()
                activateEmail(request, token, user, form.cleaned_data['email'])
                messages.error(
                    request, "Code is out of date. New was set to your email")
                return redirect('/activate/')

            try:
                onecodeobj = UserOneTimeCode.objects.get(code=form.cleaned_data['code'])
            except:
                messages.error(
                    request, f'Invalid activation code')
                return redirect('/activate/')

            if onecodeobj == onetimecodeobj:
                user = CustomUser.objects.get(email=onecodeobj.email)
                user.is_active = True
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
                onecodeobj.delete()
                return redirect('/posts/')
            else:
                messages.error(
                    request, f'Invalid code or account on this email is not registered')
                return redirect('/activate/')
        else:
            messages.error(request, "Invalid email")

    form = AccountActivationForm()
    return render(
        request=request,
        template_name="user/account_activate.html",
        context={"form": form}
    )

@login_required
def account(request):

    return render(
        request=request,
        template_name="user/account.html",
        # context={"form": form}
    )
