from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm


def index(request):
    # в posts будет сохранена выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date по убыванию
    post_list = Post.objects.select_related('group')
    # В словаре context отправляем информацию в шаблон
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author__username=username)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user_posts = post_list.count()
    context = {
        'author': author,
        'page_obj': page_obj,
        'post_list': post_list,
        'user_posts': user_posts,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    form = PostForm(
        data=request.POST or None,
    )

    if request.method != 'POST' or not form.is_valid():
        context = {'form': form, 'is_edit': False}
        return render(request, 'posts/create_post.html', context)

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post.id)

    form = PostForm(
        data=request.POST or None,
        instance=post,
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)

    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    template = 'posts/create_post.html'
    return render(request, template, context)
