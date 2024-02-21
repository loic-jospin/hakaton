
from django.utils.http import urlsafe_base64_decode,  urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .token import generatorToken


from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from authentification import settings
from django.core.mail import send_mail, EmailMessage

# Create your views here.

def home(request):
    return render(request, "app/index.html")



def register(request):
    if request.method == "POST":
        #on recupere ce qui a été entré par l'utilisateur
        username = request.POST['username']
        fistname = request.POST['fistname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']
        #On vérifie si le nom d'utilisateur exixte deja
        if User.objects.filter(username=username):
            messages.error(request,"Le nom d'utilisateur existe déja.")
            return redirect('register')
        if User.objects.filter(email=email):
            messages.warning(request,"L'adresse e-mail est déjà utilisée.")
            return redirect('register')
        if not username.isalnum( ):
            messages.error(request,'Votre nom d\'utilisateur doit contenir uniquement des lettres et des chiffres.')
            messages.error(request,'Le nom d\'utilisateur ne peut contenir que des lettres et des chiffres.')
            return redirect("register")
        if password != password1:
            messages.error(request, 'Les mots de passe sont différents.')
            return redirect('register')
        #enregistrons les donnée de l'utlisateur pour cela on importe le modele User
        mon_utilistaeur = User.objects.create_user(username, email, password)
        mon_utilistaeur.first_name = fistname
        mon_utilistaeur.last_name = lastname
        mon_utilistaeur.is_active =False 
        mon_utilistaeur.save()
        #on a enregistré on lui revoie un message pour cela on importe la fonction message
        messages.success(request, 'votre compte a été crée avec succes')
        #on envoie l'email a l'utilisateur
        subject = "Bienvenu chez loic developpeur fullstack junior"
        message = "Bienvenue " + mon_utilistaeur.first_name +" "+ mon_utilistaeur.last_name+ "\n Nous sommes heureux de vous compter parmi nous\n\n\n Merci\n\n Loic jospin"
        from_email = settings.EMAIL_HOST_USER
        #on envoie a qui? to_list (plusieur personne) comme je veux envoyer a 1 seule personne je precise monuser dans les crochets parce que il se connecte a l'instant t
        to_list=[mon_utilistaeur.email]
        #maintenant on envoie. on importe d'abors la fonction send_mail
        send_mail(subject, message, from_email, to_list, fail_silently=False)
        #Email de confirmation
        current_site = get_current_site(request)
        email_subject = "confirmation de l'address email chez loic developpeur"
        messageConfirm = render_to_string("emailconfirm.html", {
            "name": mon_utilistaeur.first_name,
            "domain": current_site.domain,
            "uid":urlsafe_base64_encode(force_bytes(mon_utilistaeur.pk)),
            "token":generatorToken.make_token(mon_utilistaeur)
        })

        email = EmailMessage(
            email_subject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [mon_utilistaeur.email]
        )
        email.fail_silenty = False
        email.send()
        return redirect('login')
    return render(request, 'app/register.html')


def logIn(request):
    if request.method == "POST":
          #on importe la fonction authenticate pour l'authentification
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        my_user = User.objects.get(username=username)
        #verifions si l'utilisateur existe vraiment on le login
        if user is not None:
            login(request, user)
            firstname = user.first_name
       
            return render(request, 'app/index.html', {'firstname':firstname})
        elif my_user.is_active == False:
            messages.error(request, "vous n'avez pas confirmé votre addresse email! faites le maintenat.")
        else:
            messages.error(request, 'Mauvaise authentification')
            return redirect('login')
    return render(request, 'app/login.html')

def logOut(request):
    logout(request)
    messages.success(request, 'Vous êtes déconnecté')
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid =force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None


    if user is not None and generatorToken.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "votre compte a bien été activé félicitation connectez vous maintenat.")
        return redirect('login')
    else:
        messages.error(request, 'activation de votre compte a échoué.')
        return redirect('home')
    
