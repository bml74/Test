from .models import ArticleByTitle, ArticlesByTitle, Source, ArticleByURL, ArticleNote, SearchAccessRequest, Rating, SET_DEFAULT_FIELD
from .utils import (
    ReadabilityArticle, 
    get_article_data, 
    get_custom_scrape_article_data, 
    save_and_get_dict_for_rendering_article, 
    get_languages,
    scrape_search_single_article, 
    scrape_search_multiple_articles, 
    scrape_google_search_result_description, 
    get_wikipedia_summary, 
    get_google_or_wikipedia_summary, 
    get_google_url

)
from config.utils import is_ajax
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from urllib.parse import urlparse
import wikipedia, wikipediaapi
from googletrans import Translator


def user_has_news_search_access(request):
    return request.user.groups.filter(name='News Search').exists()
    

@login_required
def news_home(request):
    if user_has_news_search_access(request):
        return render(request, 'news/home.html')
    else:
        raise PermissionDenied()


@login_required
def delete_access(request):
    if request.user.groups.filter(name='News Search').exists():
        search_access_group = Group.objects.get(name='News Search') 
        search_access_group.user_set.remove(request.user) # Remove access
    return redirect('index')


@login_required
def request_access(request):
    search_access_group = Group.objects.get(name='News Search') 
    if SearchAccessRequest.objects.filter(requester=request.user).exists(): # If there is already a request from this user.
        access_request = SearchAccessRequest.objects.filter(requester=request.user).first()
        access_request.delete()
        messages.info(request, f'Access request deleted.')
    else:
        access_add_request = SearchAccessRequest(requester=request.user) # Add request to DB
        access_add_request.save()
        messages.info(request, f'Access request sent.')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


class AccessRequestsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'news/access_requests.html'
    context_object_name = 'items'

    def get_queryset(self):
        return SearchAccessRequest.objects.order_by('-date_requested')

    def test_func(self):
        return self.request.user.is_superuser and user_has_news_search_access(self.request)


@login_required
def grant_access(request, id):
    """Only available to superusers."""
    requester = get_object_or_404(User, id=id)
    search_access_group = Group.objects.get(name='News Search') 
    search_access_group.user_set.add(requester) # Add access
    messages.success(request, f'Access granted to {requester.username}.')
    access_request = SearchAccessRequest.objects.filter(requester=requester).first()
    access_request.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER']) 


@login_required
def deny_access(request, id):
    """Only available to superusers."""
    requester = get_object_or_404(User, id=id)
    messages.info(request, f'Access restricted from {requester.username}.')
    access_request = SearchAccessRequest.objects.filter(requester=requester).first()
    access_request.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER']) 


@login_required
def searcher_access(request):
    context = {
        "already_has_access": request.user.groups.filter(name='News Search').exists(),
        "request_already_sent": SearchAccessRequest.objects.filter(requester=request.user).exists()
    }
    return render(request, 'news/access.html', context)


class SourceDetailView(LoginRequiredMixin, DetailView):
    model = Source

    def get(self, request, *args, **kwargs):
        source = get_object_or_404(Source, pk=kwargs['pk'])
        return render(request, 'sources/source_detail.html', context={'item': source})


class SourceCreateView(LoginRequiredMixin, CreateView):
    model = Source
    fields = ["domain", "source_name", "primary_language"]
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(SourceCreateView, self).get_context_data(**kwargs)
        context.update({"header": "Create source", "create": True}) # If update, false; if create, true
        return context


class SourceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Source
    fields = ["domain", "source_name", "primary_language"]
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(SourceUpdateView, self).get_context_data(**kwargs)
        context.update({"header": "Update source", "create": False}) # If update, false; if create, true
        return context


class ArticleByURLCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ArticleByURL
    fields = ["URL",]
    template_name = 'news/search.html'

    def get_context_data(self, **kwargs):
        context = super(ArticleByURLCreateView, self).get_context_data(**kwargs)
        context.update({'search_description': 'Enter the URL of an article you want to read in the search box below.'})
        return context

    def form_valid(self, form):
        form.instance.searcher = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='News Search').exists() or self.request.user.is_superuser


class ArticleByURLDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = ArticleByURL

    def test_func(self):
        return self.request.user.groups.filter(name='News Search').exists() or self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        article = get_object_or_404(ArticleByURL, pk=kwargs['pk']) # Get article from URL parameter

        if is_ajax(request=request):
            if request.GET.get('original_text'):
                original_text = request.GET.get('original_text')
                src = request.GET.get('src')
                dest = request.GET.get('dest')
                print(src)
                print(dest)
                print(original_text)
                translator = Translator()
                res = translator.translate(original_text, src=src, dest=dest)
                translation_dict = {"src": res.src, "dest": res.dest, "translated_text": res.text, "original_text": original_text}
                print(translation_dict)
                return JsonResponse(translation_dict)
            if request.GET.get('element_id'):
                element_id = request.GET.get('element_id')
                if element_id == "1-star":
                    stars = 1
                elif element_id == "2-stars":
                    stars = 2
                elif element_id == "3-stars":
                    stars = 3
                elif element_id == "4-stars":
                    stars = 4
                elif element_id == "5-stars":
                    stars = 5
                stars_dict = {"stars": stars}

                article_by_url = True if article.article_searched_by == "url" else False

                try:
                    updated_rating = Rating.objects.filter(article_id=article.id).filter(user=self.request.user).filter(article_by_url=article_by_url).first()
                    updated_rating.stars = stars
                    updated_rating.save()
                except AttributeError: # If AttributeError, then note didn't exist, and we have to create one rather than updating it.
                    new_rating = Rating(user=self.request.user, article_id=article.id, article_by_url=article_by_url, stars=stars)
                    new_rating.save()
                print(stars_dict)
                return JsonResponse(stars_dict)
        if request.GET.get('wiki_query'):
            wiki_query = request.GET.get('wiki_query')
            lang = request.GET.get('lang')
            # suggestion = wikipedia.suggest(wiki_query)
            results = wikipedia.search(wiki_query)
            print(results)
            first_result = results[0]
            try:
                wikipedia.set_lang(lang)
                pg = wikipedia.page(first_result)
                first_result_title = pg.title
                wiki_page_url = pg.url
                summ = wikipedia.summary(first_result) # Additional parameter: sentences=2
            except:
                try:
                    wiki_wiki = wikipediaapi.Wikipedia(language=lang)
                    pg = wiki_wiki.page(first_result)
                    first_result_title = pg.title
                    summ = pg.summary
                    wiki_page_url = pg.fullurl
                except:
                    wiki_page_url, summ, first_result_title = "", "", ""
            wiki_dict = {
                "results": results,
                "wiki_page_url": wiki_page_url,
                "summary": summ,
                "first_result_title": first_result_title
            }
            return JsonResponse(wiki_dict)
        if request.GET.get('user_note_title') or request.GET.get('user_note_text'):
            title = request.GET.get('user_note_title')
            text = request.GET.get('user_note_text')
            article_by_url = True if article.article_searched_by == "url" else False
            try:
                updated_note = ArticleNote.objects.filter(article_id=article.id).filter(user=self.request.user).filter(article_by_url=article_by_url).first()
                updated_note.title = title
                updated_note.note = text
                updated_note.save()
            except AttributeError: # If AttributeError, then note didn't exist, and we have to create one rather than updating it.
                new_note = ArticleNote(user=self.request.user, article_id=article.id, article_by_url=article_by_url, title=title, note=text)
                new_note.save()
            return JsonResponse({'user_note_title_updated': title, 'user_note_text_updated': text})

        context = save_and_get_dict_for_rendering_article(request, user=self.request.user, article_object=article, DatabaseModel=ArticleByURL, article_searched_by="url")
        context.update({
            'LANGUAGES': get_languages()
        })

        try:
            article_by_url = True if article.article_searched_by == "url" else False
            article_note = ArticleNote.objects.filter(article_id=article.id).filter(user=self.request.user).filter(article_by_url=article_by_url).first()
            print(article_note.note)
            context.update({"article_note": article_note})
        except AttributeError:
            context.update({"article_note": None})

        try:
            article_by_url = True if article.article_searched_by == "url" else False
            article_rating = Rating.objects.filter(article_id=article.id).filter(user=self.request.user).filter(article_by_url=article_by_url).first()
            context.update({"article_rating": article_rating})
        except AttributeError:
            context.update({"article_rating": None})

        return render(request, 'news/article.html', context)


class ArticleByTitleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ArticleByTitle
    fields = ["query", "source", "other_source"]
    template_name = 'news/search.html'

    def get_context_data(self, **kwargs):
        context = super(ArticleByTitleCreateView, self).get_context_data(**kwargs)
        context.update({'search_description': 'Enter the title of an article you want to read in the search box below.'})
        return context

    def form_valid(self, form):
        form.instance.searcher = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='News Search').exists() or self.request.user.is_superuser


class ArticleByTitleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = ArticleByTitle

    def test_func(self):
        return self.request.user.groups.filter(name='News Search').exists() or self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        """
        # if article is saved:
        #     Get saved data from DB
        #     Render view
        # else:
        #     Get article data and then render
        """
        article = get_object_or_404(ArticleByTitle, pk=kwargs['pk']) # Get article from URL parameter
        if article.source:
            src = article.source.domain.replace("www.", "")
            google_url = get_google_url(source=src, other_source=None, query=article.query)
        elif article.other_source:
            src = article.other_source
            google_url = get_google_url(source=None, other_source=src, query=article.query)
        else: # If no source and no other_source
            google_url = get_google_url(source=None, other_source=None, query=article.query)

        if "https://www.google.com/search?q=" not in article.google_url:
            article.google_url = google_url
            article.save()
        article_url = scrape_search_single_article(google_url)

        if article.URL == SET_DEFAULT_FIELD(): # SET_DEFAULT_FIELD() returns "-", the default in the column.
            article.URL = article_url
            article.save()

        context = save_and_get_dict_for_rendering_article(request, user=self.request.user, article_object=article, DatabaseModel=ArticleByTitle, article_searched_by="title")
        return render(request, 'news/article.html', context)


class ArticlesByTitleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ArticlesByTitle
    fields = ["query", "source", "other_source"]
    template_name = 'news/search.html'

    def get_context_data(self, **kwargs):
        context = super(ArticlesByTitleCreateView, self).get_context_data(**kwargs)
        context.update({'search_description': 'Enter your query in the search box below.'})
        return context

    def form_valid(self, form):
        form.instance.searcher = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='News Search').exists() or self.request.user.is_superuser


class ArticlesByTitleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = ArticlesByTitle

    def get(self, request, *args, **kwargs):

        search_query = get_object_or_404(ArticlesByTitle, pk=kwargs['pk'])
        q = "+".join(search_query.query.lower().split())
        google_url = f"https://www.google.com/search?q={q}"
        if "https://www.google.com/search?q=" not in search_query.google_url: # If database row doesn't already contain "https://www.google.com/search?q=" then it's obviously not a Google URL
            search_query.google_url = google_url
            search_query.save()
        list_of_results = scrape_search_multiple_articles(google_url)
        try:
            query_summary = get_wikipedia_summary(q)
        except:
            query_summary = None
        print(list_of_results[0])
        print(google_url)
        return render(request, 'news/articles.html', {
            'search_term': search_query.query,
            'search_term_titled': search_query.query.title(),
            'query_results_link': google_url,
            'len_of_news_arr': len(list_of_results),
            'news_results': list_of_results,
            'query_summary': query_summary,
        })

    def test_func(self):
        return self.request.user.groups.filter(name='News Search').exists() or self.request.user.is_superuser


@login_required
def star_article(request, id, article_searched_by):

    if article_searched_by.lower() == "url":
        article = get_object_or_404(ArticleByURL, id=id)
        if article.article_by_url_stars.filter(id=request.user.id).exists():
            # User has already starred article. The following line removes the star.
            article.article_by_url_stars.remove(request.user)
        else: # User adding star.
            article.article_by_url_stars.add(request.user)

    else:
        article = get_object_or_404(ArticleByTitle, id=id)
        if article.article_by_title_stars.filter(id=request.user.id).exists():
            # User has already starred article. The following line removes the star.
            article.article_by_title_stars.remove(request.user)
        else: # User adding star.
            article.article_by_title_stars.add(request.user)

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def bookmark_article(request, id, article_searched_by):

    if article_searched_by.lower() == "url":
        article = get_object_or_404(ArticleByURL, id=id)
        if article.article_by_url_bookmarks.filter(id=request.user.id).exists():
            # User has already bookmarked article. The following line removes the bookmark.
            article.article_by_url_bookmarks.remove(request.user)
        else: # User adding bookmark.
            article.article_by_url_bookmarks.add(request.user)
    else:
        article = get_object_or_404(ArticleByTitle, id=id)
        if article.article_by_title_bookmarks.filter(id=request.user.id).exists():
            # User has already bookmarked article. The following line removes the bookmark.
            article.article_by_title_bookmarks.remove(request.user)  
        else: # User adding bookmark.
            article.article_by_title_bookmarks.add(request.user)

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def flag_article(request, id, article_searched_by):

    if article_searched_by.lower() == "url":
        article = get_object_or_404(ArticleByURL, id=id)
        if article.article_by_url_flags.filter(id=request.user.id).exists():
            # User has already flagged article. The following line removes the flag.
            article.article_by_url_flags.remove(request.user)
        else: # User adding flag.
            article.article_by_url_flags.add(request.user)
    else:
        article = get_object_or_404(ArticleByTitle, id=id)
        if article.article_by_title_flags.filter(id=request.user.id).exists():
            # User has already flagged article. The following line removes the flag.
            article.article_by_title_flags.remove(request.user)  
        else: # User adding flag.
            article.article_by_title_flags.add(request.user)

    return HttpResponseRedirect(request.META['HTTP_REFERER'])


class StarredListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'news/saved_articles.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super(StarredListView, self).get_context_data(**kwargs)
        context.update({"save_method": "star", "title": "Starred Articles"})
        return context

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        article_by_title = ArticleByTitle.objects.filter(article_by_title_stars=user_in_url)
        article_by_url = ArticleByURL.objects.filter(article_by_url_stars=user_in_url)
        starred_articles = list(article_by_url) + list(article_by_title)
        starred_articles.sort(key=lambda x: x.date_searched, reverse=True)
        return starred_articles

    def test_func(self):
        """
        user_in_url is the parameter in the URL. Check if this user in URL is same as user logged in.
        """
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        if user_in_url == self.request.user and self.request.user.groups.filter(name='News Search').exists():
            return True
        return False


class BookmarkedListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'news/saved_articles.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super(BookmarkedListView, self).get_context_data(**kwargs)
        context.update({"save_method": "bookmark", "title": "Bookmarked Articles"})
        return context

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        article_by_title = ArticleByTitle.objects.filter(article_by_title_bookmarks=user_in_url)
        article_by_url = ArticleByURL.objects.filter(article_by_url_bookmarks=user_in_url)
        bookmarked_articles = list(article_by_url) + list(article_by_title)
        bookmarked_articles.sort(key=lambda x: x.date_searched, reverse=True)
        return bookmarked_articles

    def test_func(self):
        """
        user_in_url is the parameter in the URL. Check if this user in URL is same as user logged in.
        """
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        if user_in_url == self.request.user and self.request.user.groups.filter(name='News Search').exists():
            return True
        return False


class FlaggedListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'news/saved_articles.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super(FlaggedListView, self).get_context_data(**kwargs)
        context.update({"save_method": "flag", "title": "Flagged Articles"})
        return context

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        article_by_title = ArticleByTitle.objects.filter(article_by_title_flags=user_in_url)
        article_by_url = ArticleByURL.objects.filter(article_by_url_flags=user_in_url)
        flagged_articles = list(article_by_url) + list(article_by_title)
        flagged_articles.sort(key=lambda x: x.date_searched, reverse=True)
        return flagged_articles

    def test_func(self):
        """
        user_in_url is the parameter in the URL. Check if this user in URL is same as user logged in.
        """
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        if user_in_url == self.request.user and self.request.user.groups.filter(name='News Search').exists():
            return True
        return False



class SingleArticlesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """MAKE IT SO THAT YOU CAN ONLY SEE SEARCHES FOR THE USER THEMSELVES"""
    template_name = 'news/article_history.html'
    context_object_name = 'items'

    def get_context_data(self, **kwargs):
        context = super(SingleArticlesListView, self).get_context_data(**kwargs)
        articles_by_title = ArticlesByTitle.objects.filter(searcher=self.request.user)
        article_by_title = ArticleByTitle.objects.filter(searcher=self.request.user)
        article_by_url = ArticleByURL.objects.filter(searcher=self.request.user)
        articles = list(article_by_url) + list(article_by_title) + list(articles_by_title)
        articles.sort(key=lambda x: x.date_searched, reverse=True)
        context.update({"items": articles})
        return context

    def get_queryset(self):
        return ArticleByURL.objects.order_by('-date_searched')

    def test_func(self):
        if not self.request.user.groups.filter(name='News Search').exists():
            return False
        searcher = get_object_or_404(User, username=self.kwargs.get('username'))
        articles_by_title = ArticleByTitle.objects.filter(searcher=searcher)
        articles_by_url = ArticleByURL.objects.filter(searcher=searcher)
        print(f"Searcher: {searcher.username}")
        print(f"User: {self.request.user.username}")
        articles = list(articles_by_url) + list(articles_by_title)
        if len(articles) > 0:
            if str(articles[0].searcher) == str(self.request.user.username):
                return True
        elif len(articles) == 0:
            return False
        else:
            return False


class ArticleByURLListView(LoginRequiredMixin, UserPassesTestMixin, ListView): # ListView
    """MAKE IT SO THAT YOU CAN ONLY SEE SEARCHES FOR THE USER THEMSELVES"""
    model = ArticleByURL
    template_name = 'news/article_history.html'
    context_object_name = 'items'
    ordering = ['-date_searched']

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return ArticleByURL.objects.filter(searcher=user).order_by('-date_searched')

    def test_func(self):
        if not self.request.user.groups.filter(name='News Search').exists():
            return False
        searcher = get_object_or_404(User, username=self.kwargs.get('username'))
        articles_by_url = ArticleByURL.objects.filter(searcher=searcher)
        print(f"Searcher: {searcher.username}")
        print(f"User: {self.request.user.username}")
        if len(articles_by_url) > 0:
            if str(articles_by_url[0].searcher) == str(self.request.user.username):
                return True
        elif len(articles_by_url) == 0:
            return False
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(ArticleByURLListView, self).get_context_data(**kwargs)
        context.update({'search_article_by': "url"})
        return context


class ArticleByTitleListView(LoginRequiredMixin, UserPassesTestMixin, ListView): # ListView
    """MAKE IT SO THAT YOU CAN ONLY SEE SEARCHES FOR THE USER THEMSELVES"""
    model = ArticleByTitle
    template_name = 'news/article_history.html'
    context_object_name = 'items'
    ordering = ['-date_searched']

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return ArticleByTitle.objects.filter(searcher=user).order_by('-date_searched')

    def test_func(self):
        if not self.request.user.groups.filter(name='News Search').exists():
            return False
        searcher = get_object_or_404(User, username=self.kwargs.get('username'))
        articles_by_url = ArticleByTitle.objects.filter(searcher=searcher)
        print(f"Searcher: {searcher.username}")
        print(f"User: {self.request.user.username}")
        if len(articles_by_url) > 0:
            if str(articles_by_url[0].searcher) == str(self.request.user.username):
                return True
        elif len(articles_by_url) == 0:
            return False
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(ArticleByTitleListView, self).get_context_data(**kwargs)
        context.update({'search_article_by': "single_article"})
        return context


class ArticlesByTitleListView(LoginRequiredMixin, UserPassesTestMixin, ListView): # ListView
    """MAKE IT SO THAT YOU CAN ONLY SEE SEARCHES FOR THE USER THEMSELVES"""
    model = ArticlesByTitle
    template_name = 'news/article_history.html'
    context_object_name = 'items'
    ordering = ['-date_searched']

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return ArticlesByTitle.objects.filter(searcher=user).order_by('-date_searched')

    def test_func(self):
        if not self.request.user.groups.filter(name='News Search').exists():
            return False
        searcher = get_object_or_404(User, username=self.kwargs.get('username'))
        articles_by_url = ArticlesByTitle.objects.filter(searcher=searcher)
        print(f"Searcher: {searcher.username}")
        print(f"User: {self.request.user.username}")
        if len(articles_by_url) > 0:
            if str(articles_by_url[0].searcher) == str(self.request.user.username):
                return True
        elif len(articles_by_url) == 0:
            return False
        else:
            return False

    def get_context_data(self, **kwargs):
        context = super(ArticlesByTitleListView, self).get_context_data(**kwargs)
        context.update({
            'search_article_by': "multiple_articles",
            "google_url": ""
        })
        return context

