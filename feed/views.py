from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Collection, Image
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import NewUserForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages


# Setup generic views
class IndexView(generic.ListView):
    template_name = 'feed/base_index.html'
    context_object_name = 'latest_image_feed'
    c = Collection.objects.get(name='main_feed')
    def get_queryset(self):
        """Return images from the 'main_feed' collection."""
        i = Image.objects.filter(collection=self.c.id)
        return i[::-1]

# view the image on its own page in more detail
# feed/<int id: id>/
# feed/image-name
class DetailView(generic.DetailView):
    model = Image
    template_name = 'feed/base_detail.html'

class AboutView(generic.DetailView):
    model = Image
    template_name = 'feed/base_about.html'

class ResultsView(generic.ListView):
    model = Collection
    template_name = 'feed/base_results.html'
    context_object_name = 'user_liked'
    
    def get_queryset(self):
        u = User.objects.get(pk=1)
        get_all = u.image_set.order_by('-votes')
        return get_all

class LeaderboardView(generic.ListView):
    model = Collection
    template_name = 'feed/base_poll.html'
    context_object_name = 'leaderboard'

    def get_queryset(self):
        # get the main_feed (collection with id/primary key equaling 1)
        c = Collection.objects.get(pk=1)
        get_all = c.image_set.order_by("-votes")
        return get_all

def getUserAuth(user):
    userAuth = authenticate(username=user.username, password=user.password)
    if userAuth is not None:
        # backend authenticated user
        return True
    else:
        return False

def about(request):
    return render(request, 'feed/base_about.html')

def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if getUserAuth(user) == False or user.is_authenticated == False:
        # raise Http404("You don't have permission to access this page. User is not authenticated")
        return redirect('feed:login')

    try:
        c = Collection.objects.get(name="{u}_{uid}".format(u=user.username, uid=user_id))
    except Collection.DoesNotExist:
        c = Collection(name="{u}_{i}".format(u=user.username, i=user.id), created_at=timezone.now())
        c.save()
    liked = user.image_set.filter(collection=c.id)

    return render(request, 'feed/base_profile.html', {
        'liked': liked[::-1],
        'likedNum': len(liked)
    })

def like(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    if request.user.is_authenticated == False:
        return redirect('feed:login')

    u = get_object_or_404(User, pk=request.user.id)
    coll_exists = ""

    try:
        selected_choice = Image.objects.get(pk=request.POST['option'])
        coll_exists = Collection.objects.get(name="{u}_{i}".format(u=u.username, i=u.id))
        coll_exists.image_set.create(collection=coll_exists,
            user=u,
            title=selected_choice.title,
            alt=selected_choice.alt,
            src=selected_choice.src,
            created_at=selected_choice.created_at,
            votes=selected_choice.votes
            )
        coll_exists.save()
    except (Collection.DoesNotExist, KeyError, Image.DoesNotExist) as e:
        coll_exists = Collection(name="{u}_{i}".format(u=u.username, i=u.id), created_at=timezone.now())
        coll_exists.save()
        coll_exists.image_set.create(collection=coll_exists,
            user=u,
            title=selected_choice.title,
            alt=selected_choice.alt,
            src=selected_choice.src,
            created_at=selected_choice.created_at,
            votes=selected_choice.votes
            )
        coll_exists.save()
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('feed:profile', args=(u.id,)))
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('feed:profile', args=(u.id,)))
    

def register(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
            # After user successfully is registered, login
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect('feed:index')
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="feed/base_register.html", context={"register_form":form})

def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('feed:index')
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="feed/base_login.html", context={"login_form":form})

def logout_user(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("feed:index")

def unlike(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    cname = "{u}_{uid}".format(u=u.username, uid=u.id)
    img_id = request.POST['image']

    try:
        coll = Collection.objects.get(name=cname)
        cimg = coll.image_set.get(id=img_id)
        # delete the image from the users collection
        cimg.delete()
        # and decrement the votes counter for that image
        # in the main feed to reflect in the leaderboards
        main_feed = Collection.objects.get(pk=1)
        img = main_feed.image_set.get(title=cimg.title)
        img.votes -= 1
        img.save()
    except (KeyError, Collection.DoesNotExist, Image.DoesNotExist) as e:
        print("Collection or Image does not exist? Major error!", e)

    return HttpResponseRedirect(reverse('feed:profile', args=(u.id,)))
