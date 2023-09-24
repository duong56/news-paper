from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
import json
from newsApp import models, forms
from about.models import Partner, AboutContent
from django.utils import translation

def context_data():
    context = {
        'site_name': 'Simple News Portal',
        'page' : 'home',
        'page_title' : 'News Portal',
        'categories' : models.Category.objects.filter(status = 1).all(),
        'banners': models.Banner.objects.all()
    }
    return context

def about_context_data():
    posts = models.Post.objects.filter(status = 1).order_by('-date_created').all()
    context = {
        'site_name': ' About page',
        'about_content': AboutContent.objects.first(),
        'about_partner': Partner.objects.all(),
        'latest_top': posts[:2]
    }
    return context

# Create your views here.
def home(request):
    # user_language = 'vi'
    # translation.activate(user_language)
    # request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    # if translation.LANGUAGE_SESSION_KEY in request.session:
    #     del request.session[translation.LANGUAGE_SESSION_KEY]

    context = context_data()
    posts = models.Post.objects.filter(status = 1).order_by('-date_created').all()
    category_posts = models.Category.objects.filter(status = 1).all()
    context['page'] = 'home'
    context['page_title'] = 'Home'
    context['latest_top'] = posts[:2]
    context['latest_bottom'] = posts[2:12]
    list_category = []
    for category in category_posts:
        list_category.append({
            'category_id': category.id,
            'name': category.name,
            'list_post': models.Post.objects.filter(category_id = category.id).all()
        })
    context['list_category'] = list_category
    return render(request, 'home.html', context)

#about
def about(request):
    context = about_context_data()
    return render(request, 'about.html', context)

#login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')


@login_required
def update_profile(request):
    context = context_data()
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id = request.user.id)
    if not request.method == 'POST':
        form = forms.UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = forms.UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile-page")
        else:
            context['form'] = form
            
    return render(request, 'update_profile.html',context)


@login_required
def update_password(request):
    context = context_data()
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = forms.UpdatePasswords(user = request.user, data= request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile-page")
        else:
            context['form'] = form
    else:
        form = forms.UpdatePasswords(request.POST)
        context['form'] = form
    return render(request,'update_password.html',context)

@login_required
def profile(request):
    context = context_data()
    context['page'] = 'profile'
    context['page_title'] = "Profile"
    return render(request,'profile.html', context)

@login_required
def manage_post(request, pk = None):
    context = context_data()
    if not pk is None:
        context['page']='edit_post'
        context['page_title']='Edit Post'
        context['post']=models.Post.objects.get(id=pk)
    else:
        context['page']='new_post'
        context['page_title']='New Post'
        context['post']={}

    return render(request, 'manage_post.html',context)

@login_required
def save_post(request):
    resp={'status':'failed', 'msg':'','id':None}
    if request.method == 'POST':
        if request.POST['id'] == '':
            form = forms.savePost(request.POST, request.FILES)
        else:
            post = models.Post.objects.get(id=request.POST['id'])
            form = forms.savePost(request.POST, request.FILES, instance= post)
    
        if form.is_valid():
            form.save()
            if request.POST['id'] == '':
                postID = models.Post.objects.all().last().id
            else:
                postID = request.POST['id']
            resp['id'] = postID
            resp['status'] = 'success'
            messages.success(request, "Post has been saved successfully.")
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.label}] {error}")

    else:
        resp['msg'] = "Request has no data sent."
    return HttpResponse(json.dumps(resp), content_type="application/json")


def view_post(request, pk=None):
    context = context_data()
    post = models.Post.objects.get(id = pk)
    context['page'] = 'post'
    context['page_title'] = post.title
    context['post'] = post
    context['latest'] = models.Post.objects.exclude(id=pk).filter(status = 1).order_by('-date_created').all()[:10]
    context['comments'] = models.Comment.objects.filter(post=post).all()
    context['actions'] = False
    if request.user.is_superuser or request.user.id == post.user.id:
        context['actions'] = True
    return render(request, 'single_post.html', context)

def save_comment(request):
    resp={'status':'failed', 'msg':'','id':None}
    if request.method == 'POST':
        if request.POST['id'] == '':
            form = forms.saveComment(request.POST)
        else:
            comment = models.Comment.objects.get(id=request.POST['id'])
            form = forms.saveComment(request.POST, instance= comment)
    
        if form.is_valid():
            form.save()
            if request.POST['id'] == '':
                commentID = models.Post.objects.all().last().id
            else:
                commentID = request.POST['id']
            resp['id'] = commentID
            resp['status'] = 'success'
            messages.success(request, "Comment has been saved successfully.")
        else:
            for field in form:
                for error in field.errors:
                    if not resp['msg'] == '':
                        resp['msg'] += str('<br />')
                    resp['msg'] += str(f"[{field.label}] {error}")

    else:
        resp['msg'] = "Request has no data sent."
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def list_posts(request):
    context = context_data()

    # allposts = models.Post.objects.filter(status = 1, category = category).all()
    # page = request.GET.get('page', 1)
    # paginator = Paginator(allposts, 1)

    # try:
    #     allposts = paginator.page(page)
    # except PageNotAnInteger:
    #     allposts = paginator.page(1)
    # except EmptyPage:
    #     allposts = paginator.page(paginator.num_pages)

    # context["allposts"] = allposts
    context['page'] = 'all_post'
    context['page_title'] = 'News'
    if request.user.is_superuser:
        context['posts'] = models.Post.objects.order_by('-date_created').all()
    else:
        context['posts'] = models.Post.objects.filter(user=request.user).all()

    context['latest'] = models.Post.objects.filter(status = 1).order_by('-date_created').all()[:10]
    
    return render(request, 'posts.html', context)


def category_posts(request,pk=None):
    context = context_data()
    if pk is None:
        messages.error(request,"File not Found")
        return redirect('home-page')
    try:
        category = models.Category.objects.get(id=pk)
    except:
        messages.error(request,"File not Found")
        return redirect('home-page')
    
    posts = models.Post.objects.filter(status = 1, category = category).all()
    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # post_return = paginatior.page(1)

    context['category'] = category
    context['page'] = 'category_post'
    context['page_title'] = f'{category.name} Posts'
    context['posts'] = posts
        
    context['latest'] = models.Post.objects.filter(status = 1).order_by('-date_created').all()[:10]
    
    return render(request, 'category.html', context)

@login_required
def delete_post(request, pk = None):
    resp = {'status':'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Post ID is Invalid'
        return HttpResponse(json.dumps(resp), content_type="application/json")
    try:
        post = models.Post.objects.get(id=pk)
        post.delete()
        messages.success(request, "Post has been deleted successfully.")
        resp['status'] = 'success'
    except:
        resp['msg'] = 'Post ID is Invalid'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_comment(request, pk = None):
    resp = {'status':'failed', 'msg':''}
    if pk is None:
        resp['msg'] = 'Comment ID is Invalid'
        return HttpResponse(json.dumps(resp), content_type="application/json")
    try:
        comment = models.Comment.objects.get(id=pk)
        comment.delete()
        messages.success(request, "Comment has been deleted successfully.")
        resp['status'] = 'success'
    except:
        resp['msg'] = 'Comment ID is Invalid'
    
    return HttpResponse(json.dumps(resp), content_type="application/json")

def search_new(request, pk = None):

    # allposts = models.Post.objects.all()
    # page = request.GET.get('page', 1)
    # paginator = Paginator(allposts, 1)

    # try:
    #     allposts = paginator.page(page)
    # except PageNotAnInteger:
    #     allposts = paginator.page(1)
    # except EmptyPage:
    #     allposts = paginator.page(paginator.num_pages)

    if request.method == "POST":
        searched = request.POST['searched']
        posts = models.Post.objects.filter(title__contains=searched)


        return render(request, 'posts.html', {'searched': searched, 'posts': posts, 'page_title': 'Search for ' + searched})
    else:
        return render(request, 'posts.html', {})