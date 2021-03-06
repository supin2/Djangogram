from django.db.models import Q
from djangogram.users.models import User as user_model
from django.shortcuts import get_object_or_404, redirect, render, redirect
from django.urls import reverse

from . import models, serializers
from .forms import CreatePostForm, UpdatePostForm, CommentForm

# Create your views here.
def index(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            comment_form = CommentForm()

            user = get_object_or_404(user_model, pk=request.user.id)
            following = user.following.all()
            posts = models.Post.objects.filter(
                Q(author__in=following) | Q(author=user)
            ).order_by("-create_at")

            serializer = serializers.PostSerializer(posts, many=True) # 피드에 보여지는 포스트가 여러개일 수도 있으니 many=True 옵션 추가
            # print(serializer.data)

            return render(request, 'posts/main.html', {"posts": serializer.data, "comment_form": comment_form})
    
    return render(request, 'posts/main.html')


def post_create(request):
    if request.method == 'GET':
        form = CreatePostForm()
        return render(request, 'posts/post_create.html', {"form" : form})

    elif request.method == 'POST':
        if request.user.is_authenticated:
            user = get_object_or_404(user_model, pk=request.user.id)
            # image = request.FILES['image']
            # caption = request.POST['caption']

            # new_post = models.Post.objects.create(
            #     author = user,
            #     image = image,
            #     caption = caption
            # )
            # new_post.save()

            form = CreatePostForm(request.POST, request.FILES)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = user
                post.save()
            else:
                print(form.errors)

            return render(request, 'posts/main.html')

        else:
            return render(request, 'users/main.html')

def post_delete(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(models.Post, pk=post_id)
        if request.user != post.author:
            return redirect(reverse('posts:index'))

        if request.method == 'GET':
            return render(request, 'posts/post_confirm_delete.html')
            
        elif request.method == 'POST':
            post.delete()
            return redirect(reverse('posts:index'))
        
    else:
        return render(request, 'users/main.html')


def post_update(request, post_id):
    if request.user.is_authenticated:
        # 작성자 체크
        post = get_object_or_404(models.Post, pk=post_id)
        if request.user != post.author:
            return redirect(reverse('posts:index'))

        # GET 요청
        if request.method == 'GET':
            form = UpdatePostForm(instance=post)
            return render(request, 'posts/post_update.html', {"form": form, "post": post})

        elif request.method == 'POST':
            # 업데이트 버튼 클릭 후 저장을 위한 POST API 요청 로직
            form = UpdatePostForm(request.POST)
            if form.is_valid():
                post.caption = form.cleaned_data['caption']
                post.save()
            
            return redirect(reverse('posts:index'))

    else:
        return render(request, 'users/main.html')

def comment_create(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(models.Post, pk=post_id)

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.posts = post
            comment.save()

            return redirect(reverse('posts:index') + "#comment-" + str(comment.id))

        else:
            return render(request, 'users/main.html')

def comment_delete(request, comment_id):
    if request.user.is_authenticated:
        comment = get_object_or_404(models.Comment, pk=comment_id)
        if request.user == comment.author:
            comment.delete()
        
        return redirect(reverse('posts:index'))

    else:
        return render(request, 'users/main.html')