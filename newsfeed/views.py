import feedparser
from .models import Feed
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)


def feed_home(request):

    # Example:
    url = "https://feeds.a.dj.com/rss/RSSOpinion.xml"
    full_feed = feedparser.parse(url)



    items = []
    for index, entry in enumerate(full_feed.entries):

        item = {
            "id": entry.get('id'),
            "title": entry.get('title'),
            "title_detail": entry.get('title_detail'),
            "published": entry.get('published'),
            "published_parsed": entry.get('published_parsed'),
            "description": entry.get('description'),
            "summary": entry.get('summary'),
            "summary_detail": entry.get('summary_detail'),
            "guidislink": entry.get('guidislink'),
            "link": entry.get('link'),
            "links": entry.get('links'),
            "media_content": entry.get('media_content'),
            'media_credit': entry.get('media_credit'),
            'credit': entry.get('credit')
        }
        try:
            item['image'] = entry.get('media_content')[0].get('url')
        except:
            item['image'] = None



        items.append(item)

    context = {
        "items": items,
        "feed_title": full_feed.feed.get('title'),
        "feed_description": full_feed.feed.get('description'),
        "feed_link": full_feed.feed.get('link'),
        "feed_published": full_feed.feed.get('published')
    }
    return render(request, "newsfeed/feed_home.html", context)


def single_feed(request, pk):
    feed = Feed.objects.filter(id=pk)[0]
    url = feed.url
    full_feed = feedparser.parse(url)

    items = []
    for index, entry in enumerate(full_feed.entries):

        item = {
            "id": entry.get('id'),
            "title": entry.get('title'),
            "title_detail": entry.get('title_detail'),
            "published": entry.get('published'),
            "published_parsed": entry.get('published_parsed'),
            "description": entry.get('description'),
            "summary": entry.get('summary'),
            "summary_detail": entry.get('summary_detail'),
            "guidislink": entry.get('guidislink'),
            "link": entry.get('link'),
            "links": entry.get('links'),
            "media_content": entry.get('media_content'),
            'media_credit': entry.get('media_credit'),
            'credit': entry.get('credit')
        }
        try:
            item['image'] = entry.get('media_content')[0].get('url')
        except:
            item['image'] = None



        items.append(item)

    context = {
        "items": items,
        "feed_title": full_feed.feed.get('title'),
        "feed_description": full_feed.feed.get('description'),
        "feed_link": full_feed.feed.get('link'),
        "feed_published": full_feed.feed.get('published')
    }

    print(context['feed_title'])
    return render(request, "newsfeed/feed.html", context)


class FeedDetailView(LoginRequiredMixin, DetailView):
    model = Feed

    def get(self, request, *args, **kwargs):
        feed = get_object_or_404(Feed, pk=kwargs['pk'])
        context = {
            "feed": feed
        }
        return render(request, 'newsfeed/feed_detail.html', context)


class FeedCreateView(LoginRequiredMixin, CreateView):
    model = Feed
    fields = ["title", "url", "source"] 
    template_name = 'malagosto/ecole/FORM_VIEW_BASE.html'

    def test_func(self):
        return self.request.user.is_superuser

class FeedUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Feed
    fields = ["title", "url", "source"]
    template_name = 'malagosto/ecole/FORM_VIEW_BASE.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser
