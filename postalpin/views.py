from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DigiPinAddress
from .serializers import DigiPinAddressSerializer

class DigiPinAddressCreateView(APIView):
    def post(self, request):
        serializer = DigiPinAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Triggers signal
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyDigiPIN(APIView):
    def post(self, request):
        digipin = request.data.get('digipin')
        if not digipin:
            return Response({'error': 'DigiPIN is required'}, status=status.HTTP_400_BAD_REQUEST)

        address_obj = DigiPinAddress.objects.filter(digipin=digipin).first()

        if address_obj:
            serializer = DigiPinAddressSerializer(address_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid DigiPIN'}, status=status.HTTP_404_NOT_FOUND)
