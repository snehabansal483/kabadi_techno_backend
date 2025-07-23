from django.db import models

class dealer_initiatives(models.Model):
    dealer_id = models.IntegerField()
    dealer_account_type = models.CharField(max_length=50)
    deale_name = models.CharField(max_length=50)
    photo=models.ImageField(upload_to="photos",null= True,blank = True)
    message = models.TextField()
    views = models.IntegerField()
    likes = models.IntegerField()
    comments = models.CharField(max_length=50)

class schedule_pickup(models.Model):
    dealer_id = models.IntegerField()
    dealer_account_type = models.CharField(max_length=50)
    deale_name = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=70)
    pincode = models.CharField(max_length=50)
    state_n_country = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    select_date = models.DateField()
    select_time = models.TimeField()

class reach_us(models.Model):
    dealer_id = models.IntegerField()
    dealer_account_type = models.CharField(max_length=50)
    deale_name = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=70)
    subject = models.CharField(max_length=50)
    message = models.TextField()


class dealer_rating(models.Model):
    dealer_id = models.IntegerField()
    dealer_account_type = models.CharField(max_length=50)
    deale_name = models.CharField(max_length=50)
    rating = models.FloatField()
    rate_count = models.CharField(max_length=20)
