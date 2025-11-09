from django.shortcuts import render, get_object_or_404
from .models import Product
from .utils import generate_barcode_image


def print_barcode(request, pk):
    """🖨️ عرض صفحة طباعة الباركود لمنتج معين"""
    product = get_object_or_404(Product, pk=pk)

    barcode_path = generate_barcode_image(product.barcode or product.sku)

    return render(request, 'products/print_barcode.html', {
        'product': product,
        'barcode_path': barcode_path,
    })


def print_multiple_barcodes(request):
    """🖨️ طباعة باركود لعدة منتجات"""
    ids = request.GET.getlist('ids')
    products = Product.objects.filter(id__in=ids)

    barcode_data = []
    for p in products:
        barcode_path = generate_barcode_image(p.barcode or p.sku)
        barcode_data.append({
            'name': p.name,
            'price': p.price,
            'barcode': p.barcode or p.sku,
            'path': barcode_path
        })

    return render(request, 'products/print_multiple_barcodes.html', {
        'barcode_data': barcode_data
    })