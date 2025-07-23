from import_export import resources
from .models import *

class ContactFormAdminResources(resources.ModelResource):
    class Meta:
        model = ContactForm

class SuggestionFormAdminResources(resources.ModelResource):
    class Meta:
        model = SuggestionForm

class InternFormAdminResources(resources.ModelResource):
    class Meta:
        model = InternForm

class InvestorFormAdminResources(resources.ModelResource):
    class Meta:
        model = InvestorForm

class MentorFormAdminResources(resources.ModelResource):
    class Meta:
        model = MentorForm

class FAQAdminResources(resources.ModelResource):
    class Meta:
        model = FAQ

class TeamMemberAdminResources(resources.ModelResource):
    class Meta:
        model = TeamMember

class WorkingTeamMemberAdminResources(resources.ModelResource):
    class Meta:
        model = WorkingTeamMember

class HappyCustomersAdminResources(resources.ModelResource):
    class Meta:
        model = HappyCustomers