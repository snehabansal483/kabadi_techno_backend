from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Address
from .serializers import AddressSerializer

class AddressCreateView(APIView):
    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Triggers signal
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyDigiPIN(APIView):
    def post(self, request):
        digipin = request.data.get('digipin')
        if not digipin:
            return Response({'error': 'DigiPIN is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            address_obj = Address.objects.get(digipin=digipin)
            serializer = AddressSerializer(address_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Address.DoesNotExist:
            return Response({'error': 'Invalid DigiPIN'}, status=status.HTTP_404_NOT_FOUND)