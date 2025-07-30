from django.db import models
#from django.contrib.gis.db import models # map
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

MY_CHOICES = (('Paper', 'Paper'),
              ('Plastic', 'Plastic'),
              ('Glass', 'Glass'),
              ('Metals', 'Metals'),
              ('E-waste', 'E-waste'),
              ('Others', 'Others'))

class dealer(models.Model):
    name = models.CharField(_("dealer Name"),max_length=100)
    email = models.EmailField(_("Dealer Email"), max_length=100, unique=True,null= True, blank=False)
    mobile = models.CharField(_("dealer Mobile No."),max_length=10)
    dealing = MultiSelectField(choices=MY_CHOICES, max_choices=3, max_length=300) # if i want to incre then incr the number
    min_qty = models.IntegerField(_("Minimum Quantity"),)
    max_qty = models.IntegerField(_("Maximum Quantity"),)
    pincode = models.CharField(_("dealer Pincode"),max_length=36)
    #geom = models.PointField(_("dealer Location"),blank=True,null=True,default="POINT(73.729974 20.7711857)", srid=4326)
    timing = models.CharField(_("Timing"),max_length=100,blank=True,null=True)
    live_location = models.CharField(_("Live Location"),max_length=100,blank=True,null=True)

    def _str_(self):
        return self.name

class RequestInquiry(models.Model):
    dealer_id = models.ForeignKey(dealer, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=13)
    email = models.EmailField(max_length=50)
    itemName = models.CharField(max_length=50)
    itemPic = models.ImageField(upload_to='photos/dealer/RequestInquiry',blank=True)
    quantity = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.itemName








# from django.db import models
# from django.contrib.gis.db import models
# from django.utils.translation import gettext_lazy as _

# class dealer(models.Model):
#     name = models.CharField(_("dealer Name"),max_length=100)
#     mobile = models.CharField(_("dealer Mobile No."),max_length=10)
#     old = models.BooleanField(_("Old dealer?"),default=False)
#     new = models.BooleanField(_("New dealer?"),default=False)
#     other = models.BooleanField(_("Others?"),default=False)
#     min_qty = models.IntegerField(_("Minimum Quantity"),)
#     max_qty = models.IntegerField(_("Maximum Quantity"),)
#     pincode = models.CharField(_("dealer Pincode"),max_length=200)
#     geom = models.PointField(_("dealer Location"),blank=True,null=True,default="POINT(73.729974 20.7711857)", srid=4326)

#     def _str_(self):
#         return self.name
