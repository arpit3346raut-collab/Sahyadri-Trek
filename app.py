
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, make_response
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from flask_session import Session
import json
from pathlib import Path
from datetime import datetime
from bson.objectid import ObjectId
import bcrypt
from config import Config
from models import User, Trek, Booking, Admin
from database import Database
from utils import generate_qr_code, generate_booking_id, is_trek_available, format_currency
from fpdf import FPDF
import io
import base64

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
mail = Mail(app)
db = Database(app)


def initialize_treks():
    """Seed the local trek collection once when MongoDB has no trek data."""
    if db.mongo.db.treks.count_documents({}) > 0:
        return

    data_path = Path(__file__).with_name('treks_data.json')
    with data_path.open('r', encoding='utf-8') as data_file:
        treks = json.load(data_file)

    for trek in treks:
        trek.pop('id', None)
        trek.pop('available_slots', None)
        trek['is_active'] = True
        trek['created_at'] = datetime.utcnow()

    if treks:
        db.mongo.db.treks.insert_many(treks)


initialize_treks()

# Session configuration
app.config['SESSION_MONGODB'] = db.mongo
Session(app)

# Make get_trek_image available to all templates
@app.context_processor
def inject_image_helper():
    return dict(get_trek_image=get_trek_image)

# Load trek data from JSON (for initial setup)
def load_trek_data():
    try:
        with Path(__file__).with_name('treks_data.json').open('r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Image mapping for treks
def get_trek_image(trek_name):
    """Get the appropriate image file for a trek based on uploaded images"""
    # Mapping of trek names to image files
    image_mapping = {
        'Rajgad Fort': 'rajgad-fort.jpg',
        'Torna Fort': 'torna.jpg',
        'Sinhagad Fort': 'sinhagad.jpg',
        'Harishchandragad Fort': 'harishchandragad.jpeg',
        'Visapur Fort': 'visapur.jpg',
        'Lohagad Fort': 'lohagad.jpeg',
        'Mahuli Fort': 'mahuligad.jpeg',
        'Raigad Fort': 'raigad.jpg',
        'Korigad Fort': 'korigad.jpeg',
        'Pratapgad Fort': 'pratapgad.jpeg',
        'Harihar Fort': 'harihar.jpeg',
        'Purandar Fort': 'purandar.jpeg',
    }
    
    # Return the mapped image or fallback to placeholder
    return image_mapping.get(trek_name, 'fort-placeholder.jpg')

# Routes
@app.route('/')
def index():
    # Get popular treks (first 6)
    treks = db.get_all_treks()[:6]
    return render_template('index.html', treks=treks)

@app.route('/treks')
def treks():
    all_treks = db.get_all_treks()
    return render_template('treks.html', treks=all_treks)

@app.route('/trek/<trek_id>')
def trek_detail(trek_id):
    trek = db.get_trek_by_id(trek_id)
    if trek:
        return render_template('trek_detail.html', trek=trek)
    return "Trek not found", 404

@app.route('/book/<trek_id>')
def book_trek(trek_id):
    if 'user_id' not in session:
        flash('Please login to book a trek', 'warning')
        return redirect(url_for('user_login'))
    
    trek = db.get_trek_by_id(trek_id)
    if trek:
        return render_template('booking.html', trek=trek)
    return "Trek not found", 404

@app.route('/process_booking', methods=['POST'])
def process_booking():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login to book a trek'})
    
    try:
        trek_id = request.form.get('trek_id')
        trek_date = request.form.get('trek_date')
        time_slot = request.form.get('time_slot')
        num_trekkers = int(request.form.get('num_trekkers'))
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        
        # Get trek details
        trek = db.get_trek_by_id(trek_id)
        if not trek:
            return jsonify({'success': False, 'message': 'Trek not found'})
        
        # Check availability
        from datetime import datetime as dt
        if not is_trek_available(trek, dt.strptime(trek_date, '%Y-%m-%d').date(), time_slot, num_trekkers):
            return jsonify({'success': False, 'message': 'Selected trek is not available for booking'})
        
        # Calculate total amount (₹50 per trekker)
        total_amount = 50 * num_trekkers
        
        # Create booking
        booking = Booking(
            user_id=session['user_id'],
            trek_id=trek_id,
            trek_date=trek_date,
            time_slot=time_slot,
            num_trekkers=num_trekkers,
            name=name,
            mobile=mobile,
            email=email,
            total_amount=total_amount
        )
        
        # Save booking
        booking_id = db.create_booking(booking)
        
        # Update trek slots based on time slot
        db.update_trek_slots(trek_id, time_slot, -num_trekkers)
        
        # Generate QR code for trek pass
        booking_ref = generate_booking_id()
        qr_data = f"Trek Pass: {trek.name}\nDate: {trek_date}\nSlot: {time_slot}\nTrekkers: {num_trekkers}\nBooking ID: {booking_ref}"
        qr_code = generate_qr_code(qr_data)
        
        # Update booking with QR code and reference
        db.update_booking(booking_id, {
            'qr_code': qr_code,
            'booking_status': 'confirmed',
            'payment_status': 'completed',
            'booking_ref': booking_ref
        })
        
        # In a real application, send email with trek pass
        # send_trek_pass_email(email, trek, trek_date, time_slot, num_trekkers, qr_code)
        
        return jsonify({
            'success': True, 
            'message': 'Booking confirmed successfully!',
            'booking_id': booking_id,
            'booking_ref': booking_ref
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing booking: {str(e)}'})

@app.route('/booking-success')
def booking_success():
    # Get booking ID from query parameters
    booking_id = request.args.get('booking_id')
    
    if not booking_id:
        flash('Invalid booking reference', 'danger')
        return redirect(url_for('index'))
    
    # Get booking details
    booking = db.get_booking_by_id(booking_id)
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('index'))
    
    # Get trek details
    trek = db.get_trek_by_id(booking.trek_id)
    if not trek:
        flash('Trek information not found', 'danger')
        return redirect(url_for('index'))
    
    return render_template('booking_success.html', booking=booking, trek=trek)

@app.route('/login')
def combined_login():
    return render_template('combined_login.html')

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Get user from database
        user = db.get_user_by_email(email)
        if user and user.check_password(password):
            session['user_id'] = str(user.id) if hasattr(user, 'id') else str(user.email)
            session['user_name'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        # Basic validation
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if db.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User(name, email, mobile)
        user.set_password(password)
        
        # Save user
        user_id = db.create_user(user)
        
        # Auto-login the user after registration
        session['user_id'] = str(user_id)
        session['user_name'] = user.name
        
        flash('Registration successful! Welcome to Sahyadri Trekking Portal.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access your dashboard', 'warning')
        return redirect(url_for('login'))
    
    # Get user bookings
    user_bookings = db.get_bookings_by_user(session['user_id'])
    
    # Enhance bookings with trek details
    enhanced_bookings = []
    for booking in user_bookings:
        trek = db.get_trek_by_id(booking.trek_id)
        booking.trek_name = trek.name if trek else 'Unknown Trek'
        enhanced_bookings.append(booking)
    
    # Get user details
    user = db.get_user_by_id(session['user_id'])
    if not user:
        user = db.get_user_by_email(session['user_id'])
    
    return render_template('dashboard.html', bookings=enhanced_bookings, user=user)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to access your profile', 'warning')
        return redirect(url_for('login'))
    
    # Get user details
    user = db.get_user_by_id(session['user_id'])
    if not user:
        user = db.get_user_by_email(session['user_id'])
    
    return render_template('profile.html', user=user)

# Admin Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if it's the default admin (for demo purposes)
        if username == 'admin' and password == 'admin123':
            session['admin_id'] = 'admin'
            session['admin_username'] = 'admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # For production, check against database
        # admin = db.get_admin_by_username(username)
        # if admin and admin.check_password(password):
        #     session['admin_id'] = str(admin.id)
        #     session['admin_username'] = admin.username
        #     flash('Admin login successful!', 'success')
        #     return redirect(url_for('admin_dashboard'))
        # else:
        #     flash('Invalid admin credentials', 'danger')
        flash('Invalid admin credentials', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('admin_login'))

# Admin authentication decorator
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please login to access the admin panel', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Get statistics
    stats = db.get_trek_statistics()
    
    # Get recent bookings
    recent_bookings = list(db.mongo.db.bookings.find().sort('created_at', -1).limit(10))
    for booking in recent_bookings:
        # Add trek name to booking
        trek = db.get_trek_by_id(booking['trek_id'])
        booking['trek_name'] = trek.name if trek else 'Unknown Trek'
        
        # Add user name to booking
        user = db.get_user_by_id(booking['user_id'])
        booking['user_name'] = user.name if user else 'Unknown User'
    
    # Get all treks
    treks = db.get_all_treks()
    
    # Get all users
    users = list(db.mongo.db.users.find())
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent_bookings=recent_bookings, 
                         treks=treks, 
                         users=users)

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    # Get all bookings with related info
    bookings_cursor = db.mongo.db.bookings.find().sort('created_at', -1)
    bookings = []
    for booking_data in bookings_cursor:
        booking = Booking.from_dict(booking_data)
        # Add trek name
        trek = db.get_trek_by_id(booking.trek_id)
        booking.trek_name = trek.name if trek else 'Unknown Trek'
        # Add user name
        user = db.get_user_by_id(booking.user_id)
        booking.user_name = user.name if user else 'Unknown User'
        bookings.append(booking)
    
    return render_template('admin_bookings.html', bookings=bookings)

@app.route('/admin/bookings/<booking_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_booking(booking_id):
    booking = db.get_booking_by_id(booking_id)
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('admin_bookings'))
    
    if request.method == 'POST':
        # Update booking details
        update_data = {
            'trek_date': request.form.get('trek_date'),
            'time_slot': request.form.get('time_slot'),
            'num_trekkers': int(request.form.get('num_trekkers')),
            'name': request.form.get('name'),
            'mobile': request.form.get('mobile'),
            'email': request.form.get('email'),
            'booking_status': request.form.get('booking_status'),
            'payment_status': request.form.get('payment_status')
        }
        
        # Update booking
        if db.update_booking(booking_id, update_data):
            flash('Booking updated successfully!', 'success')
        else:
            flash('Failed to update booking', 'danger')
        
        return redirect(url_for('admin_bookings'))
    
    # Get trek for slot information
    trek = db.get_trek_by_id(booking.trek_id)
    
    return render_template('admin_edit_booking.html', booking=booking, trek=trek)

@app.route('/admin/bookings/<booking_id>/cancel', methods=['POST'])
@admin_required
def cancel_booking(booking_id):
    booking = db.get_booking_by_id(booking_id)
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('admin_bookings'))
    
    # Update booking status
    if db.update_booking(booking_id, {'booking_status': 'cancelled'}):
        # Restore slots
        db.update_trek_slots(booking.trek_id, booking.time_slot, booking.num_trekkers)
        flash('Booking cancelled successfully!', 'success')
    else:
        flash('Failed to cancel booking', 'danger')
    
    return redirect(url_for('admin_bookings'))

@app.route('/admin/treks')
@admin_required
def admin_treks():
    treks = db.get_all_treks()
    return render_template('admin_treks.html', treks=treks)

@app.route('/admin/treks/add', methods=['GET', 'POST'])
@admin_required
def add_trek():
    if request.method == 'POST':
        # Create new trek
        trek = Trek(
            name=request.form.get('name'),
            region=request.form.get('region'),
            difficulty=request.form.get('difficulty'),
            base_village=request.form.get('base_village'),
            contact=request.form.get('contact'),
            distance=request.form.get('distance'),
            trek_time=request.form.get('trek_time'),
            routes=request.form.get('routes'),
            history=request.form.get('history'),
            parking=request.form.get('parking'),
            rescue_number=request.form.get('rescue_number'),
            helpline=request.form.get('helpline'),
            forest_officer=request.form.get('forest_officer'),
            total_slots=int(request.form.get('total_slots', 400)),
            morning_slots=int(request.form.get('morning_slots', 200)),
            afternoon_slots=int(request.form.get('afternoon_slots', 200)),
            available_morning_slots=int(request.form.get('morning_slots', 200)),
            available_afternoon_slots=int(request.form.get('afternoon_slots', 200))
        )
        
        # Save trek
        trek_id = db.create_trek(trek)
        if trek_id:
            flash('Trek added successfully!', 'success')
            return redirect(url_for('admin_treks'))
        else:
            flash('Failed to add trek', 'danger')
    
    return render_template('admin_add_trek.html')

@app.route('/admin/treks/<trek_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_trek(trek_id):
    trek = db.get_trek_by_id(trek_id)
    if not trek:
        flash('Trek not found', 'danger')
        return redirect(url_for('admin_treks'))
    
    if request.method == 'POST':
        # Update trek details
        update_data = {
            'name': request.form.get('name'),
            'region': request.form.get('region'),
            'difficulty': request.form.get('difficulty'),
            'base_village': request.form.get('base_village'),
            'contact': request.form.get('contact'),
            'distance': request.form.get('distance'),
            'trek_time': request.form.get('trek_time'),
            'routes': request.form.get('routes'),
            'history': request.form.get('history'),
            'parking': request.form.get('parking'),
            'rescue_number': request.form.get('rescue_number'),
            'helpline': request.form.get('helpline'),
            'forest_officer': request.form.get('forest_officer'),
            'total_slots': int(request.form.get('total_slots', 400)),
            'morning_slots': int(request.form.get('morning_slots', 200)),
            'afternoon_slots': int(request.form.get('afternoon_slots', 200))
        }
        
        # Update trek
        if db.update_trek(trek_id, update_data):
            flash('Trek updated successfully!', 'success')
        else:
            flash('Failed to update trek', 'danger')
        
        return redirect(url_for('admin_treks'))
    
    return render_template('admin_edit_trek.html', trek=trek)

@app.route('/admin/treks/<trek_id>/delete', methods=['POST'])
@admin_required
def delete_trek(trek_id):
    if db.delete_trek(trek_id):
        flash('Trek deleted successfully!', 'success')
    else:
        flash('Failed to delete trek', 'danger')
    
    return redirect(url_for('admin_treks'))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = list(db.mongo.db.users.find())
    # Convert to User objects
    user_objects = [User.from_dict(user) for user in users]
    return render_template('admin_users.html', users=user_objects)

@app.route('/admin/slots')
@admin_required
def admin_slots():
    treks = db.get_all_treks()
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('admin_slots.html', treks=treks, today=today)

@app.route('/admin/slots/<trek_id>/update', methods=['POST'])
@admin_required
def update_slots(trek_id):
    trek = db.get_trek_by_id(trek_id)
    if not trek:
        flash('Trek not found', 'danger')
        return redirect(url_for('admin_slots'))
    
    morning_slots = int(request.form.get('morning_slots', trek.available_morning_slots))
    afternoon_slots = int(request.form.get('afternoon_slots', trek.available_afternoon_slots))
    
    # Update slots
    db.update_trek(trek_id, {
        'available_morning_slots': morning_slots,
        'available_afternoon_slots': afternoon_slots
    })
    
    flash('Slots updated successfully!', 'success')
    return redirect(url_for('admin_slots'))

@app.route('/safety')
def safety():
    return render_template('safety.html')

@app.route('/about')
def about():
    return render_template('about.html')

# API Routes for AJAX requests
@app.route('/api/treks')
def api_treks():
    treks = db.get_all_treks()
    treks_data = []
    for trek in treks:
        # Handle both old and new Trek model structures
        if hasattr(trek, 'available_morning_slots') and hasattr(trek, 'available_afternoon_slots'):
            # New structure with separate morning and afternoon slots
            morning_slots = trek.available_morning_slots
            afternoon_slots = trek.available_afternoon_slots
        else:
            # Old structure with single available_slots attribute
            morning_slots = getattr(trek, 'available_slots', 200)
            afternoon_slots = getattr(trek, 'available_slots', 200)
        
        treks_data.append({
            'id': str(trek.id) if hasattr(trek, 'id') else '',
            'name': trek.name,
            'region': trek.region,
            'difficulty': trek.difficulty,
            'base_village': trek.base_village,
            'available_morning_slots': morning_slots,
            'available_afternoon_slots': afternoon_slots
        })
    return jsonify(treks_data)

@app.route('/api/check_availability', methods=['POST'])
def check_availability():
    trek_id = request.form.get('trek_id')
    trek_date = request.form.get('trek_date')
    time_slot = request.form.get('time_slot')
    num_trekkers = int(request.form.get('num_trekkers'))
    
    trek = db.get_trek_by_id(trek_id)
    if trek:
        from datetime import datetime as dt
        available = is_trek_available(trek, dt.strptime(trek_date, '%Y-%m-%d').date(), time_slot, num_trekkers)
        return jsonify({'available': available})
    return jsonify({'available': False})

def generate_trekking_pass_pdf(booking, trek):
    """Generate a PDF trekking pass"""
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    
    pdf = FPDF()
    pdf.add_page()
    
    # Set title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "MAHARASHTRA GOVERNMENT - SAHYADRI TREKKING", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(5)
    
    # Add subtitle
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, "OFFICE OF THE FOREST DEPARTMENT", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(10)
    
    # Add trek pass title
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "TREKKING PASS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(15)
    
    # Add booking details
    pdf.set_font("Arial", "", 12)
    
    # Trek name
    pdf.cell(50, 10, "Trek Name:")
    pdf.cell(0, 10, trek.name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Booking date
    pdf.cell(50, 10, "Date:")
    pdf.cell(0, 10, booking.trek_date, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Time slot
    pdf.cell(50, 10, "Time Slot:")
    slot_text = "Morning (6:00 AM - 12:00 PM)" if booking.time_slot == 'morning' else "Afternoon (12:00 PM - 6:00 PM)"
    pdf.cell(0, 10, slot_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Number of trekkers
    pdf.cell(50, 10, "No. of Trekkers:")
    pdf.cell(0, 10, str(booking.num_trekkers), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Booking reference
    pdf.cell(50, 10, "Booking ID:")
    pdf.cell(0, 10, booking.booking_ref, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(10)
    
    # Trekker details
    pdf.cell(50, 10, "Trekker Name:")
    pdf.cell(0, 10, booking.name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.cell(50, 10, "Contact:")
    pdf.cell(0, 10, booking.mobile, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.cell(50, 10, "Email:")
    pdf.cell(0, 10, booking.email, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(10)
    
    # Amount (using Rs instead of ₹ for compatibility)
    pdf.cell(50, 10, "Amount Paid:")
    pdf.cell(0, 10, f"Rs. {booking.total_amount}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.ln(15)
    
    # QR Code placeholder text (since we can't easily embed the QR code in PDF)
    pdf.cell(0, 10, "QR Code for Entry Verification:", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(25)
    pdf.cell(0, 10, "[QR CODE PLACEHOLDER]", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(5)
    pdf.cell(0, 10, "Scan this QR code at the trek entrance", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.ln(15)
    
    # Important notes
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 10, "IMPORTANT NOTES:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("Arial", "", 8)
    pdf.cell(0, 5, "- This pass is non-transferable", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, "- Carry a printed copy of this pass during the trek", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, "- Reach the base location 30 minutes before the scheduled time", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, "- Follow all safety guidelines provided by forest officials", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Return PDF as bytes
    return pdf.output()

@app.route('/download-trek-pass/<booking_id>')
def download_trek_pass(booking_id):
    """Download trekking pass as PDF"""
    try:
        # Get booking details
        booking = db.get_booking_by_id(booking_id)
        if not booking:
            flash('Booking not found', 'danger')
            return redirect(url_for('index'))
        
        # Get trek details
        trek = db.get_trek_by_id(booking.trek_id)
        if not trek:
            flash('Trek information not found', 'danger')
            return redirect(url_for('index'))
        
        # Generate PDF
        pdf_bytes = generate_trekking_pass_pdf(booking, trek)
        
        # Create response
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=trek_pass_{booking.booking_ref}.pdf'
        
        return response
        
    except Exception as e:
        flash(f'Error generating trek pass: {str(e)}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)