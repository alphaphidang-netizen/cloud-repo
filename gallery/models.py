from django.db import models
# from cloudinary.models import CloudinaryField

class RecipePhoto(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Because we configured STORAGES, this automatically routes to Cloudinary
    image = models.ImageField(upload_to='recipes/') 
    # image = CloudinaryField('image')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title