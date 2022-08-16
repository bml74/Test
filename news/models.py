from operator import mod
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


def SET_DEFAULT_FIELD(): 
    return "-"


class Source(models.Model):

    domain = models.CharField(max_length=10000, unique=True) # Do not have to include www.
    source_name = models.CharField(max_length=10000, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    primary_language = models.CharField(max_length=10, default="en")
    source_followers = models.ManyToManyField(
        User,
        related_name="source_followers",
        default=None,
        blank=True
    )
    source_subscribers = models.ManyToManyField(
        User,
        related_name="source_subscribers",
        default=None,
        blank=True
    )

    def __str__(self):
        return self.source_name

    def get_absolute_url(self):
        return reverse('source-detail', kwargs={'pk': self.pk})


class SourceTwitterHandle(models.Model):
    twitter_handle = models.CharField(max_length=256, blank=True, null=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True, related_name="source_twitter_handle")

    def __str__(self):
        return f"Twitter handle: @{self.twitter_handle}"


class ArticleByURL(models.Model):
    
    URL = models.URLField() # Also in ArticleByTitle
    title = models.CharField(default=SET_DEFAULT_FIELD(), max_length=255) # Also in ArticleByTitle
    article_source = models.CharField(default=SET_DEFAULT_FIELD(), max_length=255) # Also in ArticleByTitle
    page_title = models.CharField(default=SET_DEFAULT_FIELD(), max_length=255) # Also in ArticleByTitle
    article_description = models.TextField(default=SET_DEFAULT_FIELD()) # Also in ArticleByTitle
    domain_source = models.CharField(max_length=255, default=SET_DEFAULT_FIELD()) # Also in ArticleByTitle
    domain_full = models.CharField(max_length=255, default=SET_DEFAULT_FIELD()) # Also in ArticleByTitle
    text = models.TextField(default=SET_DEFAULT_FIELD()) # Also in ArticleByTitle
    date_searched = models.DateTimeField(auto_now_add=True) # Also in ArticleByTitle
    article_searched_by = models.CharField(default="url", max_length=15) # Also in ArticleByTitle
    article_published_date = models.CharField(blank=True, max_length=255) # Also in ArticleByTitle
    article_author = models.CharField(blank=True, max_length=255)  # Also in ArticleByTitle

    searcher = models.ForeignKey(User, on_delete=models.CASCADE) # Also in ArticleByTitle
    article_by_url_stars = models.ManyToManyField( # Also in ArticleByTitle
        User,
        related_name="article_by_url_stars",
        default=None,
        blank=True
    )
    article_by_url_bookmarks = models.ManyToManyField(  # Also in ArticleByTitle
        User,
        related_name="article_by_url_bookmarks",
        default=None,
        blank=True
    )
    article_by_url_flags = models.ManyToManyField(  # Also in ArticleByTitle
        User,
        related_name="article_by_url_flags",
        default=None,
        blank=True
    )

    def __str__(self):
        return f"Query URL: {self.URL}"

    def get_absolute_url(self):
        return reverse('news-article-detail-by-url', kwargs={'pk': self.pk})


class ArticleByTitle(models.Model):
    """
    Has three columns that ArticleByURL does not have:
     1. query
     2. source
     3. other_source
    """

    query = models.CharField(max_length=255) # NOT IN ArticleByURL

    other_source = models.CharField(max_length=100, default="", blank=True) # NOT IN ArticleByURL
    URL = models.URLField(default=SET_DEFAULT_FIELD()) # Also in ArticleByURL
    title = models.CharField(default=SET_DEFAULT_FIELD(), max_length=255) # Also in ArticleByURL
    article_source = models.CharField(default=SET_DEFAULT_FIELD(), max_length=255) # Also in ArticleByURL
    page_title = models.CharField(default=SET_DEFAULT_FIELD(), max_length=255) # Also in ArticleByURL
    article_description = models.TextField(default=SET_DEFAULT_FIELD()) # Also in ArticleByURL
    domain_source = models.CharField(max_length=255, default=SET_DEFAULT_FIELD()) # Also in ArticleByURL
    domain_full = models.CharField(max_length=255, default=SET_DEFAULT_FIELD()) # Also in ArticleByURL
    text = models.TextField(default=SET_DEFAULT_FIELD()) # Also in ArticleByURL
    date_searched = models.DateTimeField(auto_now_add=True) # Also in ArticleByURL
    article_published_date = models.CharField(blank=True, max_length=255)  # Also in ArticleByURL
    article_author = models.CharField(blank=True, max_length=255)  # Also in ArticleByURL
    google_url = models.CharField(max_length=1023, default="") # NOT IN ArticleByURL
    article_searched_by = models.CharField(default="title", max_length=15) # Also in ArticleByURL

    searcher = models.ForeignKey(User, on_delete=models.CASCADE) # Also in ArticleByURL
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)
    article_by_title_stars = models.ManyToManyField( # Also in ArticleByURL
        User,
        related_name="article_by_title_stars",
        default=None,
        blank=True
    )
    article_by_title_bookmarks = models.ManyToManyField(  # Also in ArticleByURL
        User,
        related_name="article_by_title_bookmarks",
        default=None,
        blank=True
    )
    article_by_title_flags = models.ManyToManyField(  # Also in ArticleByURL
        User,
        related_name="article_by_title_flags",
        default=None,
        blank=True
    )

    def __str__(self):
        return f"Query: {self.query}"

    def get_absolute_url(self):
        return reverse('news-article-detail-by-title', kwargs={'pk': self.pk})


class ArticlesByTitle(models.Model):
    query = models.CharField(max_length=255)
    other_source = models.CharField(max_length=100, default="", blank=True) # NOT IN ArticleByURL
    date_searched = models.DateTimeField(auto_now_add=True)
    google_url = models.CharField(max_length=1023, default="")

    searcher = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Query: {self.query}"

    def get_absolute_url(self):
        return reverse('news-articles-detail-by-title', kwargs={'pk': self.pk})


class ArticleNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article_id = models.IntegerField(default=0)
    article_by_url = models.BooleanField(default=True) # If True, then article is by URL. Otherwise, article is by title.
    title = models.CharField(max_length=128, default="Title", blank=True, null=True)
    note = models.TextField(blank=True, null=True)


class SearchAccessRequest(models.Model):
    date_requested = models.DateTimeField(auto_now_add=True) 
    requester = models.ForeignKey(User, on_delete=models.CASCADE) 

    def get_absolute_url(self):
        return reverse('access_requests', kwargs={'pk': self.pk})


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    stars = models.IntegerField()
    article_by_url = models.BooleanField(default=True)
    article_id = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} gives {self.stars} star(s) to article by URL with id {self.article_id}" if self.article_by_url else f"{self.user.username} gives {self.stars} star(s) to article by title with id {self.article_id}"
