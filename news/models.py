import re
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.core.exceptions import ValidationError


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def __str__(self) -> str:
        return self.authorUser.username

    def update_rating(self):     # Рейтинг состоит из следующих слагаемых:
        #  суммарный рейтинг статей автора умножается на 3;
        postRat = self.post_set.all().aggregate(sum=Sum('rating'))['sum']
        #  суммарный рейтинг все.х комментариев автора;
        userRat = self.authorUser.comment_set.all().aggregate(sum=Sum('rating'))['sum']
        #  суммарный рейтинг всех комментариев к статьям автора.
        commentRat = Comment.objects.filter(commentPost__author=self).aggregate(sum=Sum('rating'))['sum']
        self.ratingAuthor = postRat * 3 + userRat + commentRat
        self.save()


class Category(models.Model):
    categoryName = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return self.categoryName
    



def validate_comment_text(text):
    CENSORED_WORDS = [
    'мат',
    'шах',
    'бокс',
    ]
    words = set(re.sub("[^\w]", " ",  text).split())
    for word in words:
        if word in CENSORED_WORDS:
          raise ValidationError(f"{word} - плохое слово")  

    

class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPE = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость')
        ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    categoryType = models.CharField(max_length=2, choices=POST_TYPE, default=ARTICLE, verbose_name='Тип')
    dateCreation = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    postCategory = models.ManyToManyField(Category, through='PostCategory', verbose_name='Категория')
    title = models.CharField(max_length=128, verbose_name='Заголовок', validators=[validate_comment_text])
    text = models.TextField(verbose_name='Текст', validators=[validate_comment_text])
    rating = models.SmallIntegerField(default=0, verbose_name='Рейтинг')

    def __str__(self) -> str:
        return f'{self.title} {self.preview()}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...'

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk' : self.pk})
    

    def validate_comment_text(self):
        CENSORED_WORDS = []
        with open("bad_words.txt") as f:
            CENSORED_WORDS = f.readlines()
        words = set(re.sub("[^\w]", " ",  self.text).split())
        if any(censored_word in words for censored_word in CENSORED_WORDS):
            raise ValidationError(f"is censored!")

    
class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.commentUser.username

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


