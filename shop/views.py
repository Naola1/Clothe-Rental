from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import Clothes, Rental, Category
from .filters import ClotheFilter
from datetime import timedelta


def get_all_child_categories(category):
    """
    Recursively get all child categories of a given category.
    """
    children = category.children.all()
    all_children = list(children)
    for child in children:
        all_children.extend(get_all_child_categories(child))
    return all_children


def home_view(request):
    available_clothes = Clothes.objects.filter(stock__gt=0)
    latest_clothes = Clothes.objects.filter(stock__gt=0).order_by('-created_at')[:10]
    filterset = ClotheFilter(request.GET, queryset=available_clothes)
    search_query = request.GET.get('search', '').strip()
    category_slug = request.GET.get('category', '')

    if search_query:
        clothes = filterset.qs.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) | 
            Q(category__name__icontains=search_query) 
        )
    elif category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        all_categories = [category] + get_all_child_categories(category)
        clothes = filterset.qs.filter(category__in=all_categories)
    else:
        clothes = filterset.qs

    paginator = Paginator(clothes, 10)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    show_main_image = not search_query and not category_slug

    context = {
        'clothes': page_obj,
        'latest_clothes': latest_clothes,
        'paginator': paginator,
        'page_obj': page_obj,
        'show_main_image': show_main_image,
        'search_query': search_query
    }
    return render(request, 'shop/home.html', context)