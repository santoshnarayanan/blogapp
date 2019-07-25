from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import  ListView  # create Class based view
from django.core.mail import send_mail
from .forms import EmailPostForm, CommentForm
from .models import Post, Comment


def post_list(request):
    # Code commented
    # posts = Post.published.all()
    # return render(request,'blog/post/list.html',{'posts': posts})

    # New code
    object_list = Post.published.all()
    paginator = Paginator(object_list,3)  # 3 post in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
       posts = paginator.page(1)  # if page is not an integer display the first page
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)  # if page is out of range then display last page
    return render(request,'blog/post/list.html',{'page': page,'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year,publish__month=month,publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create comment but do not save to DB
            new_comment = comment_form.save(commit=False)
            # Assign current post to comment
            new_comment.post = post
            # Save comment to DB
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html',{'post':post,
                                                    'comments':comments,
                                                    'new_comment': new_comment,
                                                    'comment_form':comment_form})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_share(request, post_id):
    # retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        # form to be submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields validate
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends	you	reading	" {}"'.format(cd['name'],cd['email'],post.title)
            message = 'Read "{}" at	{}\n\n{}\'s	comments: {}'.format(post.title,post_url, cd['name'],cd['comments'])
            send_mail(subject,message,'admin@myblog.com',[cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request,'blog/post/share.html',{'post': post,'form': form,'sent': sent})