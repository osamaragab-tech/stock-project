from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F, ExpressionWrapper, DecimalField, Case, When, Value
from django.utils.translation import gettext as _
from .models import Product, Category
from inventory.models import StockMovement
from django.db.models import Sum, Case, When, IntegerField
from .utils import generate_barcode_image





def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    stock_movements = StockMovement.objects.filter(product=product).order_by('-date')
    return render(request, 'products/product_detail.html', {
        'product': product,
        'stock_movements': stock_movements
    })

@login_required
def products_list(request):
    products = Product.objects.all().annotate(
        on_hand_calc=Sum(
            Case(
                When(stockmovement__movement_type='in', then=F('stockmovement__quantity')),
                When(stockmovement__movement_type='out', then=-F('stockmovement__quantity')),
                default=0,
                output_field=IntegerField()
            )
        )
    )
    return render(request, 'products/products_list.html', {'products': products})


def get_category_tree(categories):
    """ترتيب الفئات بشكل هرمي بدون إخفاء أي فئة"""
    def build_tree(parent=None, prefix=""):
        tree = []
        for cat in categories.filter(parent=parent).order_by('name'):
            tree.append((cat.id, prefix + cat.name))
            tree.extend(build_tree(cat, prefix + "— "))
        return tree

    # نبدأ بكل الفئات اللي مالهاش parent
    tree = build_tree()

    # نضيف أي فئة يتيمة مالهاش parent معروف (لو حصل خلل في الربط)
    used_ids = [t[0] for t in tree]
    for cat in categories.exclude(id__in=used_ids).order_by('name'):
        tree.append((cat.id, cat.name))
    return tree


@login_required
def new_product(request):
    all_categories = Category.objects.all()
    categories = get_category_tree(all_categories)

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        sku = (request.POST.get('sku') or '').strip()
        price = request.POST.get('price') or 0
        beginning_balance = int(request.POST.get('beginning_balance') or 0)
        description = request.POST.get('description')
        image = request.FILES.get('image')
        product_type = request.POST.get('product_type')
        category_name = (request.POST.get('category_name') or '').strip()
        parent_id = request.POST.get('parent_category')

        # 🟩 تحديد الفئة
        category = None
        if category_name:
            category_obj = Category.objects.filter(name__iexact=category_name).first()
            if category_obj:
                category = category_obj
            else:
                parent = Category.objects.filter(id=parent_id).first() if parent_id else None
                category = Category.objects.create(name=category_name, parent=parent)
                if parent:
                    messages.success(request, f"🆕 تم إنشاء الفئة الفرعية '{category_name}' تحت '{parent.name}'.")
                else:
                    messages.success(request, f"🆕 تم إنشاء الفئة '{category_name}' بنجاح.")

        # 🟥 تحقق من التكرار
        if Product.objects.filter(name__iexact=name).exists():
            messages.error(request, f"⚠️ المنتج '{name}' موجود بالفعل.")
            return render(request, 'products/new_product.html', {'categories': categories, 'old_data': request.POST})

        if Product.objects.filter(sku__iexact=sku).exists():
            messages.error(request, f"⚠️ كود المنتج '{sku}' مستخدم بالفعل.")
            return render(request, 'products/new_product.html', {'categories': categories, 'old_data': request.POST})

        # 🟩 إنشاء المنتج
        product = Product.objects.create(
            name=name,
            sku=sku,
            price=price,
            beginning_balance=beginning_balance,
            description=description,
            image=image,
            category=category,
            product_type=product_type
        )

        # 🧾 إضافة رصيد افتتاحي كحركة مخزون
        if beginning_balance > 0:
            StockMovement.objects.create(
                product=product,
                quantity=beginning_balance,
                movement_type='in',
                description="رصيد افتتاحي للمنتج الجديد"
            )

        messages.success(request, f"✅ تم إضافة المنتج '{name}' بنجاح.")
        return redirect('products:products_list')

    return render(request, 'products/new_product.html', {'categories': categories})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    all_categories = Category.objects.all()
    categories = get_category_tree(all_categories)

    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.sku = request.POST.get('sku', '').strip()
        product.price = request.POST.get('price') or 0
        product.beginning_balance = int(request.POST.get('beginning_balance') or 0)
        product.description = request.POST.get('description', '')
        product.product_type = request.POST.get('product_type', 'inventory')

        parent_id = request.POST.get('parent_category')
        parent = Category.objects.filter(id=parent_id).first() if parent_id else None

        # ✅ لو الفئة الحالية موجودة و الأب اتغير، نعمل نسخة جديدة من الفئة
        if product.category:
            current_category = product.category
            if current_category.parent != parent:
                # نعمل فئة جديدة بنفس الاسم لكن بأب مختلف
                new_category = Category.objects.create(
                    name=current_category.name,
                    parent=parent
                )
                product.category = new_category
        else:
            # لو المنتج ملوش فئة أساسًا
            category_id = request.POST.get('parent_category')
            if category_id:
                product.category = Category.objects.filter(id=category_id).first()

        image = request.FILES.get('image')
        if image:
            product.image = image

        product.save()
        messages.success(request, _("✅ Product updated successfully."))
        return redirect('products:products_list')

    return render(request, 'products/edit_product.html', {
        'product': product,
        'categories': categories,
        'parent_id': product.category.parent.id if (product.category and product.category.parent) else '',
    })