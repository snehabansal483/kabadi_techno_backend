from django.db import models

from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator

# Create your models here.
class ContactForm(models.Model):
    status_choice =(
        ('new', 'new'),
        ('view', 'view'),
        ('solved', 'solved'),
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField(max_length=450)
    status = models.CharField(max_length=10, choices=status_choice, default='new')
    form_created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.name}--{self.subject}'

class SuggestionForm(models.Model):
    status_choice =(
        ('new', 'new'),
        ('view', 'view'),
        ('solved', 'solved'),
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=17)
    message = models.TextField(max_length=450)
    status = models.CharField(max_length=10, choices=status_choice, default='new')
    form_created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f'{self.name}--{self.email}' 

class MentorForm(models.Model):
    status_choice =(
        ('new', 'new'),
        ('select', 'select'),
        ('reject', 'reject'),
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=17)
    domain = models.CharField(max_length=100)
    linkedin_id = models.TextField(max_length=450)
    cv = models.FileField(upload_to='mentor_cvs/')
    status = models.CharField(max_length=10, choices=status_choice, default='new')
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
        return f'{self.name}--{self.email}'

class InternForm(models.Model):
    status_choice =(
        ('new', 'new'),
        ('select', 'select'),
        ('reject', 'reject'),
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=17)
    domain = models.CharField(max_length=100)
    linkedin_id = models.TextField(max_length=450)
    cv = models.FileField(upload_to='intern_cvs/')
    status = models.CharField(max_length=10, choices=status_choice, default='new')
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
        return f'{self.name}--{self.email}'

class InvestorForm(models.Model):
    status_choice =(
        ('new', 'new'),
        ('select', 'select'),
        ('reject', 'reject'),
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=17)
    linkedin_id = models.TextField(max_length=450)
    status = models.CharField(max_length=10, choices=status_choice, default='new')
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
        return f'{self.name}--{self.email}'


class FAQ(models.Model):
    status_choice =(
        ('active', 'active'),
        ('deactive', 'deactive'),
    )
    qns = models.TextField(max_length=350)
    ans = models.TextField(max_length=450)
    status = models.CharField(max_length=10, choices=status_choice, default='active')


class CommonInfo(models.Model):
    name = models.CharField(max_length=200)
    dp = models.ImageField(default = 'dp/default_dp.png', validators = [FileExtensionValidator(
                                 ['png', 'jpg', 'jpeg']
                             )], upload_to = 'dp/')
    
    class Meta:
        abstract = True

class TeamMember(CommonInfo):
    status_choice =(
        ('active', 'active'),
        ('deactive', 'deactive'),
    )
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=status_choice, default='active')

    def __str__(self):
        return f'{self.name}--{self.title}'


class WorkingTeamMember(CommonInfo):
    status_choice =(
        ('active', 'active'),
        ('deactive', 'deactive'),
    )
    feedback = models.TextField(max_length=450)
    status = models.CharField(max_length=10, choices=status_choice, default='active')

    def __str__(self):
        return f'{self.name}'

class HappyCustomers(CommonInfo):
    status_choice =(
        ('active', 'active'),
        ('deactive', 'deactive'),
    )
    feedback = models.TextField(max_length=450)
    status = models.CharField(max_length=10, choices=status_choice, default='active')

    def __str__(self):
        return f'{self.name}'