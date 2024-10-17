from django.urls import path
from .views import upload_invoice

urlpatterns = [
    path('', upload_invoice, name='upload_invoice'),  # URL for uploading invoices
]