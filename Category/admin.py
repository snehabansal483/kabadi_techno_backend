from django.contrib import admin
from .models import Category, SubCategory
from django.utils.html import format_html
import admin_thumbnails
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="50"'.format(object.image.url))
    thumbnail.short_description = "Image"
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('id', 'name', 'slug', 'thumbnail', 'status')
    list_display_links = ('id', 'name', 'slug', 'thumbnail')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

@admin_thumbnails.thumbnail('sub_image')
class SubCategoryAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="50"">'.format(object.sub_image.url))
    thumbnail.short_description = "SubImage"
    prepopulated_fields = {'slug': ('sub_name',)}
    list_display= ('id', 'sub_name', 'slug', 'category', 'thumbnail', 'unit', 'percentage', 'status')
    list_display_links = ('id', 'sub_name', 'slug', 'category', 'thumbnail')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
