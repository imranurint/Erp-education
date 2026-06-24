from celery import shared_task
from datetime import date
from decimal import Decimal


@shared_task
def calculate_monthly_depreciation():
    """
    Run on 1st of each month (add to CELERY_BEAT_SCHEDULE).
    Calculates depreciation for all active assets.
    """
    from apps.core.models import Asset, AssetDepreciation, AssetCategory
    from apps.notifications.models import ScheduledTaskLog
    from django.utils import timezone
    import calendar

    log = ScheduledTaskLog.objects.create(
        task_name='calculate_monthly_depreciation',
        started_at=timezone.now(),
    )

    try:
        today = date.today()
        month_label = f"{calendar.month_name[today.month]} {today.year}"
        count = 0

        active_assets = Asset.objects.filter(
            status='Active',
            depreciation_method='Straight Line',
        ).select_related('category')

        for asset in active_assets:
            # Skip if already calculated this period
            if AssetDepreciation.objects.filter(
                asset=asset, period_label=month_label
            ).exists():
                continue

            opening = float(asset.current_value)
            salvage = float(asset.salvage_value)
            useful_months = (asset.category.useful_life_years or 5) * 12
            total_purchase = float(asset.purchase_price)

            if opening <= salvage:
                continue

            # Monthly depreciation
            monthly_dep = (total_purchase - salvage) / useful_months
            monthly_dep = min(monthly_dep, opening - salvage)

            if monthly_dep <= 0:
                continue

            closing = opening - monthly_dep
            acc_total = float(asset.accumulated_depreciation) + monthly_dep

            AssetDepreciation.objects.create(
                asset=asset,
                depreciation_date=today,
                period_label=month_label,
                opening_value=round(opening, 2),
                depreciation_amount=round(monthly_dep, 2),
                closing_value=round(closing, 2),
                accumulated_total=round(acc_total, 2),
                status='Calculated',
                branch=asset.branch,
            )

            # Update asset
            asset.current_value = round(closing, 2)
            asset.accumulated_depreciation = round(acc_total, 2)
            asset.save(update_fields=[
                'current_value', 'accumulated_depreciation', 'updated_at'
            ])

            count += 1

        log.status = 'Completed'
        log.finished_at = timezone.now()
        log.records_affected = count
        log.result_summary = f'Depreciation calculated for {count} assets'
        log.save()

        return f'Depreciation: {count} assets processed'

    except Exception as e:
        log.status = 'Failed'
        log.error_message = str(e)[:500]
        log.finished_at = timezone.now()
        log.save()
        raise