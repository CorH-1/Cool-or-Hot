#posts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Post, PostImage, PostComment, Group, GroupImage, GroupComment
from .forms import PostForm, PostImageFrom, PostCommentForm, GroupForm, GroupImageFrom, GroupCommentForm
from django.db.models import Q

# Create your views here.
# 1 index
def index(request):
    posts = Post.objects.all()
    context ={
        'posts': posts,
    }
    return render(request,'posts/index.html', context)

# 2 post_detail 내용 조회
def post_detail(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    post_images = PostImage.objects.filter(post=post)
    post_comments = post.postcomment_set.all()
    post_comment_form = PostCommentForm()

    tags = post.tags.all()

    session_key = 'post_{}_hits'.format(post_pk)
    if not request.session.get(session_key):
        post.hits += 1
        post.save()
        request.session[session_key] = True

    context = {
        'post': post,
        'post_images': post_images,
        'post_comments': post_comments,
        'post_comment_form': post_comment_form,
        'tags' : tags,
    }
    return render(request,'posts/post_detail.html', context)

# 3 post_create 생성
@login_required
def post_create(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        post_image_form = PostImageFrom(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        tags = request.POST.get('tags', '').split(',')

        if post_form.is_valid() and post_image_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()

            for tag in tags:
                post.tags.add(tag.strip())

            for file in files:
                PostImage.objects.create(post=post, image=file)

            return redirect('posts:post_detail', post.pk)
    else:
        post_form = PostForm()
        post_image_form = PostImageFrom()
    context = {
        'post_form': post_form,
        'post_image_form': post_image_form, 
    }
    return render(request,'posts/post_create.html', context)

# 4 post_delete 삭제
@login_required
def post_delete(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    if request.user == post.user:
        post.delete()
    return redirect('posts:index')

# 5 post_update 수정
@login_required
def post_update(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    post_images = PostImage.objects.filter(post=post)
    if request.user == post.user:
        if request.method == 'POST':
            post_form = PostForm(request.POST, instance=post)
            post_image_form = PostImageFrom(request.POST, request.FILES)
            files = request.FILES.getlist('image')
            if post_form.is_valid() and post_image_form.is_valid():
                post_form = post_form.save(commit=False)
                post.user = request.user
                post.save()
                post.tags.clear()
                tags = request.POST.get('tags').split(',')

                for tag in tags:
                    post.tags.add(tag.strip())

                 # 기존 이미지 삭제
                post_images = PostImageFrom.objects.filter(post=post)
                for img in post_images:
                    img.delete()

                for file in files:
                    PostImage.objects.create(post=post, image=file)

                return redirect('posts:post_detail', post.pk)
        else:
            post_form = PostForm(instance=post)
            post_image_form = PostImageFrom()
    else:
        return redirect('posts:index')
    context ={
        'post': post,
        'post_form': post_form,
        'post_image_form': post_image_form,
    }
    return render(request, 'posts/post_update.html', context)


@login_required
def post_comments_create(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    post_comment_form = PostCommentForm(request.POST)
    if post_comment_form.is_valid():
        post_comment = post_comment_form.save(commit=False)
        post_comment.post = post
        post_comment.user = request.user
        post_comment.save()
        return redirect('posts:post_detail', post_pk)
    context = {
        'post': post,
        'post_comment_form': post_comment_form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_comments_delete(request, post_pk, comment_pk):
    post_comment = PostComment.objects.get(pk=comment_pk)
    if request.user == post_comment.user:
        post_comment.delete()
    return redirect('posts:post_detail', post_pk)


# def post_comments_update(request, post_pk, comment_pk):
#     return render(request, 'posts/post_detail.html', context)


def post_likes(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    if request.user in post.like_users.all():
        post.like_users.remove(request.user)
        is_liked = False
    else:
        post.like_users.add(request.user)
        is_liked = True
    context = {
        'is_liked': is_liked,
    }
    return JsonResponse(context)


# 카카오 지도 api
@login_required
def where(request) :
    group_data = get_group_data()
    context = {
        'group_data' : group_data
    }
    return render(request, 'posts/where.html', context)

def get_group_data():
    group_data = []
    groups = Group.objects.all()
    
    for group in groups:
        data = {
            'title': group.title,
            'content': group.content,
            'category': group.category,
            'day': group.day,
            'region': group.region,
            'gender': group.gender,
            'Propensity': group.Propensity,
            'address': group.address,
        }
        group_data.append(data)
    
    return group_data


# group_list
def group_list(request):
    groups = Group.objects.all()
    context ={
        'groups': groups,
    }
    return render(request,'posts/group_list.html', context)


# group_detail 내용 조회
def group_detail(request, group_pk):
    group = Group.objects.get(pk=group_pk)
    group_images = GroupImage.objects.filter(group=group)
    group_comments = group.groupcomment_set.all()
    group_comment_form = GroupCommentForm()

    tags = group.tags.all()

    session_key = 'group_{}_hits'.format(group_pk)
    if not request.session.get(session_key):
        group.hits += 1
        group.save()
        request.session[session_key] = True

    context = {
        'group': group,
        'group_images': group_images,
        'group_comments': group_comments,
        'group_comment_form': group_comment_form,
        'tags': tags,
    }
    return render(request, 'posts/group_detail.html', context)


# group_create 생성
@login_required
def group_create(request):
    if request.method == 'POST':
        group_form = GroupForm(request.POST)
        group_image_form = GroupImageFrom(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        tags = request.POST.get('tags', '').split(',')

        if group_form.is_valid() and group_image_form.is_valid():
            category = request.POST.get('category')
            group = group_form.save(commit=False)
            group.user = request.user
            group.save()

            for tag in tags:
                group.tags.add(tag.strip())

            for file in files:
                GroupImage.objects.create(group=group, image=file)
            
            return redirect('posts:group_detail', group.pk)
    else:
        group_form = GroupForm()
        group_image_form = GroupImageFrom()
    context = {
        'group_form': group_form,
        'group_image_form': group_image_form,
    }
    return render(request, 'posts/group_create.html', context)


# group_delete 삭제
@login_required
def group_delete(request, group_pk):
    group = Group.objects.get(pk=group_pk)
    if request.user == group.user:
        group.delete()
    return redirect('posts:group_list')


# group_update 수정
@login_required
def group_update(request, group_pk):
    group = Group.objects.get(pk=group_pk)
    group_images = GroupImage.objects.filter(group=group)

    if request.user == group.user:
        if request.method == 'POST':
            group_form = GroupForm(request.POST, instance=group)
            group_image_form = GroupImageFrom(request.POST, request.FILES)

            if group_form.is_valid() and group_image_form.is_valid():
                group = group_form.save(commit=False)
                group.user = request.user
                group.save()

                tags = request.POST.get('tags', '').split(',')
                group.tags.clear()

                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        group.tags.add(tag)

                files = request.FILES.getlist('image')
                GroupImage.objects.filter(group=group).delete()
                for file in files:
                    GroupImage.objects.create(group=group, image=file)

                return redirect('posts:group_detail', group.pk)
        else:
            group_form = GroupForm(instance=group)
            group_image_form = GroupImageFrom()
        context = {
            'group': group,
            'group_form': group_form,
            'group_image_form': group_image_form,
        }
        return render(request, 'posts/group_update.html', context)
    

# group_comments_create 그룹(모임) 댓글 작성
@login_required
def group_comments_create(request, group_pk):
    group = Group.objects.get(pk=group_pk)
    group_comment_form = GroupCommentForm(request.POST)
    
    if group_comment_form.is_valid():
        group_comment = group_comment_form.save(commit=False)
        group_comment.group = group
        group_comment.user = request.user
        group_comment.save()
        return redirect('posts:group_detail', group_pk)
    context = {
        'group': group,
        'group_comment_form': group_comment_form,
    }
    return render(request, 'posts/group_detail.html', context)


# group_comments_delete 그룹(모임) 댓글 삭제
@login_required
def group_comments_delete(request, group_pk, comment_pk):
    group_comment = GroupComment.objects.get(pk=comment_pk)
    if request.user == group_comment.user:
        group_comment.delete()
    return redirect('posts:group_detail', group_pk)


# group_likes 그룹(모임) 좋아요
def group_likes(request, group_pk):
    group = Group.objects.get(pk=group_pk)
    if request.user in group.like_users.all():
        group.like_users.remove(request.user)
        is_liked = False
    else:
        group.like_users.add(request.user)
        is_liked = True
    context = {
        'is_liked': is_liked,
    }
    return JsonResponse(context)


# search 검색
def search(request):
    query = None
    post_search_list = None
    group_search_list = None

    if 'q' in request.GET:
        query = request.GET.get('q')
        post_search_list = Post.objects.filter(
            Q(title__icontains=query)
        ).distinct()
        group_search_list = Group.objects.filter(
            Q(title__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'post_search_list': post_search_list,
        'group_search_list': group_search_list,
    }
    return render(request, 'posts/search.html', context)


# category 카테고리
def category(request, subject):
    posts = Post.objects.filter(category=subject)
    groups = Group.objects.filter(category=subject)
    context = {
        'posts': posts,
        'groups': groups,
        'category_subject': subject,
    }
    return render(request, 'posts/category.html', context)