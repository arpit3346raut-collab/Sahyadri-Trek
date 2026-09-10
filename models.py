from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, name, email, mobile, password_hash=None):
        self.name = name
        self.email = email
        self.mobile = mobile
        self.password_hash = password_hash
        self.created_at = datetime.utcnow()
        self.is_verified = False
        self.role = 'user'  # 'user' or 'admin'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'mobile': self.mobile,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'is_verified': self.is_verified,
            'role': self.role
        }
    
    @staticmethod
    def from_dict(data):
        user = User(
            name=data['name'],
            email=data['email'],
            mobile=data['mobile'],
            password_hash=data.get('password_hash')
        )
        user.created_at = data.get('created_at', datetime.utcnow())
        user.is_verified = data.get('is_verified', False)
        user.role = data.get('role', 'user')
        # Add id if it exists
        if '_id' in data:
            user.id = data['_id']
        return user

class Trek:
    def __init__(self, name, region, difficulty, base_village, contact, distance, 
                 trek_time, routes, history, parking, rescue_number, helpline, 
                 forest_officer, total_slots=400, morning_slots=200, afternoon_slots=200, 
                 available_morning_slots=200, available_afternoon_slots=200):
        self.name = name
        self.region = region
        self.difficulty = difficulty
        self.base_village = base_village
        self.contact = contact
        self.distance = distance
        self.trek_time = trek_time
        self.routes = routes
        self.history = history
        self.parking = parking
        self.rescue_number = rescue_number
        self.helpline = helpline
        self.forest_officer = forest_officer
        self.total_slots = total_slots  # Total slots (morning + afternoon)
        self.morning_slots = morning_slots  # Total morning slots
        self.afternoon_slots = afternoon_slots  # Total afternoon slots
        self.available_morning_slots = available_morning_slots  # Available morning slots
        self.available_afternoon_slots = available_afternoon_slots  # Available afternoon slots
        self.created_at = datetime.utcnow()
        self.is_active = True
    
    def to_dict(self):
        return {
            'name': self.name,
            'region': self.region,
            'difficulty': self.difficulty,
            'base_village': self.base_village,
            'contact': self.contact,
            'distance': self.distance,
            'trek_time': self.trek_time,
            'routes': self.routes,
            'history': self.history,
            'parking': self.parking,
            'rescue_number': self.rescue_number,
            'helpline': self.helpline,
            'forest_officer': self.forest_officer,
            'total_slots': self.total_slots,
            'morning_slots': self.morning_slots,
            'afternoon_slots': self.afternoon_slots,
            'available_morning_slots': self.available_morning_slots,
            'available_afternoon_slots': self.available_afternoon_slots,
            'created_at': self.created_at,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data):
        trek = Trek(
            name=data['name'],
            region=data['region'],
            difficulty=data['difficulty'],
            base_village=data['base_village'],
            contact=data['contact'],
            distance=data['distance'],
            trek_time=data['trek_time'],
            routes=data['routes'],
            history=data['history'],
            parking=data['parking'],
            rescue_number=data['rescue_number'],
            helpline=data['helpline'],
            forest_officer=data['forest_officer'],
            total_slots=data.get('total_slots', 400),
            morning_slots=data.get('morning_slots', 200),
            afternoon_slots=data.get('afternoon_slots', 200),
            available_morning_slots=data.get('available_morning_slots', 200),
            available_afternoon_slots=data.get('available_afternoon_slots', 200)
        )
        trek.created_at = data.get('created_at', datetime.utcnow())
        trek.is_active = data.get('is_active', True)
        # Add id if it exists
        if '_id' in data:
            trek.id = data['_id']
        return trek

class Booking:
    def __init__(self, user_id, trek_id, trek_date, time_slot, num_trekkers, 
                 name, mobile, email, total_amount=0):
        self.user_id = user_id
        self.trek_id = trek_id
        self.trek_date = trek_date
        self.time_slot = time_slot  # 'morning' or 'afternoon'
        self.num_trekkers = num_trekkers
        self.name = name
        self.mobile = mobile
        self.email = email
        self.total_amount = total_amount
        self.booking_status = 'pending'  # 'pending', 'confirmed', 'cancelled'
        self.payment_status = 'pending'  # 'pending', 'completed', 'failed', 'refunded'
        self.created_at = datetime.utcnow()
        self.qr_code = None  # Will store QR code path or data
        self.booking_ref = None  # Booking reference number
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'trek_id': self.trek_id,
            'trek_date': self.trek_date,
            'time_slot': self.time_slot,
            'num_trekkers': self.num_trekkers,
            'name': self.name,
            'mobile': self.mobile,
            'email': self.email,
            'total_amount': self.total_amount,
            'booking_status': self.booking_status,
            'payment_status': self.payment_status,
            'created_at': self.created_at,
            'qr_code': self.qr_code,
            'booking_ref': self.booking_ref
        }
    
    @staticmethod
    def from_dict(data):
        booking = Booking(
            user_id=data['user_id'],
            trek_id=data['trek_id'],
            trek_date=data['trek_date'],
            time_slot=data['time_slot'],
            num_trekkers=data['num_trekkers'],
            name=data['name'],
            mobile=data['mobile'],
            email=data['email'],
            total_amount=data.get('total_amount', 0)
        )
        booking.booking_status = data.get('booking_status', 'pending')
        booking.payment_status = data.get('payment_status', 'pending')
        booking.created_at = data.get('created_at', datetime.utcnow())
        booking.qr_code = data.get('qr_code')
        booking.booking_ref = data.get('booking_ref')
        # Add id if it exists
        if '_id' in data:
            booking.id = data['_id']
        return booking

class Admin:
    def __init__(self, username, email, password_hash=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.utcnow()
        self.is_active = True
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'is_active': self.is_active
        }
    
    @staticmethod
    def from_dict(data):
        admin = Admin(
            username=data['username'],
            email=data['email'],
            password_hash=data.get('password_hash')
        )
        admin.created_at = data.get('created_at', datetime.utcnow())
        admin.is_active = data.get('is_active', True)
        # Add id if it exists
        if '_id' in data:
            admin.id = data['_id']
        return admin