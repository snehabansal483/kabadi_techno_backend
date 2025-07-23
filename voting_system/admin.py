from django.contrib import admin

from .models import Voters, Votes

# Register your models here.
class VotesAdmin(admin.ModelAdmin):
    list_display= ('id', 'title', 'yes_count', 'no_count')
    list_display_links = ('id', 'title',)
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    # readonly_fields=('yes_count', 'no_count')

class VotersAdmin(admin.ModelAdmin):
    list_display= ('id', 'vote', 'ip', 'status')
    list_display_links = ('id', 'vote', 'ip', 'status')
    ordering=()
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Votes, VotesAdmin)
admin.site.register(Voters, VotersAdmin)