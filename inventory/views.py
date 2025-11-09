from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Min, Max
from .models import StockMovement, Transaction
from .forms import StockMovementForm
from products.models import Product

@login_required
def inventory_home(request):
	recent_movements = StockMovement.objects.order_by('-date')[:10]
	products = Product.objects.all()
	context = {
		'recent_movements': recent_movements,
		'products': products,
	}
	return render(request, 'inventory/home.html', context)




@login_required
def add_movement(request):
	if request.method == 'POST':
		form = StockMovementForm(request.POST)
		if form.is_valid():
			movement = form.save(commit=False)
			product = movement.product

			# validate "out" does not make stock negative
			if movement.movement_type == 'out':
				if movement.quantity > product.on_hand:
					messages.error(request, f"❌ لا يوجد كمية كافية ({product.on_hand}) for {product.name}.")
					return redirect('inventory:add_movement')

			movement.save()
			messages.success(request, '✅ Stock movement recorded.')
			return redirect('inventory:inventory_home')
	else:
		form = StockMovementForm()
	return render(request, 'inventory/add_movement.html', {'form': form})




@login_required
def product_movement_report(request):
	start_date = request.GET.get('start_date')
	end_date = request.GET.get('end_date')
	product_id = request.GET.get('product_id')


	movements = StockMovement.objects.all()
	if start_date:
		movements = movements.filter(date__date__gte=start_date)
	if end_date:
		movements = movements.filter(date__date__lte=end_date)
	if product_id and product_id != 'all':
		movements = movements.filter(product_id=product_id)


	report_data = (
		movements
		.values('product__id', 'product__name')
		.annotate(
			first_date=Min('date'),
			last_date=Max('date'),
			total_in=Sum('quantity', filter=Q(movement_type='in')),
			total_out=Sum('quantity', filter=Q(movement_type='out')),
		)
	)


	for r in report_data:
		r['net_qty'] = (r['total_in'] or 0) - (r['total_out'] or 0)


	products = Product.objects.all()
	context = {'report_data': report_data, 'products': products, 'start_date': start_date, 'end_date': end_date}
	return render(request, 'inventory/product_movement_report.html', context)