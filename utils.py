import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from datetime import datetime, timedelta
import secrets
import string
from flask import url_for

def generate_qr_code(data):
    """Generate QR code for trek pass"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO object
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to base64 for embedding in HTML
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

def generate_booking_id():
    """Generate unique booking ID"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_string = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"TRK{timestamp}{random_string}"

def generate_otp():
    """Generate 6-digit OTP"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def is_trek_available(trek, booking_date, time_slot, num_trekkers):
    """Check if trek is available for booking"""
    # Check if trek is active
    if not trek.is_active:
        return False
    
    # For now, we'll assume each date has full slot availability
    # This is a temporary fix until we implement date-specific slot management
    available_slots = 200  # Default to maximum slots per date
    
    if available_slots < num_trekkers:
        return False
    
    # Check if date is in the future
    if booking_date < datetime.now().date():
        return False
    
    # Check if date is within booking window (e.g., 60 days in advance)
    max_booking_date = datetime.now().date() + timedelta(days=60)
    if booking_date > max_booking_date:
        return False
    
    return True

def format_currency(amount):
    """Format amount as Indian Rupees"""
    return f"₹{amount:,.2f}"

def get_difficulty_badge_class(difficulty):
    """Get Bootstrap badge class for difficulty level"""
    if difficulty.lower() == 'easy':
        return 'bg-success'
    elif difficulty.lower() == 'medium':
        return 'bg-warning'
    elif difficulty.lower() == 'hard':
        return 'bg-danger'
    else:
        return 'bg-secondary'

def get_region_badge_class(region):
    """Get Bootstrap badge class for region"""
    region_colors = {
        'pune': 'bg-primary',
        'satara': 'bg-info',
        'nashik': 'bg-success',
        'raigad': 'bg-warning'
    }
    return region_colors.get(region.lower(), 'bg-secondary')

def send_email(to_email, subject, body):
    """Mock function to send email (to be implemented with actual email service)"""
    # In a real implementation, this would use Flask-Mail or similar
    print(f"Sending email to {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    return True

def validate_mobile_number(mobile):
    """Validate Indian mobile number format"""
    # Simple validation for 10-digit Indian mobile numbers
    if len(mobile) == 10 and mobile.isdigit() and mobile[0] in '6789':
        return True
    return False

def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None