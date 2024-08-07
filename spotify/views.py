from django.shortcuts import (
    render,
    redirect ,
    get_object_or_404 
)
from django.views.generic import CreateView
from . models import SpotMusic 
from . forms import SpotMusicForm , UserRegistrationForm
from django.contrib.auth.mixins import LoginRequiredMixin
""" authentication imports"""
from django.contrib.auth import authenticate 
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from django.contrib.auth.decorators import login_required

""" User profile """
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib import messages

@login_required(login_url='login')
def home(request):
    songs = SpotMusic.objects.all()[:4]
    return render(request, 'spotify/home.html',{'all':songs})

from django.urls import reverse

class SongCreateView(LoginRequiredMixin, CreateView):
    login_url = 'login/'
    model = SpotMusic
    template_name = 'spotify/song-create.html'
    fields = ['song_author','song_title','song_image','audio']
    # success_url = '/'
    
    def get_success_url(self):
        return reverse('library')

    def form_valid(self, form):
        form.instance.user = self.request.user 
        return super().form_valid(form)
    

def playSong(request,id):
    obj = SpotMusic.objects.get(id=id)
    return render(request, 'spotify/playSong.html',{'song':obj })



# def signup(request):
#     if request.method == "POST":
#         form = UserRegistrationForm(request.POST)
#         username = request.POST.get('username')
#         print(username)
#         password1 = request.POST.get('password1')
#         print(password1)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.save()

#             if user is not None:
#                 login_user(request, user)
#                 return redirect('login')
#     else:
#         form = UserRegistrationForm()
#         return render(request, "spotify/register.html",{'form':form })
def signup(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login_user(request, user)
            return redirect('home')  # Redirect to the home page after successful signup
        else:
            # Print form errors to the console for debugging
            print("Form is not valid")
            print(form.errors)
            return render(request, "spotify/register.html", {'form': form})  # Re-render the form with errors
    else:
        form = UserRegistrationForm()
        return render(request, "spotify/register.html", {'form': form})




def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        print(password)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login_user(request, user)
            return redirect('home')
    

    return render(request, 'spotify/login.html')

def logout(request):
    logout_user(request)
    return redirect('login')


from django.views import View
from django.shortcuts import render
from .mixins import TimingMixin

class MyTimedView(TimingMixin, View):
    def get(self, request,*args, **kwargs):
        elapsed_time = 90
        y = super().log_timing(request, elapsed_time)
        # y='ll'
        
        return render(request, 'my_template.html',{'y':y})
    
@login_required(login_url='login')
def library(request):
    songs = SpotMusic.objects.all()
    return render(request, 'spotify/library.html', {'all':songs})


def user_profile(request):
    user_songs = SpotMusic.objects.filter(user=request.user)
    return render(request, 'spotify/userProfile.html', {'user_songs': user_songs})

class SongUpdateView(LoginRequiredMixin, UpdateView):
    model = SpotMusic
    fields = ['song_author', 'song_title', 'song_image', 'audio']
    template_name = 'spotify/song_update.html'
    success_url = reverse_lazy('user_profile')  # Redirect to the user profile after successful update

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)
    

def song_delete(request, pk):
    song = get_object_or_404(SpotMusic, pk=pk, user=request.user)
    song.delete()
    messages.success(request, 'Song deleted successfully.')
    return redirect('user_profile')