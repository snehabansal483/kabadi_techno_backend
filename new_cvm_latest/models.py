from django.db import models


class CvmRegistration(models.Model):
    uid = models.CharField(max_length=100, unique=True)
    imei_number = models.CharField(max_length=20)
    cvm_name = models.CharField(max_length=20)
    cvm_model = models.CharField(max_length=20)
    location = models.CharField(default = 'Hankuna matata',max_length=240, null=True, blank=True)
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    area = models.CharField(max_length=20)
    pincode = models.IntegerField()
    volume = models.SmallIntegerField(default = 0, blank = True, null=True)
    weight = models.DecimalField(decimal_places=2, max_digits=20, default = 0.0, blank = True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True,null=True) 
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.uid:
            self.uid = "CVM" + str(self.id + (10 ** 5))
            self.save()
        
    def __str__(self):
        return self.uid

class QRCode(models.Model):
    user_type = models.CharField(max_length=80, null=True)
    user_id = models.CharField(max_length=80, null=True)
    user_email_id = models.EmailField(max_length = 220, null=True)
    cvm_id = models.ForeignKey(CvmRegistration, on_delete=models.CASCADE)
    cvm_uid = models.CharField(max_length=80, null = True)
    pass_code = models.CharField(max_length=6, default = '000000')
    active = models.BooleanField(default=True)
    scaned = models.BooleanField(default=False)
    qr_code = models.CharField(max_length=80)
    qr_image = models.ImageField(upload_to='qrcode_images', null=True)

    def save(self, *args, **kwargs):
        self.cvm_uid = self.cvm_id.uid
        super(QRCode, self).save(*args, **kwargs)
        
class CvmDetails(models.Model):
    qrcode = models.ForeignKey(QRCode, on_delete=models.CASCADE)
    cvm_id = models.IntegerField()
    cvm_uid = models.CharField(max_length=80)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    weight = models.DecimalField(decimal_places=2, max_digits=20)
    volume = models.IntegerField()

    def save(self, *args, **kwargs):
        self.cvm_id = self.qrcode.cvm_id_id
        self.cvm_uid = self.qrcode.cvm_uid
        self.weight = self.qrcode.cvm_id.weight
        self.volume = self.qrcode.cvm_id.volume
        super(CvmDetails, self).save(*args, **kwargs)

class UnloadScrap(models.Model):
    cvm_unload_status = (
    ('REQUESTED','REQUESTED'),
    ('PENDING','PENDING'),
    ('COMPLETED','COMPLETED'),
    ('CANCELLED','CANCELLED')
)
    cvm_id = models.ForeignKey(CvmRegistration, on_delete = models.CASCADE)
    dealer_id = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=cvm_unload_status, default = 'REQUESTED')
    active = models.BooleanField(default=True)



class cart(models.Model):
    status = (
    ('in_machine','in_machine'),
    ('picked_up','picked_up'),
    #('Cancel','Cancel'),
)
    cart_id = models.CharField(max_length=25,unique=True,null=True)
    customer_ktid = models.CharField(max_length=20,null=True)
    customer_email = models.EmailField(max_length=255,null=True)
    qr_id = models.IntegerField(null=True)
    cvm_uid = models.CharField(max_length=20,null=True)
    weight = models.DecimalField(decimal_places=2, max_digits=20,null=True)
    volume = models.IntegerField()
    image = models.ImageField(upload_to='cvmphotos',null=True)
    approx_price = models.DecimalField(decimal_places=2, max_digits=20,null=True)
    other_comment =  models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=10, choices=status, default = 'in_machine')
    order_id = models.CharField(max_length=25,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     if not self.uid:
    #         self.cart_id = "KTCVM" + str(self.id + (10 ** 5))
    #         self.save()

    def __str__(self):
        return str(self.id)

class order(models.Model):
    status = (
    ('pending','pending'),
    ('completed','completed'),
    ('in_process','in_process'),
    #('Cancel','Cancel'),
)
    
    order_id = models.CharField(max_length=25,unique=True,null=True)
    dealer_ktid = models.CharField(max_length=20,null=True)
    dealer_email = models.EmailField(max_length=255,null=True)
    qr_id = models.IntegerField(null=True)
    cvm_uid = models.CharField(max_length=20,null=True)
    total_cart_no = models.IntegerField(null=True)
    all_cart_ids = models.TextField(null=True)
    weight = models.DecimalField(decimal_places=2, max_digits=2000,null=True)
    volume = models.IntegerField(null=True)
    image = models.ImageField(upload_to='cvmphotos',null=True)
    other_comment =  models.CharField(max_length=100,null=True)
    status = models.CharField(max_length=10, choices=status, default = 'pending')
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.order_id:
            self.order_id = "ORDER" + str(self.id + (10 ** 5))
            self.save()

    

    def __str__(self):
        return str(self.id)