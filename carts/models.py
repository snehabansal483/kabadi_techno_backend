from django.db import models
from accounts.models import CustomerProfile
from dealer_details.models import PriceList
from accounts.models import DealerProfile
from django.core.exceptions import ObjectDoesNotExist

# -----------------------
# Cart Model
# -----------------------
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

# -----------------------
# CartItem Model
# -----------------------
class CartItem(models.Model):
    unit_choice = (
        ('kg', 'kg'),
        ('pcs', 'pcs'),
    )
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, null=True)
    customer_name = models.CharField(max_length=250, null=True)
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, null=True)
    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, null=True)
    subcategory_name = models.CharField(max_length=250)
    subcategory_image = models.ImageField(upload_to='photos/SubCategory', blank=True)
    GST = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    unit = models.CharField(max_length=3, choices=unit_choice)
    quantity = models.IntegerField(default=0)
    price = models.FloatField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.customer_name} - {self.subcategory_name}"

    def save(self, *args, **kwargs):
        if self.is_active is None:
            self.is_active = True
        if self.customer and hasattr(self.customer, 'auth_id'):
            self.customer_name = self.customer.auth_id.username
        if self.price_list:
            self.subcategory_name = self.price_list.subcategory_name
            self.subcategory_image = self.price_list.subcategory_image
            self.GST = self.price_list.GST
            self.unit = self.price_list.unit
            self.percentage = self.price_list.percentage
            self.price = self.price_list.price
            self.dealer = self.price_list.dealer
        super(CartItem, self).save(*args, **kwargs)

# -----------------------
# Cart_Order Model
# -----------------------
class Cart_Order(models.Model):
    status_choice = (
        ('True','True'),
        ('False','False'),
        ('Cancel','Cancel'),
    )

    customer_id = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, null=True)
    dealer_id = models.ForeignKey(DealerProfile, on_delete=models.CASCADE, null=True)

    cart_item_1 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_1')
    cart_item_2 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_2')
    cart_item_3 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_3')
    cart_item_4 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_4')
    cart_item_5 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_5')
    cart_item_6 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_6')
    cart_item_7 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_7')
    cart_item_8 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_8')
    cart_item_9 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_9')
    cart_item_10 = models.OneToOneField(CartItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_item_no_10')

    status = models.CharField(default="False", choices=status_choice, max_length=20)

    def __str__(self):
        return f"Cart Order #{self.id}"

    @property
    def sub_total(self):
        total = 0
        for i in range(1, 11):
            item = getattr(self, f'cart_item_{i}', None)
            if item and item.price and item.quantity:
                total += item.price * item.quantity
        return total
