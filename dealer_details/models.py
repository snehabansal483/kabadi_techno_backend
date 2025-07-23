from email.policy import default
from django.db import models
from Category.models import Category, SubCategory
from accounts.models import DealerProfile
#from django.db.models import Avg, Count
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django_better_admin_arrayfield.models.fields import ArrayField
from dealer.models import dealer
from marketplace.models import Marketplace
#from dealer_details.models import Pincodes
#Create your models here.
class PriceList(models.Model):
    unit_choice =(
        ('kg','kg'),
        ('pcs','pcs'),
    )
    category = models.IntegerField()
    category_name = models.CharField(max_length=250)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    subcategory_name = models.CharField(max_length=250)
    subcategory_image = models.ImageField(upload_to='photos/SubCategory',blank=True)
    slug = models.CharField(max_length=50)
    unit = models.CharField(max_length=3,choices=unit_choice)
    GST = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    dealer = models.ForeignKey(DealerProfile, on_delete=models.CASCADE)
    dealer_account_type = models.CharField(max_length = 50, default = 'Kabadi')
    pincode = models.CharField(max_length=6)
    price = models.IntegerField()
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, null = True, blank = True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subcategory.sub_name + '-' + str(self.price)

    def save(self, *args, **kwargs):
        self.category = self.subcategory.category_id
        self.category_name = self.subcategory.category.name
        self.subcategory_name = self.subcategory.sub_name
        self.subcategory_image = self.subcategory.sub_image
        self.GST = self.subcategory.GST
        self.unit = self.subcategory.unit
        self.percentage = self.subcategory.percentage
        self.dealer_account_type = self.dealer.auth_id.account_type
        self.slug = slugify(self.subcategory) + '-' + str(self.price)
        super(PriceList, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Price List'
        verbose_name_plural = 'Price Lists'

class add_category(models.Model):
    status_choice =(
        ('INPROGRESS','INPROGRESS'),
        ('ACCEPTED','ACCEPTED'),
        ('CANCEL','CANCEL'),
    )

    dealer_id = models.ForeignKey(DealerProfile, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    category_image = models.ImageField(upload_to='photos/add_category',blank=True, default = 'photos/Profile_Pic.png')
    status = models.CharField(max_length=20, choices=status_choice, default='INPROGRESS')
    description = models.CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Add Category'
        verbose_name_plural = 'Add Categories'

class documents(models.Model):
    #dealer_id = models.ForeignKey(dealerProfile, on_delete=models.CASCADE)
    doc_status = [
        ('INPROGRESS','INPROGRESS'),
        ('ACCEPTED','ACCEPTED'),
        ('CANCEL','CANCEL'),
    ]
    Aadhar_card = models.FileField(validators = [FileExtensionValidator(
                                 ['png', 'jpg', 'jpeg', 'pdf']
                             )], upload_to='documents/aadhar_card')
    dealer = models.ForeignKey(dealer,on_delete=models.CASCADE,null=True)
    status=models.CharField(max_length=12, choices=doc_status, default='INPROGRESS')
    Pic = models.ImageField(validators = [FileExtensionValidator(
                                 ['png', 'jpg', 'jpeg']
                             )], upload_to='documents/Picture', null = True, blank = True)
    OtherDocuments = models.FileField(validators = [FileExtensionValidator(
                                 ['pdf']
                             )],upload_to='documents/Other_Documents', null = True, blank = True)
    GSTcertificate = models.FileField(validators = [FileExtensionValidator(
                                 ['pdf']
                             )],upload_to='documents/GST_certificate', null = True, blank = True)
    CompanyPAN = models.FileField(validators = [FileExtensionValidator(
                                 ['pdf']
                             )],upload_to='documents/Company_PAN', null = True, blank = True)
    CompanyIncopration  = models.FileField(validators = [FileExtensionValidator(
                                 ['pdf']
                             )],upload_to='documents/Company_Incopration', null = True, blank = True)

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

class GetPincodes(models.Model):
    dealer_id = models.ForeignKey(DealerProfile, on_delete=models.CASCADE)
    pincode1 = models.CharField(max_length=6, null=True, blank=True)
    pincode2 = models.CharField(max_length=6, null=True, blank=True)
    pincode3 = models.CharField(max_length=6, null=True, blank=True)
    pincode4 = models.CharField(max_length=6, null=True, blank=True)
    pincode5 = models.CharField(max_length=6, null=True, blank=True)
    pincode6 = models.CharField(max_length=6, null=True, blank=True)
    pincode7 = models.CharField(max_length=6, null=True, blank=True)
    pincode8 = models.CharField(max_length=6, null=True, blank=True)
    pincode9 = models.CharField(max_length=6, null=True, blank=True)
    pincode10 = models.CharField(max_length=6, null=True, blank=True)
    addrequest = models.CharField(max_length=6, null=True, blank=True)
    no_of_pincodes = models.IntegerField(default = 5, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.dealer_id.auth_id) 

    class Meta:
        verbose_name = 'GetPincode'
        verbose_name_plural = 'GetPincodes'
