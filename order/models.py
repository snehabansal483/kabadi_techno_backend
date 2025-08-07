from django.db import models
from accounts.models import CustomerProfile

from carts.models import CartItem

# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )
    

    TimeSlot = (
        ('8am - 1pm','8am - 1pm'),
        ('1pm - 6pm','1pm - 6pm'),
    )

    customer_id = models.ForeignKey(CustomerProfile, on_delete=models.SET_NULL, null=True, db_column='customer_id')

    # price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, null=True)
    dealer_id = models.IntegerField(null=True, blank=True)
    order_number = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=50)
    address_line_1 = models.CharField(max_length=50)
    address_line_2 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    digipin = models.CharField(max_length=20, blank=True, null=True)
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.FloatField(null=True)
    tax = models.FloatField(null=True)
    pickup_date = models.DateField()
    pickup_time = models.CharField(max_length=30, choices=TimeSlot, default='8am - 1pm')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    cart_order_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending') 

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}' 

    def __str__(self):
        return str(self.customer_id.auth_id)
    

class OrderProduct(models.Model):
    STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'), 
        ('Cancelled by Customer','Cancelled by Customer'),
        ('Cancelled by dealer','Cancelled by dealer'),

    )
    unit_choice =(
        ('kg','kg'),
        ('pcs','pcs'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, null=True)
    customer_id = models.IntegerField()
    dealer_id = models.IntegerField()
    subcategory_name = models.CharField(max_length=250)
    subcategory_image = models.ImageField(upload_to='photos/SubCategory',blank=True)
    GST = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    unit = models.CharField(max_length=3,choices=unit_choice)
    quantity = models.IntegerField()
    status = models.CharField(max_length=30, choices=STATUS, default='New')
    price = models.FloatField()
    order_number = models.CharField(max_length=50, default = '20220906KT000005')
    is_ordered = models.BooleanField(default=False)
    total_cart_items = models.IntegerField(default=0)
    total_amount = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subcategory_name

    def save(self, *args, **kwargs):
        if self.cart_item:
            self.customer_id = self.cart_item.customer_id
            self.dealer_id = self.cart_item.dealer_id
            self.subcategory_name = self.cart_item.subcategory_name
            self.subcategory_image = self.cart_item.subcategory_image
            self.GST = self.cart_item.GST
            self.unit = self.cart_item.unit
            self.percentage = self.cart_item.percentage
            self.quantity = self.cart_item.quantity
            self.price = self.cart_item.price

        if self.order:
            self.order_number = self.order.order_number

        # Calculate total_amount for this order product
        if self.quantity and self.price:
            subtotal = self.quantity * self.price
            tax_amount = subtotal * (self.GST / 100)
            percentage_amount = subtotal * (self.percentage / 100)
            self.total_amount = subtotal + tax_amount + percentage_amount
        
        # Calculate total_cart_items (number of items in this order product)
        self.total_cart_items = self.quantity if self.quantity else 0

        super(OrderProduct, self).save(*args, **kwargs)

    
