from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from models import User, Trek, Booking, Admin

class Database:
    def __init__(self, app):
        self.mongo = PyMongo(app)
    
    # User operations
    def create_user(self, user):
        user_data = user.to_dict()
        result = self.mongo.db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user_by_email(self, email):
        user_data = self.mongo.db.users.find_one({'email': email})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_user_by_id(self, user_id):
        user_data = self.mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def update_user(self, user_id, update_data):
        result = self.mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    # Trek operations
    def create_trek(self, trek):
        trek_data = trek.to_dict()
        result = self.mongo.db.treks.insert_one(trek_data)
        return str(result.inserted_id)
    
    def get_all_treks(self):
        treks_cursor = self.mongo.db.treks.find({'is_active': True})
        treks = []
        for trek_data in treks_cursor:
            trek = Trek.from_dict(trek_data)
            treks.append(trek)
        return treks
    
    def get_trek_by_id(self, trek_id):
        trek_data = self.mongo.db.treks.find_one({'_id': ObjectId(trek_id)})
        if trek_data:
            return Trek.from_dict(trek_data)
        return None
    
    def update_trek(self, trek_id, update_data):
        result = self.mongo.db.treks.update_one(
            {'_id': ObjectId(trek_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_trek(self, trek_id):
        result = self.mongo.db.treks.update_one(
            {'_id': ObjectId(trek_id)},
            {'$set': {'is_active': False}}
        )
        return result.modified_count > 0
    
    # Booking operations
    def create_booking(self, booking):
        booking_data = booking.to_dict()
        result = self.mongo.db.bookings.insert_one(booking_data)
        return str(result.inserted_id)
    
    def get_booking_by_id(self, booking_id):
        booking_data = self.mongo.db.bookings.find_one({'_id': ObjectId(booking_id)})
        if booking_data:
            return Booking.from_dict(booking_data)
        return None
    
    def get_bookings_by_user(self, user_id):
        bookings_cursor = self.mongo.db.bookings.find({'user_id': user_id}).sort('created_at', -1)
        bookings = []
        for booking_data in bookings_cursor:
            booking = Booking.from_dict(booking_data)
            bookings.append(booking)
        return bookings
    
    def get_bookings_by_trek(self, trek_id):
        bookings_cursor = self.mongo.db.bookings.find({'trek_id': trek_id}).sort('created_at', -1)
        bookings = []
        for booking_data in bookings_cursor:
            booking = Booking.from_dict(booking_data)
            bookings.append(booking)
        return bookings
    
    def update_booking(self, booking_id, update_data):
        result = self.mongo.db.bookings.update_one(
            {'_id': ObjectId(booking_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def update_trek_slots(self, trek_id, time_slot, slots_change):
        """Update available slots for a trek (positive to add, negative to subtract)"""
        if time_slot == 'morning':
            field = 'available_morning_slots'
        elif time_slot == 'afternoon':
            field = 'available_afternoon_slots'
        else:
            # Fallback to old field for backward compatibility
            field = 'available_slots'
            
        result = self.mongo.db.treks.update_one(
            {'_id': ObjectId(trek_id)},
            {'$inc': {field: slots_change}}
        )
        return result.modified_count > 0
    
    # Admin operations
    def create_admin(self, admin):
        admin_data = admin.to_dict()
        result = self.mongo.db.admins.insert_one(admin_data)
        return str(result.inserted_id)
    
    def get_admin_by_username(self, username):
        admin_data = self.mongo.db.admins.find_one({'username': username})
        if admin_data:
            return Admin.from_dict(admin_data)
        return None
    
    def get_admin_by_id(self, admin_id):
        admin_data = self.mongo.db.admins.find_one({'_id': ObjectId(admin_id)})
        if admin_data:
            return Admin.from_dict(admin_data)
        return None
    
    # Statistics
    def get_trek_statistics(self):
        """Get statistics for admin dashboard"""
        total_treks = self.mongo.db.treks.count_documents({'is_active': True})
        total_bookings = self.mongo.db.bookings.count_documents({})
        active_bookings = self.mongo.db.bookings.count_documents({'booking_status': 'confirmed'})
        closed_treks = self.mongo.db.treks.count_documents({'is_active': False})
        
        # Calculate total revenue
        pipeline = [
            {'$match': {'payment_status': 'completed'}},
            {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
        ]
        revenue_result = list(self.mongo.db.bookings.aggregate(pipeline))
        total_revenue = revenue_result[0]['total'] if revenue_result else 0
        
        # Get bookings per trek
        pipeline = [
            {'$group': {'_id': '$trek_id', 'count': {'$sum': 1}}},
            {'$lookup': {
                'from': 'treks',
                'localField': '_id',
                'foreignField': '_id',
                'as': 'trek_info'
            }},
            {'$unwind': '$trek_info'},
            {'$project': {
                'trek_name': '$trek_info.name',
                'booking_count': '$count'
            }},
            {'$sort': {'booking_count': -1}},
            {'$limit': 5}
        ]
        popular_treks = list(self.mongo.db.bookings.aggregate(pipeline))
        
        return {
            'total_treks': total_treks,
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'closed_treks': closed_treks,
            'total_revenue': total_revenue,
            'popular_treks': popular_treks
        }