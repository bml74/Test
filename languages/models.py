from django.db import models


class CorsicanBibleChapter(models.Model):
    livre = models.CharField(max_length=100) 
    chapter = models.IntegerField() 
    corsican_stlc = models.CharField(max_length=100) 
    corsican_titre = models.CharField(max_length=100) 
    corsican_lines = models.TextField(blank=False)
    french_stlc = models.CharField(max_length=100) 
    french_titre = models.CharField(max_length=100) 
    french_lines = models.TextField(blank=False)
    page_url = models.CharField(max_length=255, default="http://projetbabel.org/bibbia_corsa/index.php") 
        
    def __str__(self):
        return self.corsican_stlc