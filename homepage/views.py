import razorpay
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import Contact, WasteDonation
from .serializers import ContactSerializer,TakeAllContactSerializer, WasteDonationSerializer
class ContactListCreateView(APIView):
    def get(self, request):
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Contact created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ContactCreateView(APIView):
    def get(self, request):
        contacts = Contact.objects.all()
        serializer = TakeAllContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TakeAllContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Initialize Razorpay client with your keys
# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# class CreateDonationView(APIView):
#     def post(self, request):
#         try:
#             name = request.data.get("name")
#             phone_number = request.data.get("phone_number")
#             email = request.data.get("email")
#             amount = float(request.data.get("amount"))  # amount in INR (e.g. 500.00)

#             # Create Razorpay order (amount in paise)
#             razorpay_order = razorpay_client.order.create({
#                 "amount": int(amount * 100),  # e.g. 500 * 100 = 50000
#                 "currency": "INR",
#                 "payment_capture": "1"
#             })

#             # Save order info in DB
#             donation = Donation.objects.create(
#                 name=name,
#                 phone_number=phone_number,
#                 email=email,
#                 amount=amount,
#                 payment_id=razorpay_order["id"],
#                 payment_status="Created"
#             )

#             return Response({
#                 "order_id": razorpay_order["id"],
#                 "razorpay_key": settings.RAZORPAY_KEY_ID,
#                 "amount": amount,
#                 "donation_id": donation.id
#             }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# @api_view(["POST"])
# def payment_success(request):
#     try:
#         order_id = request.data.get("order_id")
#         payment_id = request.data.get("payment_id")
#         # signature = request.data.get("signature")

#         # Verify signature (optional but recommended)
#         # params_dict = {
#         #     'razorpay_order_id': order_id,
#         #     'razorpay_payment_id': payment_id,
#         #     'razorpay_signature': signature
#         # }

#         # This will raise SignatureVerificationError if not valid
#         # razorpay_client.utility.verify_payment_signature(params_dict)

#         # Update payment status
#         donation = Donation.objects.get(payment_id=order_id)
#         donation.payment_status = "Success"
#         donation.payment_id = payment_id  # update real payment ID
#         donation.save()

#         return Response({"status": "Payment verified and recorded."})

#     except razorpay.errors.SignatureVerificationError:
#         return Response({"error": "Signature verification failed."}, status=400)
#     except Donation.DoesNotExist:
#         return Response({"error": "Donation not found."}, status=404)
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def create_waste_donation(request):
    serializer = WasteDonationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_waste_donations(request):
    donations = WasteDonation.objects.all().order_by('-donation_date')
    serializer = WasteDonationSerializer(donations, many=True)
    return Response(serializer.data)        