from django.shortcuts import render
from .forms import CompressImageForm

def compress(request):
    form = CompressImageForm()
    context = {
        'form': form,
    }
    return render(request, 'image_compression/compress.html', context)