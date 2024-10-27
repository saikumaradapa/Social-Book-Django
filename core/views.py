from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowerCount



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

from icecream import ic 
import random


@login_required(login_url='signin')
def index(request):
    user = request.user
    user_profile = Profile.objects.get(user=user)
    
    # Retrieve all posts and their associated profile images
    posts = Post.objects.all()
    posts_with_profiles = [
        {
            'post': post,
            'profile_img': Profile.objects.get(user__username=post.user).profileimg.url
        }
        for post in posts
    ]
    random.shuffle(posts_with_profiles)

    # Get the list of users the current user is following
    following = FollowerCount.objects.filter(follower=user.username).values_list('user', flat=True)
    
    # Suggest profiles not yet followed by the current user
    suggestions_list = Profile.objects.exclude(user__username__in=following).exclude(user=user)

    # ic(suggestions_list)
    
    return render(request, 'index.html', {
        'user_profile': user_profile,
        'posts_with_profiles': posts_with_profiles,
        'suggestions_list': suggestions_list,
    })





def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Already Taken!")            
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Already Taken!")
                return redirect('signup')    
            else:
                user = User.objects.create_user(username=username, email=email, password=password)            
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)                
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, "Password Should Match with Confirm Password!")
            return redirect('signup')    
    return render(request, 'signup.html')

def signin(request):    
    # ic(request.method)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid Credentials!')
            return redirect('/signin')
    else:
        return render(request, 'signin.html')
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('/signin')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        image = request.FILES.get('image', user_profile.profileimg)
        bio = request.POST.get('bio', user_profile.bio)
        location = request.POST.get('location', user_profile.location)

        # ic(location)
        # ic(bio)
        # Update user profile fields
        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location 
        user_profile.save()

        return redirect('/settings')  # Should stay on settings page after updating

    return render(request, 'setting.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        # ic(request.POST)
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')

    else:
        return redirect('/')
    

@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    followers = FollowerCount.objects.filter(user=user_object)
    followers_count = len(followers)
    following = FollowerCount.objects.filter(follower=user_object)
    following_count = len(following)

    follower = request.user.username 
    user = pk

    if FollowerCount.objects.filter(follower=follower, user=user).first():
        follow_text = "Unfollow"
    else:
        follow_text = "Follow"

    context = {
        'user_object' : user_object,
        'user_profile' : user_profile,
        'user_posts' : user_posts,
        'user_post_length' : user_post_length,
        'followers_count' : followers_count,
        'following_count' : following_count,
        'follow_text' : follow_text,
    }

    return render(request, 'profile.html', context)  

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowerCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowerCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowerCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)
        


    else:
        return redirect('/')
    

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        user_profile_ids = [user.id for user in username_object]

        username_profiles = []
        for id in user_profile_ids:
            username_profile = Profile.objects.filter(id_user=id)
            # ic(id, username_profile)
            username_profiles.extend(username_profile)  # Use extend to add profiles directly        
        
        context = {
            'user_profile' : user_profile,
            'username_profiles': username_profiles, 
            'username':username, 
            }
        return render(request, 'search.html', context)
    else:
        return redirect('/')
