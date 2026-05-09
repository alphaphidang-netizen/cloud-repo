from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
import cloudinary.uploader

from recipe_project import settings # We need this to manually delete cloud files!
from .models import RecipePhoto
from .forms import PhotoUploadForm

def gallery_view(request):
    # 1. Handle Search
    query = request.GET.get('q', '')
    if query:
        # Search by title OR description
        photo_list = RecipePhoto.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).order_by('-uploaded_at')
    else:
        photo_list = RecipePhoto.objects.all().order_by('-uploaded_at')

    # 2. Handle Pagination (2 images per page)
    paginator = Paginator(photo_list, 2) 
    page_number = request.GET.get('page')
    photos = paginator.get_page(page_number)
    
    # 3. Handle Form Uploads
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery_home')
    else:
        form = PhotoUploadForm()

    return render(request, 'gallery/home.html', {
        'photos': photos, 
        'form': form,
        'query': query
    })

# 1. The Edit View
def edit_recipe(request, pk):
    # Fetch the specific recipe or return a 404 error if it doesn't exist
    photo = get_object_or_404(RecipePhoto, pk=pk)
    
    if request.method == 'POST':
        # Pass the existing instance to the form so it knows to UPDATE, not create
        form = PhotoUploadForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{photo.title}' updated successfully!")
            return redirect('gallery_home')
    else:
        # Pre-fill the form with the existing data
        form = PhotoUploadForm(instance=photo)
        
    return render(request, 'gallery/edit.html', {'form': form, 'photo': photo})

# 2. The Delete View
def delete_recipe(request, pk):
    photo = get_object_or_404(RecipePhoto, pk=pk)
    
    if request.method == 'POST':
        title = photo.title
        # Check if the image exists and if we are using Cloudinary
        # 1. NEW CHECK: Only delete from cloud if cloud storage is active
        # This makes your app resilient to internet outages.
        if photo.image and getattr(settings, 'USE_CLOUD_STORAGE', False):
            try:
                # 2. Tell Cloudinary to permanently delete the file from their servers
                # After model update, photo.image.public_id will now exist!
                cloudinary.uploader.destroy(photo.image.public_id)
            except Exception as e:
                # Still handle exceptions, but print for debugging
                print(f"Cloudinary deletion failed: {e}")
                
        # Delete the record from our local Django database
        photo.delete()
        messages.success(request, f"'{title}' was permanently deleted.")
        return redirect('gallery_home')
        
    return render(request, 'gallery/delete.html', {'photo': photo})