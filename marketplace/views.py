from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from datetime import date
from .serializers import *
from .models import Marketplace
from accounts.models import DealerProfile

from PIL import Image
import qrcode
import os

def convert_text_to_qrcode(text, filename, request):
    """Generate a QR code with a central logo and return its path and URL."""
    print(f"Generating QR code for: {text}, filename: {filename}")

    # Create QR code
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(text)
    qr.make()
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Try to load logo, if it exists
    logo_path = os.path.join(settings.MEDIA_ROOT, 'marketplace/QRs/logo.png')
    print(f"Looking for logo at: {logo_path}")
    
    try:
        if os.path.exists(logo_path):
            print("Logo file found, loading...")
            logo = Image.open(logo_path)
            
            # Resize logo
            basewidth = 100
            wpercent = (basewidth / float(logo.size[0]))
            hsize = int((float(logo.size[1]) * float(wpercent)))
            logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS)

            # Paste logo at the center
            pos = ((qr_img.size[0] - logo.size[0]) // 2,
                   (qr_img.size[1] - logo.size[1]) // 2)
            qr_img.paste(logo, pos)
            print("Logo added to QR code successfully")
        else:
            print(f"Logo file not found at {logo_path}")
    except Exception as e:
        # If logo loading fails, continue without logo
        print(f"Warning: Could not load logo: {e}")
        pass

    # Save QR code
    qr_filename = f"{filename}.jpg"
    qr_directory = os.path.join(settings.MEDIA_ROOT, 'marketplace/QRs')
    
    # Create directory if it doesn't exist
    os.makedirs(qr_directory, exist_ok=True)
    
    qr_image_path = os.path.join(qr_directory, qr_filename)
    qr_img.save(qr_image_path)

    # Construct public URL
    domain = get_current_site(request).domain
    qr_code_url = f"http://{domain}/media/marketplace/QRs/{qr_filename}"
    qr_code_image_path = f"/marketplace/QRs/{qr_filename}"

    return qr_code_image_path, qr_code_url


class CreateMarketplace(APIView):
    serializer_class = CreateMarketplaceSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            dealer_ktid = request.data['dealer_ktid']

            try:
                # Get dealer object using kt_id
                dealer = DealerProfile.objects.get(kt_id=dealer_ktid)
                
                # Check if marketplace already exists
                if Marketplace.objects.filter(dealer_id=dealer).exists():
                    return Response({'unsuccessful': 'This dealer already has a Marketplace created'},
                                    status=status.HTTP_306_RESERVED)

                # Get dealer's active subscription to determine end_duration
                from payment_gateway.models import DealerSubscription
                current_subscription = DealerSubscription.objects.filter(
                    dealer=dealer, 
                    status='active'
                ).first()
                
                if not current_subscription or not current_subscription.is_active:
                    return Response({
                        'error': 'No active subscription found',
                        'message': 'Dealer must have an active subscription to create marketplace'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Create Marketplace using subscription end date
                marketplace = Marketplace.objects.create(
                    dealer_id=dealer,
                    end_duration=current_subscription.end_date.date(),
                    status='active'  # Set status as active immediately
                )

                # Generate QR URL
                Dkt_id = marketplace.kt_id
                current_site_frontend = 'http://localhost:5173'
                qr_url = f"{current_site_frontend}/marketplace/{Dkt_id}"
                qr_code_image_path, qr_code_url = convert_text_to_qrcode(qr_url, Dkt_id, request)

                # Save QR code path and URL to Marketplace
                marketplace.qrCode = qr_code_image_path
                marketplace.url = qr_code_url
                marketplace.save()

                return Response({
                    'success': 'Marketplace created and QR code generated',
                    'marketplace_id': marketplace.kt_id,
                    'dealer_ktid': dealer_ktid,
                    'end_duration': marketplace.end_duration,
                    'qr_code_url': qr_code_url,
                    'qr_code_path': qr_code_image_path,
                    'frontend_url': qr_url,
                    'qr_display_url': f"{request.build_absolute_uri('/').rstrip('/')}/marketplace/qr-display/{marketplace.kt_id}/",
                    'subscription_expires': current_subscription.end_date
                }, status=status.HTTP_202_ACCEPTED)
            
            except DealerProfile.DoesNotExist:
                return Response(
                    {'error': 'Dealer profile not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )


class GetMarketplace(APIView):
    def get(self, request, kt_id):
        # Check if marketplace exists
        marketplace = Marketplace.objects.filter(kt_id=kt_id).first()
        if not marketplace:
            return Response({'error': 'Marketplace not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if dealer has active subscription
        from payment_gateway.models import DealerSubscription
        dealer = marketplace.dealer_id
        current_subscription = DealerSubscription.objects.filter(
            dealer=dealer, 
            status='active'
        ).first()
        
        # If no active subscription or marketplace is inactive, block access
        if not current_subscription or not current_subscription.is_active or marketplace.status != 'active':
            return Response({
                'error': 'Marketplace access denied',
                'message': 'This marketplace is currently not accessible. Subscription may have expired.',
                'marketplace_status': marketplace.status,
                'subscription_active': current_subscription.is_active if current_subscription else False,
                'dealer_kt_id': dealer.kt_id,
                'subscription_required': True
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Return marketplace data if access is granted
        serializer = GetMarketplaceSerializer([marketplace], many=True)
        response_data = serializer.data[0] if serializer.data else {}
        response_data['access_granted'] = True
        response_data['subscription_expires'] = current_subscription.end_date
        response_data['subscription_type'] = current_subscription.plan.plan_type
        response_data['days_remaining'] = current_subscription.days_remaining
        response_data['dealer_name'] = dealer.auth_id.full_name if dealer.auth_id else dealer.kt_id
        response_data['dealer_profile_type'] = dealer.profile_type
        
        return Response(response_data)


class ListActiveMarketplaces(APIView):
    """List all marketplaces that have active subscriptions"""
    
    def get(self, request):
        from payment_gateway.models import DealerSubscription
        
        # Get all dealers with active subscriptions
        active_subscriptions = DealerSubscription.objects.filter(
            status='active'
        ).select_related('dealer')
        
        # Get marketplaces for dealers with active subscriptions
        active_dealers = [sub.dealer for sub in active_subscriptions if sub.is_active]
        
        marketplaces = Marketplace.objects.filter(
            dealer_id__in=active_dealers,
            status='active'
        )
        
        marketplace_data = []
        for marketplace in marketplaces:
            # Get subscription info for each marketplace
            subscription = DealerSubscription.objects.filter(
                dealer=marketplace.dealer_id,
                status='active'
            ).first()
            
            if subscription and subscription.is_active:
                serializer = GetMarketplaceSerializer(marketplace)
                data = serializer.data
                data['subscription_expires'] = subscription.end_date
                data['subscription_type'] = subscription.plan.plan_type
                data['days_remaining'] = subscription.days_remaining
                data['dealer_name'] = marketplace.dealer_id.auth_id.full_name if marketplace.dealer_id.auth_id else marketplace.dealer_id.kt_id
                data['dealer_profile_type'] = marketplace.dealer_id.profile_type
                marketplace_data.append(data)
        
        return Response({
            'count': len(marketplace_data),
            'marketplaces': marketplace_data
        })


def marketplace_qr_display(request, kt_id):
    """Display QR code in a beautiful template with Kabadi Techno branding"""
    
    # Get marketplace
    marketplace = get_object_or_404(Marketplace, kt_id=kt_id)
    
    # Get dealer information
    dealer = marketplace.dealer_id
    dealer_name = dealer.auth_id.full_name if dealer.auth_id else dealer.kt_id
    
    # Get subscription information
    from payment_gateway.models import DealerSubscription
    subscription = DealerSubscription.objects.filter(
        dealer=dealer,
        status='active'
    ).first()
    
    # Calculate days remaining
    days_remaining = 0
    if subscription and subscription.is_active:
        days_remaining = subscription.days_remaining
    
    context = {
        'marketplace': marketplace,
        'dealer_name': dealer_name,
        'subscription': subscription,
        'days_remaining': days_remaining,
        'current_date': timezone.now(),
    }
    
    return render(request, 'marketplace/qr_display.html', context)
