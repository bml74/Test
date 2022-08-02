from django.urls import path
from . import views


urlpatterns = [

    path('', views.news_home, name='news-home'),

    # # Granting or restricting access to News Search:
    path('access/', views.searcher_access, name='news-searcher-access'), 
    path('access/request/', views.request_access, name='request_access'),
    path('access/requests/', views.AccessRequestsListView.as_view(), name='access_requests'),
    path('access/delete/', views.delete_access, name='delete_access'),
    path('access/request/granted/<int:id>/', views.grant_access, name='grant_access'),
    path('access/request/denied/<int:id>/', views.deny_access, name='deny_access'),

    # List Views:
    path('history/<str:username>/', views.SingleArticlesListView.as_view(), name='news-article-user-search-list'),
    # For ALL single articles (i.e., for those single articles searched by URL and by title).
    # Note: The view ABOVE returns a 403 Forbidden if the user hasn't searched for an article yet.
    path('<str:username>/article/url/', views.ArticleByURLListView.as_view(), name='news-article-user-search-list-by-url'),
    path('<str:username>/article/title/', views.ArticleByTitleListView.as_view(), name='news-article-user-search-list-by-title'),
    path('<str:username>/articles/title/', views.ArticlesByTitleListView.as_view(), name='news-articles-user-search-list-by-title'),


    path('source/<int:pk>/', views.SourceDetailView.as_view(), name='source-detail'),
    path('source/create/', views.SourceCreateView.as_view(), name='source-add'),
    path('source/update/', views.SourceUpdateView.as_view(), name='source-update'),

    path('article/url/', views.ArticleByURLCreateView.as_view(), name='news-article-search-by-url'),
    path('article/title/', views.ArticleByTitleCreateView.as_view(), name='news-article-search-by-title'),
    path('articles/title/', views.ArticlesByTitleCreateView.as_view(), name='news-articles-search-by-title'),

    path('article/url/<int:pk>/', views.ArticleByURLDetailView.as_view(), name='news-article-detail-by-url'),
    path('article/title/<int:pk>/', views.ArticleByTitleDetailView.as_view(), name='news-article-detail-by-title'),
    path('articles/title/<int:pk>/', views.ArticlesByTitleDetailView.as_view(), name='news-articles-detail-by-title'),

    # Starred articles:
    path('star/<str:article_searched_by>/<int:id>/', views.star_article, name='star_article'),
    path('starred/<str:username>/', views.StarredListView.as_view(), name='starred_list'), # View all favorites
    # Bookmarked articles:
    path('bookmark/<str:article_searched_by>/<int:id>/', views.bookmark_article, name='bookmark_article'),
    path('bookmarked/<str:username>/', views.BookmarkedListView.as_view(), name='bookmarked_list'),  # View all favorites
    # Flagged articles:
    path('flag/<str:article_searched_by>/<int:id>/', views.flag_article, name='flag_article'),
    path('flagged/<str:username>/', views.FlaggedListView.as_view(), name='flagged_list'),  # View all favorites

]

