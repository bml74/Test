from django.contrib import admin
from .models import (
    Source, SourceTwitterHandle, 
    ArticleByURL,
    ArticleNote,
    ArticleByTitle,
    ArticlesByTitle,
    SearchAccessRequest,
    Rating
)


admin.site.register(Source)
admin.site.register(SourceTwitterHandle)
admin.site.register(ArticleByURL)
admin.site.register(ArticleNote)
admin.site.register(ArticleByTitle)
admin.site.register(ArticlesByTitle)
admin.site.register(SearchAccessRequest)
admin.site.register(Rating)
