import stripe
from datetime import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY

def pricing(request):
    subscription = {}
    canuse = False
    if request.user.is_authenticated:
        subscription = Subscription.objects.get(user=request.user)
        canuse = subscription.can_use()
    return render(request, 'subscription/pricing.html', {
        'canuse': canuse,
        'subscription': subscription
    })

@login_required(login_url='login')
def subscription_management(request):
    sub = Subscription.objects.get(user=request.user)
    subscription_detail = None
    if sub.is_subscribed:
        try:
            checkout_session = stripe.checkout.Session.retrieve(sub.stripe_checkout_id)
            subscription = stripe.Subscription.retrieve(checkout_session.subscription)
            subscription_detail = {
                'is_subscribed': subscription.status == 'active',
                'start': datetime.fromtimestamp(subscription.current_period_start),
                'end': datetime.fromtimestamp(subscription.current_period_end),
                'price': subscription['items']['data'][0]['price']['unit_amount'] / 100,
                'currency': subscription['items']['data'][0]['price']['currency'],
                'interval': subscription['items']['data'][0]['plan']['interval'],
                'credits': sub.credits
            }
            print(subscription_detail)
        except stripe.error.StripeError as e:
            print(e)
            return HttpResponse("Retrieve stripe subscription error", status=500)
    else:
        subscription_detail = {
            'is_subscribed': False,
            'credits': sub.credits
        }
    return render(request, 'subscription/subscription.html', {
        'subscription': subscription_detail,
    })

@login_required(login_url='login')
def create_checkout_session(request):
    try:
        customer_id = ''
        subscription = Subscription.objects.get(user=request.user)
        if subscription.stripe_customer_id:
            customer_id = subscription.stripe_customer_id
        else:
            customer = stripe.Customer.create(
                email=request.user.email
            )
            subscription.stripe_customer_id = customer.id
            customer_id = customer.id
            subscription.save()

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': settings.PRODUCT_PRICE,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            customer=customer_id,
            customer_update={'address': 'auto'},
            success_url=settings.REDIRECT_DOMAIN + '/subscribe_success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=settings.REDIRECT_DOMAIN + '/subscribe_cancel',
            automatic_tax={'enabled': True},
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return HttpResponse("Create checkout session error", status=500)

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
    sig_header = request.headers.get('STRIPE_SIGNATURE')
    event = None
    logging.warning(sig_header)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        logging.error(f"VAL {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logging.error(f"SIG {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Handle successful checkout session here
        session_id = session.get('id', None)
        customer_id = session.get('customer')
        try:
            subscription = Subscription.objects.get(stripe_customer_id=customer_id)
            subscription.stripe_checkout_id = session_id
            subscription.is_subscribed = True
            subscription.save()
        except Subscription.DoesNotExist:
            logging.error(f"Subscription with customer_id {customer_id} does not exist.")
    elif event['type'] == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.
        session = event['data']['object']
        customer_id = session['customer']
        try:
            subscription = Subscription.objects.get(stripe_customer_id=customer_id)
            subscription.stripe_checkout_id = None
            subscription.is_subscribed = False
            subscription.save()
        except Subscription.DoesNotExist:
            logging.error(f"Subscription with customer_id {customer_id} does not exist.")

    return HttpResponse(status=200)
