from django.urls import path
from .views import *

urlpatterns = [
    path('contact-form/', CreateContactForm.as_view()),
    path('suggestion-form/', CreateSuggestionForm.as_view()),
    path('mentor-form/', CreateMentorForm.as_view()),
    path('intern-form/', CreateInternForm.as_view()),
    path('investor-form/', CreateInvestorForm.as_view()),
    path('faq/', FAQList.as_view()),

    path('team-members/', get_team_members, name="team_members"),
    path('working-team-members/', get_working_team_members, name="working_team_members"),
    path('happy-customers/', get_happy_customers, name="happy_customers"),
]
