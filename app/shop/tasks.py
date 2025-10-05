from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Order, Report
from django.db.models import F, Sum

@shared_task
def generate_sales_reports():
    """Создаёт дневной, недельный и месячный отчёты по заказам"""
    now = timezone.now()
    periods = {
        "daily": now - timedelta(days=1),
        "weekly": now - timedelta(weeks=1),
        "monthly": now - timedelta(days=30),
    }

    for report_type, start_date in periods.items():
        orders = Order.objects.filter(created_at__gte=start_date)

        total_orders = orders.count()
        total_revenue = orders.aggregate(total=Sum(F("product__price") * F("quantity")))["total"] or 0

        Report.objects.create(
            report_type=report_type,
            total_orders=total_orders,
            total_revenue=total_revenue,
        )
