from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Item, OrderItem, Order, BillingAddress, Payment, Discount
from .forms import CheckoutForm, DiscountForm
import paystack
# from .models import Item

# Create your views here.


class HomeView(ListView):
    model = Item
    paginate_by = 7
    # context_object_name = 'items' Another method to loop through the items
    template_name = "body.html"


class DetailView(DetailView):
    model = Item
    template_name = "detail_v.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This Item quantity was updated!")
            return redirect("order-summary")
        else:
            messages.info(request, "This Item was added to your cart")
            order.items.add(order_item)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This Item was added to your cart")

    return redirect("product", slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("order-summary")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)
    return redirect("order-summary")


@login_required
def remove_single_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)


def home(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'body.html', context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(
                user=self.request.user,
                ordered=False
            )
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order
            }
            return render(self.request, 'checkout.html', context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect('checkout')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                shipping_address = form.cleaned_data.get('shipping_address')
                shipping_address2 = form.cleaned_data.get('shipping_address2')
                shipping_country = form.cleaned_data.get('shipping_country')
                shipping_zip = form.cleaned_data.get('shipping_zip')
                # TODO: add functionality llater
                # same_billing_address = form.cleaned_data.get(
                #     'same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    stree_address=shipping_address,
                    shipping_address2=shipping_address2,
                    shipping_country=shipping_country,
                    shipping_zip=shipping_zip,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_option == 'P':
                    return redirect('payment', payment_option='Pay Stack')
                elif payment_option == 'D':
                    return redirect('payment', payment_option='Debit card')
                else:
                    messages.warning(self.request, "invalid payment option")
                    return redirect('checkout')


            messages.warning(self.request, "Failed to checkout")
            return redirect('checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("order-summary")


# below is the function for the payment view, card input and all others

class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('paystackToken')
        amount = int(order.get_total()) * 1000  #in naira 
        charge = paystack.Charges.create(
            amount=amount,
            currency='nar',
            source=token,
        )

        
        payment = Payment()
        payment.paystack_charge_id = charge['id']
        payment.user = self.request.user
        payment.amount = order.get_total()
        payment.save()

# the next 4 lines of code help to clear cart after successful payment on a re order
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()

        order.ordered = True
        order.payment = payment
        order.save()

        # I believe there should be a try statement for error handling for issues


# view to take in discount codes 
def get_discount( request, code):
    try:
        discount = Discount.objects.get(code=code)
        return discount
    except ObjectDoesNotExist:
        messages.info(request, "This discount code doesn't exist")
        return redirect('checkout')

def add_discount(request):
    try:
        order = Order.objects.get(
            user=request.user,
            ordered=False
        )
        order.discount = get_discount(request)
        order.save()
        messages.success(request, "Discount was added successfully")
        return redirect('checkout')


    except ObjectDoesNotExist:
        messages.info(request, "You do not have an active order")
        return redirect('checkout')
    # if order_qs.exists():
    #     order = order_qs[0]


