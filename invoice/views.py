from order.models import Order, OrderProduct  
from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.conf import settings
import os

def dealer_invoice_view(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        order_items = OrderProduct.objects.filter(order=order)
    except Order.DoesNotExist:
        return render(request, 'invoice/dealer_invoice.html', {
            'order': None,
            'order_found': False,
            'order_number': order_number
        })

    # Calculate line totals and grand total
    grand_total = 0
    for item in order_items:
        item.total = item.quantity * item.price
        grand_total += item.total

    context = {
        'order': order,
        'order_items': order_items,
        'grand_total': grand_total,
        'order_found': True,
        'order_number': order_number,
        
    }

    if request.GET.get("download") == "pdf":
        template_path = 'invoice/dealer_invoice.html'
        template = get_template(template_path)
        html = template.render(context)
        output_path = os.path.join(settings.MEDIA_ROOT, 'invoices')
        os.makedirs(output_path, exist_ok=True)
        filename = f"invoice_{order_number}.pdf"
        full_path = os.path.join(output_path, filename)

        with open(full_path, "wb") as f:
            pisa.CreatePDF(html, dest=f)

        with open(full_path, "rb") as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

    return render(request, 'invoice/dealer_invoice.html', context)
