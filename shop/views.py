from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
import json
from .models import Clothes, Rental, Category, Cart, CartItem
from .forms import RentalForm
from .filters import ClotheFilter


def get_all_child_categories(category):
    """
    Recursively get all child categories of a given category.
    Useful for filtering clothes within subcategories.
    """
    children = category.children.all()
    all_children = list(children)
    for child in children:
        all_children.extend(get_all_child_categories(child))
    return all_children


def home_view(request):
    """
    Displays the homepage with available clothes, filters, and search functionality.
    Includes pagination for clothes and highlights the latest additions.
    """
    # Fetch clothes with stock available
    available_clothes = Clothes.objects.filter(stock__gt=0)
    latest_clothes = available_clothes.order_by('-created_at')[:10]

    # Apply filters and search
    filterset = ClotheFilter(request.GET, queryset=available_clothes)
    search_query = request.GET.get('search', '').strip()
    category_slug = request.GET.get('category', '')

    if search_query:
        # Search clothes by name, description, or category
        clothes = filterset.qs.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    elif category_slug:
        # Filter clothes by category and its children
        category = get_object_or_404(Category, slug=category_slug)
        all_categories = [category] + get_all_child_categories(category)
        clothes = filterset.qs.filter(category__in=all_categories)
    else:
        clothes = filterset.qs

    # Paginate the results
    paginator = Paginator(clothes, 10)
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Show the main banner image if no search or category filter is applied
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


def cloth_detail_view(request, cloth_id):
    """
    Displays the details of a single cloth item along with related items and a rental form.
    """
    # Fetch the cloth item and related items
    cloth = get_object_or_404(Clothes, id=cloth_id)
    related_clothes_list = Clothes.objects.filter(category=cloth.category).exclude(id=cloth_id)

    # Paginate related items
    paginator = Paginator(related_clothes_list, 10)
    page_number = request.GET.get('page', 1)
    try:
        related_clothes = paginator.page(page_number)
    except PageNotAnInteger:
        related_clothes = paginator.page(1)
    except EmptyPage:
        related_clothes = paginator.page(paginator.num_pages)

    # Check for existing rentals for authenticated users
    form = RentalForm()
    existing_rental = None
    if request.user.is_authenticated:
        existing_rental = Rental.objects.filter(user=request.user, clothe_id=cloth.id, status='active').first()

    # Handle rental form submission
    if request.method == "POST" and request.user.is_authenticated:
        form = RentalForm(request.POST)
        if existing_rental:
            messages.warning(request, 'You have already rented this item.')
        elif form.is_valid() and cloth.stock > 0:
            rental_data = form.cleaned_data
            rental_data.update({
                'user_id': request.user.id,
                'cloth_id': cloth.id,
                'total_price': form.cleaned_data['duration'] * cloth.price
            })
            # Redirect to the payment process
            return redirect(
                'initiate_payment',
                cloth_id=cloth.id,
                duration=rental_data['duration'],
                rental_date=rental_data['rental_date'],
                return_date=rental_data['return_date'],
                total_price=rental_data['total_price']
            )
        else:
            messages.error(request, 'This item is out of stock.')

    context = {
        'cloth': cloth,
        'related_clothes': related_clothes,
        'form': form,
        'price': float(cloth.price),
        'page_obj': related_clothes,
        'existing_rental': existing_rental
    }
    return render(request, 'shop/detail.html', context)


@login_required
def rented_items(request):
    """
    Displays the list of items rented by the logged-in user.
    """
    rentals = Rental.objects.filter(user=request.user)
    return render(request, 'shop/rented_items.html', {'rentals': rentals})


@csrf_protect
@login_required
def extend_rental(request, rental_id):
    """
    Allows the user to extend the rental period for an item.
    """
    rental = get_object_or_404(Rental, pk=rental_id, user=request.user)
    cloth = rental.clothe

    # Calculate new return date and extension price
    days_to_extend = int(request.POST.get('days', 0))
    original_return_date = rental.return_date
    new_return_date = original_return_date + timedelta(days=days_to_extend)
    extension_price = days_to_extend * cloth.price

    # Redirect to the payment process for the extension
    return redirect(
        'initiate_payment',
        cloth_id=cloth.id,
        duration=days_to_extend,
        rental_date=original_return_date,
        return_date=new_return_date,
        total_price=extension_price,
        original_rental_id=rental_id
    )


@login_required
def add_to_cart(request, cloth_id):
    """
    Adds a cloth item to the user's cart. If the item already exists, increments the quantity.
    """
    cloth = get_object_or_404(Clothes, id=cloth_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, clothes=cloth)

    if not created:
        cart_item.quantity += 1  # Increment the quantity
    cart_item.save()
    return redirect('cart')  # Redirect to the cart page


@login_required
def cart_view(request):
    """
    Displays the contents of the user's cart and calculates the total price.
    """
    cart = get_object_or_404(Cart, user=request.user)
    today_date = timezone.now().date()
    cart_total = sum(item.get_total_price() for item in cart.items.all())
    max_duration = max(item.quantity for item in cart.items.all())
    return_date = today_date + timedelta(days=max_duration)

    context = {
        'cart': cart,
        'cart_total': cart_total,
        'today_date': today_date,
        'return_date': return_date,
    }
    return render(request, 'shop/cart.html', context)