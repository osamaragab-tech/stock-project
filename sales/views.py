from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from django.utils import timezone
from .models import Sale, SaleItem, SaleReturn, SaleReturnItem
from inventory.models import StockMovement  # تأكد إنك مستوردها
from django.db import transaction
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required

def get_product_by_barcode(request):
    """ترجع بيانات المنتج بناءً على الباركود"""
    barcode = request.GET.get('barcode')
    if not barcode:
        return JsonResponse({'error': 'No barcode provided'}, status=400)

    try:
        product = Product.objects.get(barcode=barcode)
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'sku': product.sku or '',
            'category': product.category.name if product.category else '',
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

def product_search(request):
    """🔍 بحث AJAX عن المنتجات بالاسم أو SKU أو الباركود + رصيد فعلي"""
    q = request.GET.get('q', '').strip()
    results = []

    if q:
        products = Product.objects.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(barcode__icontains=q)
        )
    else:
        products = Product.objects.all()[:10]

    for p in products:
        stock_in = StockMovement.objects.filter(product=p, movement_type='in').aggregate(total=Sum('quantity'))['total'] or 0
        stock_out = StockMovement.objects.filter(product=p, movement_type='out').aggregate(total=Sum('quantity'))['total'] or 0
        on_hand = stock_in - stock_out

        results.append({
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'barcode': p.barcode or '',
            'price': float(p.price),
            'quantity': on_hand,
        })

    return JsonResponse(results, safe=False)

@login_required
def new_sale_return(request):
    sales = Sale.objects.order_by('-date')[:50]
    products = Product.objects.all()

    if request.method == 'POST':
        sale_id = request.POST.get('sale_id')
        notes = request.POST.get('notes', '').strip()
        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')
        prices = request.POST.getlist('price')

        # لا يوجد منتجات
        if not product_ids:
            messages.error(request, "❌ Add at least one product to return.")
            return redirect('sales:new_sale_return')

        # تجهيز قائمة المنتجات المرتجعة
        items_to_return = []
        for i, pid in enumerate(product_ids):
            try:
                qty = int(quantities[i])
            except (IndexError, ValueError):
                qty = 0

            if not pid or qty <= 0:
                continue

            product = get_object_or_404(Product, pk=pid)
            try:
                price = float(prices[i])
            except (IndexError, ValueError):
                price = product.price or 0

            items_to_return.append({'product': product, 'qty': qty, 'price': price})

        # تحقق من صحة العناصر
        if not items_to_return:
            messages.error(request, "❌ No valid return items.")
            return redirect('sales:new_sale_return')

        # التحقق من الفاتورة الأصلية إن وجدت
        sale = None
        if sale_id:
            sale = get_object_or_404(Sale, pk=sale_id)

        # لا يُسمح بإرجاع كمية أكبر من المباعة
        if sale:
            for it in items_to_return:
                product = it['product']
                qty = it['qty']

                sold = SaleItem.objects.filter(sale=sale, product=product).aggregate(
                    total=Sum('quantity')
                )['total'] or 0

                already_returned = SaleReturnItem.objects.filter(
                    sale_return__sale=sale, product=product
                ).aggregate(total=Sum('quantity'))['total'] or 0

                allowed = sold - already_returned
                if qty > allowed:
                    messages.error(
                        request,
                        f"❌ Cannot return {qty} of {product.name}. Max allowed: {allowed}."
                    )
                    return redirect('sales:new_sale_return')

        # إنشاء المردود وتحديث المخزون
        with transaction.atomic():
            sale_return = SaleReturn.objects.create(
                sale=sale,
                created_by=request.user,
                notes=notes
            )

            for it in items_to_return:
                product = it['product']
                qty = it['qty']
                price = it['price']

                SaleReturnItem.objects.create(
                    sale_return=sale_return,
                    product=product,
                    quantity=qty,
                    price=price,
                    subtotal=qty * price
                )

                # ✅ زيادة المخزون (المنتج رجع من العميل)
                product.quantity += qty
                product.save()

                # ✅ سجل حركة المخزون
                StockMovement.objects.create(
                    product=product,
                    quantity=qty,
                    movement_type='in',
                    description=f"Sale return #{sale_return.id}"
                )

            messages.success(
                request,
                f"✅ Sale Return #{sale_return.id} created successfully."
            )
            return redirect('sales:sale_return_detail', return_id=sale_return.id)

    return render(
        request,
        'sales/new_sale_return.html',
        {
            'sales': sales,
            'products': products
        }
    )

@login_required
def sale_returns_list(request):
    returns = SaleReturn.objects.all()
    return render(request, "sales/sale_returns_list.html", {"returns": returns})

@login_required
def sale_return_detail(request, return_id):
    sale_return = get_object_or_404(SaleReturn, id=return_id)
    items = sale_return.items.select_related('product')

    total = sum(item.subtotal for item in items)

    return render(request, 'sales/sale_return_detail.html', {
        'sale_return': sale_return,
        'items': items,
        'total': total,
    })




def new_sale(request):
    products = Product.objects.all()

    if request.method == "POST":
        customer_name = request.POST.get("customer_name", "").strip()
        product_ids = request.POST.getlist("product_id")
        quantities = request.POST.getlist("quantity")
        prices = request.POST.getlist("price")

        if not product_ids:
            messages.error(request, "Please add at least one product.")
            return redirect("sales:new_sale")

        sale = Sale.objects.create(customer_name=customer_name, date=timezone.now())

        total = 0
        for i in range(len(product_ids)):
            try:
                product = Product.objects.get(id=product_ids[i])
                qty = int(quantities[i])
                price = float(prices[i])
                subtotal = qty * price

                # إنشاء عنصر الفاتورة
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    price=price,
                    subtotal=subtotal
                )

                # 🧾 تسجيل حركة خروج بدون تعديل مباشر على المنتج
                StockMovement.objects.create(
                    product=product,
                    quantity=qty,
                    movement_type="out",
                    description=f"Sale #{sale.id} - {customer_name or 'Customer'}"
                )

                total += subtotal

            except Product.DoesNotExist:
                continue

        sale.total_amount = total
        sale.save()

        messages.success(request, f"Invoice #{sale.id} created successfully!")
        return redirect("sales:sale_detail", sale_id=sale.id)

    return render(request, "sales/new_sale.html", {"products": products})



def sale_detail(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    items = sale.items.select_related('product')

    return render(request, "sales/sale_detail.html", {
        "sale": sale,
        "items": items,
    })

def sales_dashboard(request):
    sales = Sale.objects.all().order_by('-date')
    return render(request, "sales/sales_dashboard.html", {"sales": sales})