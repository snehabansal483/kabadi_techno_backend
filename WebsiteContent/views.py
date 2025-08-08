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
    def get(self, request):
        contacts = ContactForm.objects.all()
        serializer = ConatctFormSerializer(contacts, many=True)
        return Response(serializer.data)
    def post(self, request):
        if request.data.get('delete_all', False):
            ContactForm.objects.all().delete()
            return Response({'message': 'All contact form data deleted.'})
        return super().post(request)
    

@permission_classes([AllowAny])
class CreateSuggestionForm(CreateAPIView):
    queryset = SuggestionForm.objects.all()
    serializer_class = SuggestionFormSerializer
    def get(self, request):
        suggestions = SuggestionForm.objects.all()
        serializer = SuggestionFormSerializer(suggestions, many=True)
        return Response(serializer.data)
    def post(self, request):
        if request.data.get('delete_all', False):
            SuggestionForm.objects.all().delete()
            return Response({'message': 'All suggestion form data deleted.'})
        return super().post(request)

@permission_classes([AllowAny])
class CreateMentorForm(CreateAPIView):
    queryset = MentorForm.objects.all()
    serializer_class = MentorFormSerializer         
    def get(self, request):
        mentors = MentorForm.objects.all()
        serializer = MentorFormSerializer(mentors, many=True)
        return Response(serializer.data)
    def post(self, request):
        if request.data.get('delete_all', False):
            MentorForm.objects.all().delete()
            return Response({'message': 'All mentor form data deleted.'})
        return super().post(request)


@permission_classes([AllowAny])
class CreateInternForm(CreateAPIView):
    queryset = InternForm.objects.all()
    serializer_class = InternFormSerializer
    def get(self, request):
        interns = InternForm.objects.all()
        serializer = InternFormSerializer(interns, many=True)
        return Response(serializer.data)
    def post(self, request):
        if request.data.get('delete_all', False):
            InternForm.objects.all().delete()
            return Response({'message': 'All intern form data deleted.'})
        return super().post(request)


@permission_classes([AllowAny])
class CreateInvestorForm(CreateAPIView):
    queryset = InvestorForm.objects.all()
    serializer_class = InvestorFormSerializer
    def get(self, request):
        investors = InvestorForm.objects.all()
        serializer = InvestorFormSerializer(investors, many=True)
        return Response(serializer.data)
    def post(self, request):
        if request.data.get('delete_all', False):
            InvestorForm.objects.all().delete()
            return Response({'message': 'All investor form data deleted.'})
        return super().post(request)

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