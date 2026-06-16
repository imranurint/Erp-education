from django.db import models
from apps.core.models import Branch, User


class Partner(models.Model):
    partner_id = models.AutoField(primary_key=True)
    partner_code = models.CharField(max_length=20, unique=True)
    partner_name = models.CharField(max_length=200)
    partner_type = models.CharField(max_length=20, default='Agent')
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, default='Bangladesh')
    website = models.CharField(max_length=255, blank=True, null=True)
    default_commission_type = models.CharField(max_length=40, default='Percentage of University Commission')
    default_commission_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    default_commission_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    payment_currency = models.CharField(max_length=3, default='BDT')
    payment_terms_days = models.IntegerField(default=30)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_name = models.CharField(max_length=150, blank=True, null=True)
    bank_account_no = models.CharField(max_length=50, blank=True, null=True)
    bank_branch = models.CharField(max_length=100, blank=True, null=True)
    bank_routing_no = models.CharField(max_length=30, blank=True, null=True)
    contract_start_date = models.DateField(blank=True, null=True)
    contract_end_date = models.DateField(blank=True, null=True)
    contract_document = models.CharField(max_length=500, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, default='Active')
    branch = models.ForeignKey(Branch, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='branch_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='created_by')

    class Meta:
        db_table = 'partners'
        ordering = ['partner_name']

    def __str__(self):
        return f"{self.partner_code} - {self.partner_name}"


class University(models.Model):
    university_id = models.AutoField(primary_key=True)
    university_name = models.CharField(max_length=300)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    ranking = models.CharField(max_length=50, blank=True, null=True)
    has_commission_agreement = models.BooleanField(default=False)
    commission_type = models.CharField(max_length=25, default='None')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    commission_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    commission_currency = models.CharField(max_length=3, default='GBP')
    commission_payment_terms = models.CharField(max_length=100, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.CharField(max_length=150, blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    admissions_portal_url = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=8, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'universities'
        ordering = ['university_name']

    def __str__(self):
        return f"{self.university_name}, {self.country}"
