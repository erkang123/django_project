# Create your views here.
import markdown
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ArticlePostForm
from .models import ArticlePost
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from .models import ArticleColumn
from comment.forms import CommentForm
from django.views import View

def article_list(request):
    # 从url中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    # 初始化查询集
    article_list = ArticlePost.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title_icontains=search) |
            Q(boy_icontains=search)
        )
    else:
        search = ''
    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in = [tag])

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    paginator = Paginator(article_list,5)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column':column,
        'tag':tag,
    }

    return render(request,'article/list.html',context)

def article_detail(request,id):
    article = ArticlePost.objects.get(id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 修改 Markdown 语法渲染
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    # 引入评论表单
    comment_form = CommentForm()

    # 新增了md.toc对象
    context = {'article': article, 'toc': md.toc,'comments':comments,'comment_form':comment_form}

    return render(request, 'article/detail.html', context)

#写文章的视图
@login_required(login_url='/userprofile/login')
def article_create(request):
    if request.method == 'POST':
        # 增加 request.FILES
        article__post_form = ArticlePostForm(request.POST,request.FILES)
        if article__post_form.is_valid():
            new_article = article__post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            # 新增代码
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            # 新增代码，保存tags的多对多关系
            article__post_form.save_m2m()
            return redirect("article:article_list")
        else:
            return HttpResponse('表单内容有误，请重新填写。')
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()

        context = {'article_post_form':article_post_form,'columns':columns}
        return render(request,'article/create.html',context)
@login_required(login_url='userprofile/login')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if request.user != article.author:
            return HttpResponse("抱歉，你无权修改这篇文章.")
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

#修改文章
@login_required(login_url='userprofile/login')
def article_update(request,id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新title,body字段
    GET方法进入初始表单页面
    id: 文章的id
    """
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章.")
    if request.method == 'POST':
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            # 新增代码
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            article.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm()
        # 新增
        columns = ArticleColumn.objects.all()

        context = {'article': article,'article_post_form': article_post_form,'columns':columns}
        return render(request, 'article/update.html', context)


# 点赞数+1
class IncreaseLikeView(View):
    def post(self,request,*args,**kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')