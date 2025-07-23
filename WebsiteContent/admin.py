from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.utils.html import format_html
import admin_thumbnails
from import_export.admin import ImportExportModelAdmin
from .resources import *

class ContactFormAdmin(ImportExportModelAdmin):
    list_display= ('id', 'form_created_at', 'name', 'email', 'subject', 'status')
    list_display_links = ('id', 'name', 'email')
    readonly_fields = ('form_created_at',)
    ordering = ('-form_created_at',)
    filter_horizontal=()
    list_filter=()
    resource_class = ContactFormAdminResources

class SuggestionFormAdmin(ImportExportModelAdmin):
    list_display= ('id', 'form_created_at', 'name', 'email', 'phone', 'status')
    list_display_links = ('id', 'name', 'email')
    filter_horizontal=()
    ordering=()
    list_filter=()
    resource_class = SuggestionFormAdminResources


class MentorFormAdmin(ImportExportModelAdmin):
    list_display= ('id', 'created_at', 'name', 'email', 'phone', 'linkedin_id', 'status')
    list_display_links = ('id', 'name', 'email')
    filter_horizontal=()
    ordering=('-created_at',)
    list_filter=()
    resource_class = MentorFormAdminResources


class InternFormAdmin(ImportExportModelAdmin):
    list_display= ('id', 'created_at', 'name', 'email', 'phone', 'domain', 'status')
    list_display_links = ('id', 'name', 'email')
    filter_horizontal=()
    ordering=('-created_at',)
    list_filter=()
    resource_class = InternFormAdminResources


class InvestorFormAdmin(ImportExportModelAdmin):
    list_display= ('id', 'created_at', 'name', 'email', 'phone', 'linkedin_id', 'status')
    list_display_links = ('id', 'name', 'email')
    filter_horizontal=()
    ordering=('-created_at',)
    list_filter=()
    resource_class = InvestorFormAdminResources


class FAQAdmin(ImportExportModelAdmin):
    list_display= ('id', 'qns', 'ans', 'status')
    list_display_links = ('id', 'qns', 'ans')
    filter_horizontal=()
    ordering=()
    list_filter=()
    resource_class = FAQAdminResources


@admin_thumbnails.thumbnail('dp')
class TeamMemberAdmin(ImportExportModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="50" style="border-radius:50%;">'.format(object.dp.url))
    thumbnail.short_description = "DP"
    list_display= ('id', 'name', 'thumbnail', 'status')
    list_display_links = ('id', 'name', 'thumbnail')
    filter_horizontal=()
    ordering=()
    list_filter=()
    resource_class = TeamMemberAdminResources


@admin_thumbnails.thumbnail('dp')
class WorkingTeamMemberAdmin(ImportExportModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="50" style="border-radius:50%;">'.format(object.dp.url))
    thumbnail.short_description = "DP"
    list_display= ('id', 'name', 'thumbnail', 'status')
    list_display_links = ('id', 'name', 'thumbnail')
    filter_horizontal=()
    ordering=()
    list_filter=()
    resource_class = WorkingTeamMemberAdminResources


@admin_thumbnails.thumbnail('dp')
class HappyCustomersAdmin(ImportExportModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="50" style="border-radius:50%;">'.format(object.dp.url))
    thumbnail.short_description = "DP"
    list_display= ('id', 'name', 'thumbnail', 'status')
    list_display_links = ('id', 'name', 'thumbnail')
    filter_horizontal=()
    ordering=()
    list_filter=()
    resource_class = HappyCustomersAdminResources


# Register your models here.
admin.site.register(ContactForm, ContactFormAdmin)
admin.site.register(SuggestionForm, SuggestionFormAdmin)
admin.site.register(InternForm, InternFormAdmin)
admin.site.register(InvestorForm, InvestorFormAdmin)
admin.site.register(MentorForm, MentorFormAdmin)
admin.site.register(FAQ, FAQAdmin)
admin.site.register(TeamMember,TeamMemberAdmin)
admin.site.register(WorkingTeamMember, WorkingTeamMemberAdmin)
admin.site.register(HappyCustomers, HappyCustomersAdmin)
