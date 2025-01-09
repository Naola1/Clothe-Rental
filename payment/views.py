import stripe
from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from shop.models import Clothes, Rental
from decimal import Decimal
from datetime import datetime

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def initiate_payment(request):
    try:
        cloth_id = request.POST.get('cloth_id')
        duration = request.POST.get('duration')
        rental_date = request.POST.get('rental_date')
        return_date = request.POST.get('return_date')
        total_price = request.POST.get('total_price')
        notes = request.POST.get('notes', '')

        cloth = Clothes.objects.get(id=cloth_id)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(float(total_price) * 100),  # Convert to cents
                    'product_data': {
                        'name': f'Rental for {duration} days',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/payments/success/?cloth_id={cloth_id}&duration={duration}&rental_date={rental_date}&return_date={return_date}&total_price={total_price}'),
            cancel_url=request.build_absolute_uri('/payments/cancel/'),
            client_reference_id=str(request.user.id)
        )

        Payment.objects.create(
            user=request.user,
            cloth=cloth,  
            stripe_payment_intent=checkout_session.id,
            amount=total_price,
            status='pending'
        )

        return redirect(checkout_session.url)

    except Clothes.DoesNotExist:
        return JsonResponse({'error': 'Cloth not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403)
    

@login_required
def extend_rental(request, rental_id):
    """
    Handle rental extension payment
    """
    try:
        rental = get_object_or_404(Rental, id=rental_id, user=request.user)
        days_to_extend = int(request.POST.get('days', 0))
        extension_price = float(request.POST.get('extension_price', 0))

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(extension_price * 100),
                    'product_data': {
                        'name': f'Rental Extension: {rental.clothe.name}',
                        'description': f'Extend by {days_to_extend} days'
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/payments/extension-success/?rental_id={rental_id}&days={days_to_extend}&extension_price={extension_price}'),
            cancel_url=request.build_absolute_uri('/payments/cancel/'),
            client_reference_id=str(request.user.id)
        )

        Payment.objects.create(
            user=request.user,
            cloth=rental.clothe,
            stripe_payment_intent=checkout_session.id,
            amount=extension_price,
            status='pending',
            payment_type='extension'
        )

        return redirect(checkout_session.url)

    except Exception as e:
        messages.error(request, f'Extension payment failed: {str(e)}')
        return redirect('rentals:rental_detail', pk=rental_id)

@login_required
def cart_payment(request):
    """
    Handle cart payment with only email input
    """
    try:
        cart_items = request.POST.getlist('cart_items')
        cart_durations = request.POST.getlist('durations')
        cart_total = request.POST.get('cart_total')

        if not cart_items:
            messages.error(request, 'No items in cart')
            return redirect('cart')

        line_items = []
        rental_details = []

        try:
            for item_id, duration in zip(cart_items, cart_durations):
                cloth = get_object_or_404(Clothes, id=item_id)
                rental_start = request.POST.get(f'rental_date_{item_id}')
                rental_end = request.POST.get(f'return_date_{item_id}')
                item_price = float(request.POST.get(f'price_{item_id}', cloth.price))

                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(item_price * 100),
                        'product_data': {
                            'name': f'Rental: {cloth.name}',
                            'description': f'Duration: {duration} days (from {rental_start} to {rental_end})'
                        },
                    },
                    'quantity': 1,
                })

                rental_details.append({
                    'cloth_id': item_id,
                    'duration': duration,
                    'rental_date': rental_start,
                    'return_date': rental_end,
                    'price': item_price
                })

            # Store rental details in session
            request.session['cart_rental_details'] = rental_details

            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=request.build_absolute_uri('/payments/cart-success/'),
                    cancel_url=request.build_absolute_uri('/payments/cancel/'),
                    client_reference_id=str(request.user.id),
                    customer_email=request.user.email,  # Pre-fill the email
                    # payment_method_collection='always',  # Only collect payment method
                    billing_address_collection='auto',  # Don't collect billing address
                    shipping_address_collection=None,  # Don't collect shipping address
                )
                print("Stripe session created successfully:", checkout_session.id)

                try:
                    print("Creating Payment object...")
                    payment = Payment.objects.create(
                        user=request.user,
                        cloth=cloth,
                        stripe_payment_intent=checkout_session.id,
                        amount=cart_total,
                        status='pending',
                        payment_type='cart'
                    )
                    print("Payment object created successfully:", payment.id)

                    return redirect(checkout_session.url)

                except Exception as payment_error:
                    print("Error creating Payment object:", str(payment_error))
                    raise Exception(f"Payment creation failed: {str(payment_error)}")

            except stripe.error.StripeError as stripe_error:
                print("Stripe error:", str(stripe_error))
                raise Exception(f"Stripe error: {str(stripe_error)}")

        except Clothes.DoesNotExist as cloth_error:
            print("Clothes not found:", str(cloth_error))
            raise Exception(f"Item not found: {str(cloth_error)}")

    except Exception as e:
        print("Final error:", str(e))
        messages.error(request, str(e))
        return redirect('cart')
    

@login_required
def cart_payment_success(request):
    """
    Handle successful cart payment and create rental records
    """
    try:
        rental_details = request.session.get('cart_rental_details', [])
        rentals_created = []

        for item in rental_details:
            cloth = get_object_or_404(Clothes, id=item['cloth_id'])
            
            rental = Rental.objects.create(
                user=request.user,
                clothe=cloth,
                duration=item['duration'],
                rental_date=item['rental_date'],
                return_date=item['return_date'],
                total_price=item['price'],
                status='active'
            )
            rentals_created.append(rental)

        # Update payment status
        Payment.objects.filter(
            user=request.user,
            status='pending',
            payment_type='cart'
        ).update(status='completed')

        # Clear session
        del request.session['cart_rental_details']

        messages.success(request, 'Cart payment successful! Your rentals have been created.')
        return render(request, 'payments/cart_success.html', {
            'rentals': rentals_created
        })

    except Exception as e:
        messages.error(request, f'Error processing cart payment: {str(e)}')
        return redirect('cart')
    
@login_required
def payment_success(request):
    cloth_id = request.GET.get('cloth_id')
    duration = request.GET.get('duration')
    rental_date_str = request.GET.get('rental_date')  # Get as string
    return_date_str = request.GET.get('return_date')  # Get as string
    total_price = request.GET.get('total_price')

    # Convert strings to datetime.date objects
    rental_date = datetime.strptime(rental_date_str, '%Y-%m-%d').date()
    return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()

    clothe = Clothes.objects.get(id=cloth_id)
    
    # Create rental record
    rental = Rental.objects.create(
        user=request.user,
        clothe=clothe,
        duration=duration,
        rental_date=rental_date,  # Use datetime.date object
        return_date=return_date,  # Use datetime.date object
        total_price=total_price,
        status='active'
    )

    # Update Payment status
    Payment.objects.filter(
        user=request.user, 
        cloth_id=cloth_id, 
        status='pending'
    ).update(status='completed')

    return render(request, 'payments/success.html', {'rental': rental})
def payment_cancel(request):
    return render(request, 'payments/cancel.html')

@login_required
def extension_success(request):
    """
    Handle successful rental extension payment
    """
    rental_id = request.GET.get('rental_id')
    days_to_extend = int(request.GET.get('days', 0))
    extension_price = float(request.GET.get('extension_price', 0))

    try:
        # Get the rental
        rental = Rental.objects.get(id=rental_id, user=request.user)

        # Update rental details
        rental.return_date += timedelta(days=days_to_extend)
        rental.is_extended = True 
        rental.extended_return_date = rental.return_date
        rental.total_price += Decimal(extension_price) 
        rental.save()
        
        # Update payment status
        Payment.objects.filter(
            user=request.user,
            cloth_id=rental.clothe.id,
            status='pending',
            payment_type='rental_extension'
        ).update(status='completed')

        messages.success(request, f'Rental successfully extended by {days_to_extend} days.')
        return render(request, 'payments/extension_success.html', {
            'rental': rental,
            'days_extended': days_to_extend
        })

    except Rental.DoesNotExist:
        messages.error(request, 'Rental not found.')
        return redirect('rented_items')
    except Exception as e:
        messages.error(request, f'Extension processing failed: {str(e)}')
        return redirect('rented_items')
