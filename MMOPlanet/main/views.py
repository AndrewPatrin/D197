from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.views.generic import UpdateView, CreateView
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from .decorators import user_permission_to_edit
from .models import Post, Category, Comment
from .forms import PostForm, PostEditForm, CommentForm, SubscribeForm


def home_page(request, category = None):
    if not category:
        posts = Post.objects.order_by('-published_date')
    else:
        posts = Post.objects.filter(category=Category.objects.get(category_slug=category)).order_by('-published_date')
    paginator = Paginator(posts, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    posts_to_list = [i for i in page_obj]

    if len(posts_to_list) % 2 == 0:
        posts_list = [[posts_to_list[i], posts_to_list[i+1]] for i in range(0, len(posts_to_list), 2)]
    else:
        posts_list = [[posts_to_list[i], posts_to_list[i + 1]] for i in range(0, len(posts_to_list)-1, 2)]
        posts_list.append([posts_to_list[-1]])

    categories = Category.objects.all()
    template_name = 'posts/posts.html'

    return render(
        request,
        template_name,
        {'paginator': paginator, 'page_obj': page_obj,'categories': categories, 'list': posts_list}
    )


def post_page(request, post: str):
    post = Post.objects.filter(slug=post).first()
    categories = Category.objects.all()
    template_name = 'post/post.html'

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment.objects.create(post=post, user=request.user, comment_text=form.cleaned_data['comment_text'])
            if post.user == request.user:
                comment.accepted = True
                comment.save()
            else:
                messages.success(request, f"Your comment was sent. Wait for accept from post's author.")
            return redirect(f'/posts/{post.slug}')
    form = CommentForm()
    return render(
        request,
        template_name,
        context={'post': post, 'categories': categories, 'form': form}
    )


class PostCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post/post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.user = self.request.user
        return super().form_valid(form)


@method_decorator(user_permission_to_edit, name='dispatch')
class PostEdit(UpdateView):
    form_class = PostEditForm
    model = Post
    template_name = 'post/post_edit.html'

@login_required
def delete_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    user_posts = request.user.post_set.all()
    if comment.post in user_posts or comment.user.pk == request.user.pk:
        comment.delete()
    return redirect('/account/')

@login_required
def accept_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    user_posts = request.user.post_set.all()
    if comment.post in user_posts or comment.user.pk != request.user.pk:
        msg = EmailMultiAlternatives(
            subject=f"""Your comment was accepted""",
            body=f"""Hello, {comment.user.username}! Author "{request.user.username}" accepted your comment \
"{comment.comment_text}" on post "{comment.post.title}" """,
            from_email='newspaper.main@yandex.ru',
            to=[comment.user.email]
        )
        msg.send()
        comment.accepted = True
        comment.save()
    return redirect('/account/')

@login_required
def subscribe(request):
    form = SubscribeForm(request.POST)
    if form.is_valid():
        print(form.cleaned_data['name'])
        print(form.cleaned_data['rpath'])
        Category.objects.get(
            name=form.cleaned_data['name']).users.add(request.user)
    return redirect(form.cleaned_data['rpath'])
