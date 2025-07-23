from rest_framework.response import Response
from WebsiteContent.serializers import *
from WebsiteContent.models import *
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView

# Create your views here.
@permission_classes([AllowAny])
class CreateContactForm(CreateAPIView):
    queryset = ContactForm.objects.all()
    serializer_class = ConatctFormSerializer
    

@permission_classes([AllowAny])
class CreateSuggestionForm(CreateAPIView):
    queryset = SuggestionForm.objects.all()
    serializer_class = SuggestionFormSerializer

@permission_classes([AllowAny])
class CreateMentorForm(CreateAPIView):
    queryset = MentorForm.objects.all()
    serializer_class = MentorFormSerializer         


@permission_classes([AllowAny])
class CreateInternForm(CreateAPIView):
    queryset = InternForm.objects.all()
    serializer_class = InternFormSerializer


@permission_classes([AllowAny])
class CreateInvestorForm(CreateAPIView):
    queryset = InvestorForm.objects.all()
    serializer_class = InvestorFormSerializer

@permission_classes([AllowAny])
class FAQList(APIView):
    def get(self, request):
        faq = FAQ.objects.all()
        serializer = FAQSerializer(faq, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_team_members(request):
    team_members = TeamMember.objects.all()
    serializer = TeamMeberSerializer(team_members, many = True, context={"request": request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_working_team_members(request):
    team_members = WorkingTeamMember.objects.all()
    serializer = WorkingTeamMeberSerializer(team_members, many = True, context={"request": request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_happy_customers(request):
    team_members = HappyCustomers.objects.all()
    serializer = WorkingTeamMeberSerializer(team_members, many = True, context={"request": request})
    return Response(serializer.data)
