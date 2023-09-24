from django.db import models
from ckeditor.fields import RichTextField
# Create your models here.
class Partner(models.Model):
    name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to="partners_logo")

class AboutContent(models.Model):
    content = RichTextField()