from django.shortcuts import render
from .models import Crop

# Create your views here.
def index(request):

    context = {
        'num_crops': Crop.objects.all().count(),
        'crops': Crop.objects.all()[:]
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)