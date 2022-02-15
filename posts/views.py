from django.db.models import Count, Q
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CommentForm, PostForm
from .models import Post, PostView
from accounts.models import Author


def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

def get_category_count():
    context = Post \
        .objects \
        .values('categories__title') \
        .annotate(Count('categories__title'))
    return context

def get_tag_count():
    context = Post \
        .objects \
        .values('tags__title') \
        .annotate(Count('tags__title'))
    return context


class SearchView(View):
    def get(self, request, *args, **kwargs):
        search_result = Post.objects.all()
        query = request.GET.get('q')
        if query:
             search_result = search_result.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            ).distinct()
        context = {
            "search_result": search_result
        }
        return render(request, 'search.html', context)


def search(request):
    search_result = Post.objects.all()
    query = request.GET.get('q')
    if query:
         search_result =  search_result.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).distinct()
    context = {
       "search_result": search_result
    }
    return render(request, 'search.html', context)


class IndexView(View):

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        context = {
            'posts': posts,
        }
        return render(request, 'index.html', context)

def index(request):
    posts = Post.objects.all()
    context = {
        'object_list': posts,
    }
    return render(request, 'index.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog.html'
    context_object_name = 'post'
    paginate_by = 1

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        tag_count = get_tag_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context['posts']= Post.objects.all()
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] = category_count
        context['tag_count'] = tag_count
        return context


def post_list(request):
    category_count = get_category_count()
    tag_count = get_tag_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 1)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_post = paginator.page(page)
    except PageNotAnInteger:
        paginated_post = paginator.page(1)
    except EmptyPage:
        paginated_post = paginator.page(paginator.num_pages)

    context = {
        'post': paginated_post,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count,
        'tag_count' : tag_count,
    }
    return render(request, 'blog.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    form = CommentForm()

    def get_context_data(self, **kwargs):
        tag_count = get_tag_count()
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] = category_count
        context['tag_count'] = tag_count
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            post = self.get_object()
            form.instance.user = get_author(self.request.user)
            form.instance.post = post
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'pk': post.pk
            }))


def post_detail(request, id):
    category_count = get_category_count()
    tag_count = get_tag_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)

    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': post.pk
            }))
    context = {
        'post': post,
        'most_recent': most_recent,
        'category_count': category_count,
        'tag_count' : tag_count,
        'form': form
    }
    return render(request, 'post.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse("post-detail", kwargs={
            'pk': form.instance.pk
        }))


def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse("post-detail", kwargs={
            'pk': form.instance.pk
        }))


def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "post_create.html", context)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = '/blog'
    template_name = 'post_confirm_delete.html'


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("post-list"))
