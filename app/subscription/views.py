import stripe
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

def pricing(request):
    return render(request, 'subscription/pricing.html')

def subscription_management(request):
    return render(request, 'subscription/subscription.html')

@login_required(login_url='login')
def create_checkout_session(request):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': settings.PRODUCT_PRICE,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=settings.REDIRECT_DOMAIN + '/subscribe_success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings.REDIRECT_DOMAIN + '/subscribe_cancel',
            automatic_tax={'enabled': True},
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return HttpResponse("Server error", status=500)

def subscribe_success(request):
    checkout_session_id = request.GET.get('session_id', None)
    return render(request, 'subscription/success.html')

def subscribe_cancel(request):
    return render(request, 'subscription/cancel.html')

def create_portal_session(request):
    subscription = Subscription.objects.get(user=request.user)
    if not subscription.is_subscribed:
        return HttpResponse("You have no subscription", status=500)
    checkout_session = stripe.checkout.Session.retrieve(subscription.stripe_checkout_id)

    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    portalSession = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=settings.REDIRECT_DOMAIN + '/subscription',
    )
    return redirect(portalSession.url, code=303)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Handle successful checkout session here
        session_id = session.get('id', None)
        customer_email = session["customer_details"]["email"]
        try:
            user = User.objects.get(email=customer_email)
            subscription = Subscription.objects.get(user=user)
            subscription.stripe_checkout_id = session_id
            subscription.is_subscribed = True
            subscription.save()
        except User.DoesNotExist:
            print(f'User with email {customer_email} does not exist')
    elif event['type'] == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.
        session = event['data']['object']
        customer_id = session['customer']
        try:
            customer = stripe.Customer.retrieve(customer_id)
            customer_email = customer.email
            try:
                user = User.objects.get(email=customer_email)
                subscription = Subscription.objects.get(user=user)
                subscription.stripe_checkout_id = None
                subscription.is_subscribed = False
                subscription.save()
            except User.DoesNotExist:
                print(f'User with email {customer_email} does not exist')
        except stripe.error.InvalidRequestError as e:
            print(f'Error retrieving customer: {e}')

    return HttpResponse(status=200)
