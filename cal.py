
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import io
from datetime import datetime

# Streamlit App Title
st.title("Quotation Calculator for iCoast")

# Initialize session state
if 'selected_services' not in st.session_state:
    st.session_state.selected_services = []
if 'quantities' not in st.session_state:
    st.session_state.quantities = {}

# Services Dictionary with Base Manufacturing Costs
services = {
    "Advertising Campaigns - PPC (Pay per Click)": 3000,
    "Advertising Campaigns - Google Ads": 5000,
    "Advertising Campaigns - Display Advertising": 4000,
    "Social Media Mastery - Content Creation": 2500,
    "SEO Expertise - SEO On-Page (1 keyword)": 1500,
    "AI Marketing Tools - Custom Chatbots": 25000,
    "Content Marketing - Blog Post": 300,
    "Creatives & Video Production - Basic Creatives": 500,
    "Creatives & Video Production - Logo Designing": 1000,
    "Creatives & Video Production - Basic Videos": 1500,
}

# Profit Margins
st.header("Set Profit Margins")
col1, col2 = st.columns(2)
with col1:
    profit_margin_sun = st.number_input("SUN E-Learning Profit Margin (%)", 
                                      min_value=0.0, max_value=100.0, value=0.0, step=10.0)
with col2:
    profit_margin_iCoast = st.number_input("iCoast Profit Margin (%)", 
                                         min_value=0.0, max_value=100.0, value=0.0, step=10.0)

# Multi-select for services
st.header("Select Services")
selected_services = st.multiselect(
    "Choose Multiple Services",
    options=list(services.keys()),
    default=st.session_state.selected_services
)

# Update session state
st.session_state.selected_services = selected_services

# Container for service quantities and costs
services_container = st.container()

total_cost = 0
selected_items = []

with services_container:
    if selected_services:
        st.subheader("Service Details")
        for service in selected_services:
            base_cost = services[service]
            # Calculate final unit price including both profit margins
            unit_price = base_cost * (1 + (profit_margin_sun + profit_margin_iCoast)/100)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(service)
            
            with col2:
                quantity = st.number_input(
                    f"Quantity",
                    min_value=1,
                    value=st.session_state.quantities.get(service, 1),
                    key=f"qty_{service}"
                )
                st.session_state.quantities[service] = quantity
            
            with col3:
                service_total = unit_price * quantity
                st.write(f"₹{service_total:,.2f}")
                total_cost += service_total
                selected_items.append({
                    'description': service,
                    'quantity': quantity,
                    'unit_price': unit_price
                })

if selected_services:
    st.header("Total Cost")
    st.write(f"₹{total_cost:,.2f}")

    # Client Information Form
    st.header("Client Information")
    client_name = st.text_input("Client Name")
    client_address = st.text_area("Client Address")
    client_email = st.text_input("Client Email")

    def generate_invoice(company_info, client_info, items, invoice_number):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch / 2,
            leftMargin=inch / 2,
            topMargin=inch / 2,
            bottomMargin=inch / 2
        )

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='CenterAlign',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=12,
            spaceAfter=30
        ))
        styles.add(ParagraphStyle(
            name='CompanyName',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER
        ))

        elements = []

        # Company header
        elements.append(Paragraph(company_info['name'], styles['CompanyName']))
        elements.append(Paragraph(company_info['address'], styles['CenterAlign']))
        elements.append(Paragraph(f"Phone: {company_info['phone']} | Email: {company_info['email']}", styles['CenterAlign']))

        # Invoice info
        elements.append(Spacer(1, 20))
        invoice_info = [
            ['Invoice Number:', invoice_number],
            ['Date:', datetime.now().strftime('%B %d, %Y')],
            ['Due Date:', (datetime.now()).strftime('%B %d, %Y')]
        ]
        invoice_table = Table(invoice_info, colWidths=[2 * inch, 4 * inch])
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 20))

        # Bill to section
        elements.append(Paragraph('Bill To:', styles['Heading2']))
        elements.append(Paragraph(client_info['name'], styles['Normal']))
        elements.append(Paragraph(client_info['address'], styles['Normal']))
        elements.append(Paragraph(f"Email: {client_info['email']}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Items table
        table_data = [['Description', 'Quantity', 'Unit Price(INR)', 'Amount(INR)']]
        subtotal = 0

        for item in items:
            amount = item['quantity'] * item['unit_price']
            subtotal += amount
            table_data.append([
                item['description'],
                str(item['quantity']),
                str(f"{item['unit_price']:,.2f}"),
                str(f"{amount:,.2f}")
            ])

        # Create the table for items
        items_table = Table(table_data, colWidths=[4 * inch, 1 * inch, 1.25 * inch, 1.25 * inch])
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            # Data
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(items_table)

        # Calculate GST and total
        gst_amount = subtotal * 0.18
        total_with_gst = subtotal + gst_amount

        # Add Subtotal, GST, and Total as a separate section
        elements.append(Spacer(1, 20))
        summary_data = [
            ['Subtotal:', f"{subtotal:,.2f}"],
            ['GST (18%):', f"{gst_amount:,.2f}"],
            ['Total(INR):', f"{total_with_gst:,.2f}"]
        ]
        summary_table = Table(summary_data, colWidths=[6 * inch, 2 * inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
        ]))
        elements.append(summary_table)

        # Terms and conditions
        elements.append(Spacer(1, 30))
        elements.append(Paragraph('Terms and Conditions:', styles['Heading3']))
        terms = [
            "1. Payment is due within 30 days",
            "2. Please include invoice number on your payment",
            "3. Make all checks payable to the company name above",
            "4. Bank transfer details will be provided upon request"
        ]
        for term in terms:
            elements.append(Paragraph(term, styles['Normal']))

        doc.build(elements)
        buffer.seek(0)
        return buffer


    # Generate Invoice Button
    if st.button("Generate Invoice"):
        if not client_name or not client_address or not client_email:
            st.error("Please fill in all client information before generating the invoice.")
        else:
            company_info = {
                'name': 'iCoast Digital Solutions',
                'address': '123 Business Park, Tech City, State - 578962',
                'phone': '+91 98765 43210',
                'email': 'billing@icoast.com'
            }
            
            client_info = {
                'name': client_name,
                'address': client_address,
                'email': client_email
            }
            
            # Generate PDF
            pdf_file = generate_invoice(
                company_info,
                client_info,
                selected_items,
                f'INV-{datetime.now().strftime("%Y%m%d")}-{len(selected_services):03d}'
            )
            
            # Download button for the generated PDF
            st.download_button(
                "Download Invoice",
                pdf_file,
                file_name=f"icoast_invoice_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
else:
    st.info("Please select at least one service to proceed.")
