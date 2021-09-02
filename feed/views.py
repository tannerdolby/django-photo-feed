from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Collection, Image
from django.contrib.auth.models import User
from django.utils import timezone
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import NewUserForm, ModelFormWithFileField, ModelFormWithImageField
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.conf import settings
from os import getcwd
from pandas import read_csv
from unicodedata import normalize
from unidecode import unidecode

cwd = getcwd()

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

def about(request):
    return render(request, 'feed/base_about.html')

def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    if user.id != request.user.id:
        # raise Http404("You don't have permission to access this page. User is not authenticated")
        return redirect('feed:index')
    try:
        c = Collection.objects.get(name="{u}_{uid}".format(u=user.username, uid=user_id))
    except Collection.DoesNotExist:
        c = Collection(name="{u}_{i}".format(u=user.username, i=user.id), created_at=timezone.now())
        c.save()

    liked = user.image_set.filter(collection=c.id)

    return render(request, 'feed/base_profile.html', {
        'liked': liked[::-1],
        'likedNum': len(liked),
        'uid': request.user.id
    })

def likeHelper(coll, selected_choice, u):
    coll.image_set.create(
        collection=coll,
        user=u,
        title=selected_choice.title,
        alt=selected_choice.alt,
        src=selected_choice.src or "",
        created_at=selected_choice.created_at,
        votes=selected_choice.votes,
        data=selected_choice.data
        )
    coll.save()

def like(request, image_id):
    image = get_object_or_404(Image, pk=image_id)
    if request.user.is_authenticated == False:
        return redirect('feed:login')

    u = get_object_or_404(User, pk=request.user.id)
    coll_exists = ""

    try:
        selected_choice = Image.objects.get(pk=request.POST['option'])
        coll_exists = Collection.objects.get(name="{u}_{i}".format(u=u.username, i=u.id))
        likeHelper(coll_exists, selected_choice, u)
    except (Collection.DoesNotExist, KeyError, Image.DoesNotExist) as e:
        coll_exists = Collection(name="{u}_{i}".format(u=u.username, i=u.id), created_at=timezone.now())
        coll_exists.save()
        likeHelper(coll_exists, selected_choice, u)
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
	return render(request=request, template_name="feed/base_register.html", context={"register_form":form})

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
        if img.votes < 0:
            img.votes = 0
        img.save()
    except (KeyError, Collection.DoesNotExist, Image.DoesNotExist) as e:
        print("Collection or Image does not exist!", e)

    return HttpResponseRedirect(reverse('feed:profile', args=(u.id,)))

def add_image(request, user_id):
    u = get_object_or_404(User, pk=user_id)
    c = Collection.objects.get(pk=1)
    title = request.POST['title']
    alt = request.POST['alt']

    # my gut wants to use ImageField but FileField with request.FILES
    # is the only way I could successfully get the user uploaded
    # image to be used in the `data` field of Image instances
    form = ModelFormWithImageField(request.POST, request.FILES)
    filename = "{path}{filename}".format(path="images/", filename=request.FILES['file'])

    if form.is_valid():
        form.save()
        try:
            filename = unidecode(filename)
            i = Image(collection=c, user=u, title=title, alt=alt, src="", created_at=timezone.now(), votes=0, data=filename)
            i.save()
        except FileNotFoundError as e:
            print("Uploaded filename differs from the image source in template", e)

    else:
        form = ModelFormWithImageField()
    
    return HttpResponseRedirect(reverse('feed:profile', args=(user_id,)))

def handle_uploaded_file(file):
    """Write uploaded file to a new file in chunks."""
    with open(file, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)

def upload_file(request, user_id):
    """Handle user uploaded CSV files."""
    if request.method == 'POST':
        u = get_object_or_404(User, pk=user_id)
        c = Collection.objects.get(pk=1)
        form = ModelFormWithFileField(request.POST, request.FILES)
       
        if form.is_valid():
            # file is saved
            form.save()

            df = read_csv("./media/files/{f}".format(f=request.FILES['file']))
            imglist = []
            for item in df.itertuples():
                imglist.append(
                    Image(
                        user=u, 
                        collection=c, 
                        title=item[1].strip(), 
                        src=item[2].strip(), 
                        alt=item[3].strip(), 
                        created_at=timezone.now(), 
                        votes=0, 
                        data=""
                    )
                )
            # do a massive insert query to Image
            bulkQuery = Image.objects.bulk_create(imglist)
            return HttpResponseRedirect(reverse('feed:profile', args=(user_id,)))
        else:
            form = ModelFormWithFileField()
    return render(request, 'feed/base_profile.html', {'form': form})