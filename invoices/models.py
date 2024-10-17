from django.db import models

class Invoice(models.Model):
    invoice_file = models.FileField(upload_to='invoices/')
    extracted_data = models.JSONField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
