from django.shortcuts import render

# Create your views here.
def index_page(request):
    return render(request, 'mechdb_core/under_construction.html', {})
