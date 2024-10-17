from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .models import Invoice
import re
import pdfplumber

# Function to extract required data from the PDF
def extract_invoice_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() or ''  # Handle None return value

    # Updated regex patterns
    invoice_data = {
        'invoice_number': re.search(r'Invoice No\.?\s*[:\-]?\s*([\w\d-]+)', text),
        'invoice_date': re.search(r'Invoice Date[-\s]*([\d]{1,2}-[A-Za-z]+-[\d]{4})', text),
        'bill_from_gst': re.search(r'Invoice Date[-\s]*([\d]{1,2}-[A-Za-z]+-[\d]{4})', text),  # Capture "From GSTIN No"
        'bill_to_gst': re.search(r'Due Date[-\s]*([\d]{1,2}-[A-Za-z]+-[\d]{4})', text),
        'billing_period': re.search(r'Billing Period from\s*([0-9]{2}-[A-Za-z]+-[0-9]{4}) to\s*([0-9]{2}-[A-Za-z]+-[0-9]{4})', text),
        'amount': re.search(r'Total[:\s]*([\d,]+.\d{2})', text),
    }

    # Clean up the results
    cleaned_data = {}
    for key in invoice_data:  # Iterate over the original keys
        value = invoice_data[key]
        if value:
            if key == 'billing_period':
                cleaned_data['period_from'] = value.group(1)
                cleaned_data['period_to'] = value.group(2)
            else:
                cleaned_data[key] = value.group(1)
        else:
            cleaned_data[key] = None

    return cleaned_data

def upload_invoice(request):
    if request.method == 'POST' and request.FILES['invoice_file']:
        # Get the uploaded PDF file
        uploaded_file = request.FILES['invoice_file']

        # Save the file temporarily to the server
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        # Save the file path to the database
        invoice = Invoice(invoice_file=filename)
        invoice.save()

        # Extract invoice data from the uploaded PDF file
        invoice_data = extract_invoice_data(file_path)
        invoice.extracted_data = invoice_data
        invoice.save()
        print("hhhhhhhhhhh")

        return render(request, 'success.html', {'invoice_data': invoice_data})

    return render(request, 'upload.html')
