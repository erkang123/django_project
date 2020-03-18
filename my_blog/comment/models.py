from django.db import models
from django.contrib.auth.models import User
from article.models import ArticlePost
from ckeditor.fields import RichTextField
from mptt.models import MPTTModel,TreeForeignKey
# Create your models here.

# 替换 models.Model 为 MPTTModel
class Comment(MPTTModel):
    article = models.ForeignKey(
        ArticlePost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    #新增，mptt树形结构
    parent = TreeForeignKey(
        'self',
        on_delete= models.CASCADE,
        null= True,
        blank= True,
        related_name= 'children'
    )
    # 新增，二级评论给谁，str
    reply_to = models.ForeignKey(
        User,
        null= True,
        blank= True,
        on_delete= models.CASCADE,
        related_name= 'replyers'
    )

    # body = models.TextField()
    body = RichTextField()
    created = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     ordering = ('created',)
    class MPTTMeta:
        order_insertion_by = ['created']
    def __str__(self):
        return self.body[:20]