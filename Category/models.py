from django.db import models

# Create your models here.

class Category(models.Model):
    status_choice =(
        ('active', 'active'),
        ('deactive', 'deactive'),
    )
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length = 100, unique = True)
    image = models.ImageField(upload_to='photos/categories',blank=True)
    status = models.CharField(max_length=10, choices=status_choice, default='active')

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    # def get_url(self):
    #     return reverse('products_by_category', args = [self.slug])

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    Substatus_choice =(
        ('active', 'active'),
        ('deactive', 'deactive'),
    )
    unit_choice =(
        ('kg','kg'),
        ('pcs','pcs'),
    )
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    sub_name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)
    unit = models.CharField(max_length=3,choices=unit_choice)
    sub_image = models.ImageField(upload_to='photos/SubCategory',blank=True)
    percentage = models.FloatField(default=0)
    GST = models.FloatField(default=0)
    status = models.CharField(max_length=10, choices=Substatus_choice, default='active')
    # created_date = models.DateTimeField(auto_now_add=True)
    # modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'

    def __str__(self):
        return self.sub_name
