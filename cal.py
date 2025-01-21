import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import io
from datetime import datetime
from typing import Dict, List
import logging
from decimal import Decimal

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_CURRENCY = "INR"
DEFAULT_GST_RATE = 18.0
MIN_QUANTITY = 1
MAX_QUANTITY = 1000

# Function to generate invoice
def generate_invoice(company_info, client_info, items, invoice_number, gst_rate=None, additional_tax_rate=0.0, invoice_currency=None):
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
    currency = invoice_currency if invoice_currency else selected_currency
    symbol = currency_symbols[currency]
    rate = currency_rates[currency]
    
    table_data = [['Description', 'Quantity', f'Unit Price({currency})', f'Amount({currency})']]
    subtotal = Decimal('0')

    for item in items:
        # Convert all numbers to Decimal
        unit_price_decimal = Decimal(str(item['unit_price']))
        quantity_decimal = Decimal(str(item['quantity']))
        unit_price_converted = unit_price_decimal * rate
        amount = quantity_decimal * unit_price_converted
        subtotal += amount
        table_data.append([
            item['description'],
            str(quantity_decimal),
            str(f"{symbol}{unit_price_converted:,.2f}"),
            str(f"{symbol}{amount:,.2f}")
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

    # Calculate total using Decimal
    total_with_taxes = subtotal  # Start with subtotal
    
    # Add Subtotal, GST, and Total as a separate section
    elements.append(Spacer(1, 20))
    summary_data = [
        ['Subtotal:', f"{symbol}{subtotal:,.2f}"]
    ]
    
    # Only add GST if gst_rate is provided
    if gst_rate is not None:
        gst_rate_decimal = Decimal(str(gst_rate))
        gst_amount = subtotal * (gst_rate_decimal / Decimal('100'))
        total_with_taxes += gst_amount
        summary_data.append([f'GST ({gst_rate}%):', f"{symbol}{gst_amount:,.2f}"])

    # Add additional tax if provided
    if additional_tax_rate > 0:
        additional_tax_rate_decimal = Decimal(str(additional_tax_rate))
        additional_tax = subtotal * (additional_tax_rate_decimal / Decimal('100'))
        total_with_taxes += additional_tax
        summary_data.append([f'Tax ({additional_tax_rate}%):', f"{symbol}{additional_tax:,.2f}"])
    
    summary_data.append([f'Total({currency}):', f"{symbol}{total_with_taxes:,.2f}"])
    
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

# Helper functions
def safe_decimal_conversion(value: float) -> Decimal:
    """Safely convert float to Decimal for precise calculations."""
    try:
        return Decimal(str(value))
    except (ValueError, TypeError) as e:
        logger.error(f"Error converting value to Decimal: {e}")
        return Decimal('0')

def initialize_session_state():
    """Initialize or reset session state variables."""
    if 'selected_services' not in st.session_state:
        st.session_state.selected_services = []
    if 'quantities' not in st.session_state:
        st.session_state.quantities = {}
    if 'current_currency' not in st.session_state:
        st.session_state.current_currency = DEFAULT_CURRENCY

def format_amount(amount_inr: float, target_currency: str) -> str:
    """Safely format and convert currency amounts."""
    try:
        if target_currency not in currency_rates:
            logger.error(f"Invalid currency: {target_currency}")
            return "Invalid Currency"
        
        amount_decimal = safe_decimal_conversion(amount_inr)
        rate = currency_rates[target_currency]
        converted_amount = amount_decimal * rate
        
        return f"{currency_symbols[target_currency]}{converted_amount:,.2f}"
    except Exception as e:
        logger.error(f"Error formatting amount: {e}")
        return "Error"

def calculate_total_cost(services_dict: Dict, selected_services: List[str], 
                        quantities: Dict[str, int], profit_margin: float) -> float:
    """Calculate total cost with error handling."""
    try:
        total = 0
        for service in selected_services:
            if service not in services_dict:
                logger.warning(f"Invalid service selected: {service}")
                continue
                
            base_cost = services_dict[service]
            quantity = quantities.get(service, 1)
            
            if not isinstance(quantity, (int, float)) or quantity < 1:
                logger.warning(f"Invalid quantity for service {service}: {quantity}")
                continue
                
            margin_multiplier = 1 + (profit_margin / 100)
            service_total = base_cost * quantity * margin_multiplier
            total += service_total
            
        return total
    except Exception as e:
        logger.error(f"Error calculating total cost: {e}")
        return 0

def validate_client_info(name: str, address: str, email: str) -> tuple[bool, str]:
    """Validate client information."""
    if not name or not name.strip():
        return False, "Client name is required"
    if not address or not address.strip():
        return False, "Client address is required"
    if not email or '@' not in email:
        return False, "Valid email address is required"
    return True, ""

# Streamlit App Title
st.title("Quotation Calculator for iCoast")

# Initialize session state
initialize_session_state()

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

# Currency conversion rates - Move to a separate configuration file in production
currency_rates = {
    "INR": Decimal('1.0'),
    "USD": Decimal('0.011561052'),
    "CAD": Decimal('0.0166942')
}

currency_symbols = {
    "INR": "Rs.",
    "USD": "$",
    "CAD": "CAD"
}

# Profit margin and currency selection with validation
with st.form("margin_settings"):
    col1, col2 = st.columns(2)
    with col1:
        profit_margin_sun = st.number_input(
            "SUN E-Learning Profit Margin (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=10.0
        )
    with col2:
        selected_currency = st.selectbox(
            "Select Currency",
            options=list(currency_rates.keys()),
            index=list(currency_rates.keys()).index(st.session_state.current_currency)
        )
    
    if st.form_submit_button("Update"):
        st.session_state.current_currency = selected_currency
        st.success("Settings updated successfully!")

# Multi-select for services and quantities
st.header("Select Services")

# Create columns for the header
header_col1, header_col2, header_col3 = st.columns([3, 1, 1])
with header_col1:
    st.write("**Service Name**")
with header_col2:
    st.write("**Quantity**")
with header_col3:
    st.write("**Price**")

# Container for services
for service in services:
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        selected = st.checkbox(service, key=f"select_{service}")
        if selected and service not in st.session_state.selected_services:
            st.session_state.selected_services.append(service)
        elif not selected and service in st.session_state.selected_services:
            st.session_state.selected_services.remove(service)
    
    with col2:
        if selected:
            quantity = st.number_input(
                "Quantity",
                min_value=MIN_QUANTITY,
                max_value=MAX_QUANTITY,
                value=st.session_state.quantities.get(service, MIN_QUANTITY),
                key=f"qty_{service}",
                label_visibility="collapsed"
            )
            st.session_state.quantities[service] = quantity
        else:
            st.write("")  # Empty space for alignment
    
    with col3:
        if selected:
            base_cost = services[service]
            unit_price = base_cost * (1 + profit_margin_sun/100)
            service_total = unit_price * st.session_state.quantities.get(service, MIN_QUANTITY)
            st.write(format_amount(service_total, selected_currency))
        else:
            st.write("")  # Empty space for alignment

# Calculate total cost and prepare selected items
total_cost = 0  # Initialize to 0
selected_items = []

for service in st.session_state.selected_services:
    base_cost = services[service]
    unit_price = base_cost * (1 + profit_margin_sun/100)
    quantity = st.session_state.quantities.get(service, MIN_QUANTITY)
    service_total = unit_price * quantity
    total_cost += service_total  # Add to total
    selected_items.append({
        'description': service,
        'quantity': quantity,
        'unit_price': unit_price
    })

if st.session_state.selected_services:
    st.header("Total Cost")
    st.write(format_amount(total_cost, selected_currency))
    
    # Display GST and Final Amount
    gst_amount = total_cost * 0.18
    total_with_gst = total_cost + gst_amount
    st.write(f"GST (18%): {format_amount(gst_amount, selected_currency)}")
    st.write(f"Total Amount (including GST): {format_amount(total_with_gst, selected_currency)}")

    # Add a separator
    st.markdown("---")

    # Quick Invoice Generation for SunElearning
    quick_invoice_col1, quick_invoice_col2 = st.columns([3, 1])
    with quick_invoice_col1:
        st.write("Generate SunElearning invoice with default company details")
    with quick_invoice_col2:
        if st.button("Generate SunElearning Invoice"):
            company_info = {
                'name': 'Sun E-Learning',
                'address': '123 Business Park, Tech City, State - 578962',
                'phone': '+91 98765 43210',
                'email': 'billing@sunelearning.com'
            }
            
            client_info = {
                'name': 'iCoast Digital Solutions',
                'address': '123 Business Park, Tech City, State - 578962',
                'email': 'billing@icoast.com'
            }
            
            # Generate SunElearning invoice WITH GST
            pdf_file = generate_invoice(
                company_info,
                client_info,
                selected_items,
                f'INV-{datetime.now().strftime("%Y%m%d")}-{len(st.session_state.selected_services):03d}',
                gst_rate=18.0,  # Include GST for SunElearning invoice
                additional_tax_rate=0.0,
                invoice_currency=selected_currency
            )
            
            st.download_button(
                "Download SunElearning Invoice",
                pdf_file,
                file_name=f"sunelearning_invoice_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

    # Add a separator
    st.markdown("---")

    # iCoast Reselling Calculator
    st.header("iCoast Reselling Calculator")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        icoast_profit_margin = st.number_input(
            "Profit Margin (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=0.0, 
            step=5.0
        )
    # with col2:
    #     icoast_gst_rate = st.number_input(
    #         "GST Rate (%)",
    #         min_value=0.0,
    #         max_value=100.0,
    #         value=18.0,
    #         step=0.1
    #     )
    with col3:
        icoast_additional_tax = st.number_input(
            "Tax (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1
        )
    with col4:
        icoast_currency = st.selectbox(
            "Select Currency",
            options=["INR", "USD", "CAD"],
            key="icoast_currency"
        )

    # Calculate iCoast's costs
    icoast_base_cost = total_cost  # Base cost from SunElearning (before GST)
    icoast_selling_price = icoast_base_cost * (1 + icoast_profit_margin/100)
    # icoast_gst = icoast_selling_price * (icoast_gst_rate/100)
    icoast_add_tax = icoast_selling_price * (icoast_additional_tax/100)
    icoast_final_price = icoast_selling_price + icoast_add_tax

    # Display iCoast's pricing breakdown
    st.subheader("iCoast Pricing Breakdown")
    st.write(f"Base Cost from SunElearning (before GST): {format_amount(icoast_base_cost, icoast_currency)}")
    st.write(f"iCoast Selling Price (with {icoast_profit_margin}% margin): {format_amount(icoast_selling_price, icoast_currency)}")
    # st.write(f"GST ({icoast_gst_rate}%): {format_amount(icoast_gst, icoast_currency)}")
    if icoast_additional_tax > 0:
        st.write(f"Tax ({icoast_additional_tax}%): {format_amount(icoast_add_tax, icoast_currency)}")
    st.write(f"Final Price to Client: {format_amount(icoast_final_price, icoast_currency)}")

    st.markdown("---")

    # iCoast Client Invoice Generation
    st.subheader("Generate Invoice for iCoast Client")
    client_name = st.text_input("Client Name")
    client_address = st.text_area("Client Address")
    client_email = st.text_input("Client Email")

    if st.button("Generate Client Invoice"):
        if not client_name or not client_address or not client_email:
            st.error("Please fill in all client information before generating the invoice.")
        else:
            # Prepare items with iCoast's margin
            icoast_items = []
            for item in selected_items:
                item_with_margin = item.copy()
                item_with_margin['unit_price'] = item['unit_price'] * (1 + icoast_profit_margin/100)
                icoast_items.append(item_with_margin)

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
            
            # Generate iCoast invoice WITHOUT GST
            pdf_file = generate_invoice(
                company_info,
                client_info,
                icoast_items,
                f'ICOAST-INV-{datetime.now().strftime("%Y%m%d")}-{len(st.session_state.selected_services):03d}',
                gst_rate=None,  # No GST for iCoast invoice
                additional_tax_rate=icoast_additional_tax,
                invoice_currency=icoast_currency
            )
            
            st.download_button(
                "Download Client Invoice",
                pdf_file,
                file_name=f"icoast_client_invoice_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
else:
    st.info("Please select at least one service to proceed.")
