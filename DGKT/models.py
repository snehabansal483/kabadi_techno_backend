from functools import partial
import os
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator 
# Create your models here.
class DGKabadiTechno(models.Model):
    aadhar_status_choice =(
        ('Pending','Pending'),
        ('Verified','Verified'),
        ('Rejected','Rejected'),
    )
    status_choice =(
        ('active','active'),
        ('unactive','unactive'),
    )
    kt_id = models.CharField(max_length = 100)
    account_type = models.CharField(max_length = 100)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone_number = models.CharField(max_length=12)
    aadhar_number = models.IntegerField(validators=[
            MaxValueValidator(999999999999),
            MinValueValidator(000000000000)
        ])
    aadhar_status = models.CharField(max_length=12, choices = aadhar_status_choice, default = 'Pending')
    ProfilePic = models.ImageField(default = 'photos/Profile_Pic.png', upload_to='DGKT/ProfilePic', null = True, blank = True)
    DGLogo = models.ImageField(default = 'photos/Profile_Pic.png', upload_to='DGKT/DGLogo')
    DGLogoWoBg = models.ImageField(default = 'photos/Profile_Pic.png', upload_to='DGKT/DGLogoWoBg')
    # DG LOGO WITHOUT BACKGROUND
    otp = models.CharField(max_length=7, default = '000000')
    DGPin = models.IntegerField(validators=[
            MaxValueValidator(999999),
            MinValueValidator(000000)
        ])
    status = models.CharField(max_length=12, choices = status_choice, default = 'unactive')

    def __str__(self):
        return self.kt_id

    class Meta:
        verbose_name = 'DG Kabadi Techno'
        verbose_name_plural = 'DG Kabadi Techno'
import hashlib

# def hash_file(filename):
#    """"This function returns the SHA-1 hash
#    of the file passed into it"""

#    # make a hash object
#    h = hashlib.sha1()

#    # open file for reading in binary mode
#    with open(filename,'rb') as file:

#        # loop till the end of the file
#        chunk = 0
#        while chunk != b'':
#            # read only 1024 bytes at a time
#            chunk = file.read(1024)
#            h.update(chunk)

#    # return the hex representation of digest
#    return h.hexdigest()

def hash_file(file, block_size=65536):
    hasher = hashlib.md5()
    for buf in iter(partial(file.read, block_size), b''):
        hasher.update(buf)

    return hasher.hexdigest()


def upload_to(instance, filename):
    """
    :type instance: dolphin.models.File
    """
    instance.file.open()
    filename_base, filename_ext = os.path.splitext(filename)

    return "{0}.{1}".format(hash_file(instance.file), filename_ext)

class DGDetails(models.Model): 
    DGkt = models.ForeignKey(DGKabadiTechno, on_delete = models.CASCADE)
    kt_id = models.CharField(max_length = 100)
    name = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    ip = models.CharField(blank=True, max_length=20)
    DGid = models.CharField(max_length=100, unique=True)
    qr_code = models.CharField(max_length=80, null = True)
    qr_image = models.ImageField(upload_to='DGKT/qrcodes', null=True)
    document = models.FileField(validators = [FileExtensionValidator(
                                 ['pdf']
                             )], upload_to='DGKT/documents', null=True, blank = True)
    document_hash_value = models.CharField(max_length = 255, null = True)
    def save(self, *args, **kwargs):
        self.kt_id = self.DGkt.kt_id
        self.name = self.DGkt.name
        self.DGid = str(str(self.kt_id) + '.' + str(self.DGkt.id) + '.' + str(self.date) + '.' + str(self.time) + '.' + self.ip)
        self.document_hash_value = str(hash_file(self.document))
        super(DGDetails, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'DG Detail'
        verbose_name_plural = 'DG Details'
