from django.db import models
from django.core.validators import MaxLengthValidator
# Create your models here.


class Film(models.Model):
    #Film model to store Star Wars films data from SWAPI.

    swapi_id = models.IntegerField(unique=True, help_text="ID from SWAPI")
    title = models.CharField(max_length=255)
    episode_id = models.IntegerField()
    opening_crawl = models.TextField()
    director = models.CharField(max_length=255)
    producer = models.CharField(max_length=255)
    release_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['release_date']
        indexes = [
            models.Index(fields=['release_date']),
            models.Index(fields=['swapi_id']),
        ]

    def __str__(self):
        return self.title



class Comment(models.Model):
    # model for storing user comments on films.

    film = models.ForeignKey(Film,on_delete=models.CASCADE,related_name='comments')
    text = models.TextField(max_length=500,validators=[MaxLengthValidator(500)],help_text="Comment text (max 500 characters)")
    author_name = models.CharField(max_length=100,default="Anonymous",help_text="Name of the commenter")
    author_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['film', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author_name} on {self.film.title}"

