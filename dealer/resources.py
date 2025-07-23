from import_export import resources
from .models import dealer

class dealersAdminResource(resources.ModelResource):

    def before_import_row(self, row, **kwargs):
        row['name'] = row['name'].capitalize()

    def skip_row(self, instance, original, row, import_validation_errors): #change this fumction signature from 3 argument to 5 argument to match the import_export library's expected signature
        dealers = dealer.objects.filter(name=instance.name,mobile=instance.mobile)
        if dealers.exists():
            return True
        
    class Meta:
        model = dealer
        fields = (
            'id',
            'name',
            'mobile',
            'dealing',
            'min_qty',
            'max_qty',
            'pincode',
            'timing',
            'live_location'
        )






# from import_export import resources
# from .models import dealer

# class dealersAdminResource(resources.ModelResource):

#     def before_import_row(self, row, **kwargs):
#         row['name'] = row['name'].capitalize()

#     def skip_row(self, instance,original):
#         dealers = dealer.objects.filter(name=instance.name,mobile=instance.mobile)
#         if dealers.exists():
#             return True
        
#     class Meta:
#         model = dealer
#         fields = (
#             'id',
#             'name',
#             'mobile',
#             'old',
#             'new',
#             'other',
#             'min_qty',
#             'max_qty',
#             'pincode',
#             'geom'
#         )
