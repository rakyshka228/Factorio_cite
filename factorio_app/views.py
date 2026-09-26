from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .blueprints import BLUEPRINTS
from .forms import BlueprintForm, CommentForm, RegisterForm
from .models import Blueprint, Comment, Like, Tag


def home(request):
    query = request.GET.get('q', '').strip()
    selected_tag = request.GET.get('tag', '').strip()
    user_blueprints = Blueprint.objects.select_related('author').prefetch_related('tags', 'likes')
    if query:
        user_blueprints = user_blueprints.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if selected_tag:
        user_blueprints = user_blueprints.filter(tags__slug=selected_tag)
    return render(request, 'factorio_app/home.html', {
        'blueprints': BLUEPRINTS,
        'user_blueprints': user_blueprints,
        'tags': Tag.objects.all(),
        'query': query,
        'selected_tag': selected_tag,
    })


def blueprint_detail(request, slug):
    blueprint = next((item for item in BLUEPRINTS if item['slug'] == slug), None)
    if blueprint is None:
        return render(request, 'factorio_app/404.html', status=404)
    return render(request, 'factorio_app/blueprint_detail.html', {'blueprint': blueprint})


def user_blueprint_detail(request, pk):
    blueprint = get_object_or_404(
        Blueprint.objects.select_related('author').prefetch_related('tags', 'comments__user', 'likes'),
        pk=pk,
    )
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'/login/?next={request.path}')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.blueprint = blueprint
            comment.save()
            return redirect(blueprint.get_absolute_url())
    else:
        form = CommentForm()
    return render(request, 'factorio_app/user_blueprint_detail.html', {
        'blueprint': blueprint,
        'comment_form': form,
        'liked': request.user.is_authenticated and blueprint.likes.filter(user=request.user).exists(),
    })


@login_required
def toggle_like(request, pk):
    blueprint = get_object_or_404(Blueprint, pk=pk)
    if request.method == 'POST':
        like, created = Like.objects.get_or_create(user=request.user, blueprint=blueprint)
        if not created:
            like.delete()
    return redirect(blueprint.get_absolute_url())


@login_required
def create_blueprint(request):
    if request.method == 'POST':
        form = BlueprintForm(request.POST, request.FILES)
        if form.is_valid():
            blueprint = form.save(request.user)
            messages.success(request, 'Чертёж опубликован.')
            return redirect(blueprint.get_absolute_url())
    else:
        form = BlueprintForm()
    return render(request, 'factorio_app/blueprint_form.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    blueprints = author.blueprints.prefetch_related('tags', 'likes').annotate(comment_total=Count('comments'))
    return render(request, 'factorio_app/profile.html', {
        'author': author,
        'blueprints': blueprints,
        'blueprint_count': blueprints.count(),
        'like_count': Like.objects.filter(blueprint__author=author).count(),
        'comment_count': Comment.objects.filter(blueprint__author=author).count(),
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
