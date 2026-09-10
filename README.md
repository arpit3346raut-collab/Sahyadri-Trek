# Maharashtra Government – Sahyadri Trekking Crowd Management Portal

## Project Overview

This is a web portal for managing crowd and online slot booking for Sahyadri treks in Maharashtra. The portal provides a clean, government-style interface for trekkers to explore, book, and manage trekking slots while ensuring safety through weather monitoring and crowd control.

## Folder Structure

```
sahyadri_trek/
│
├── templates/                 # HTML templates
│   ├── base.html              # Base template with header/footer
│   ├── index.html             # Landing page
│   ├── treks.html             # Treks listing page
│   ├── trek_detail.html       # Trek detail page
│   ├── booking.html           # Trek booking page
│   ├── booking_success.html   # Booking confirmation page
│   ├── login.html             # User login page
│   ├── register.html          # User registration page
│   ├── dashboard.html         # User dashboard
│   ├── admin_login.html       # Admin login page
│   ├── admin_dashboard.html   # Admin dashboard
│   └── safety.html            # Safety guidelines page
│
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css          # Custom CSS styles
│   ├── js/
│   │   └── script.js          # Custom JavaScript
│   └── images/                # Image assets
│       ├── placeholder.html    # Visual guide for image placement
│       ├── README.md           # Image requirements and guidelines
│       └── ...                 # Actual trek images (to be added)
│
├── models.py                  # Data models for User, Trek, Booking, Admin
├── database.py                # Database operations using PyMongo
├── config.py                  # Application configuration
├── utils.py                   # Utility functions
├── app.py                     # Main Flask application
├── init_db.py                 # Database initialization script
├── treks_data.json            # Sample trek data
├── generate_placeholders.py   # Script to generate placeholder images
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation
```

## Pages & Features

### 1. Landing Page (index.html)
- Government-style header with logo
- Hero section with Rajgad Fort background
- Popular treks grid (6 featured treks)
- Smooth scroll to treks section
- Features section highlighting key benefits

### 2. Treks Page (treks.html)
- Search functionality
- Filter by difficulty (Easy/Medium/Hard)
- Filter by region (Pune/Satara/Nashik/Raigad)
- Responsive grid of trek cards (30+ treks)

### 3. Trek Detail Page (trek_detail.html)
- Comprehensive trek information
- Image carousel
- Difficulty level and trail details
- Historical information
- Emergency contacts
- Real-time weather forecast
- Slot booking button

### 4. Booking Page (booking.html)
- Multi-step booking form:
  1. Date and slot selection
  2. Number of trekkers
  3. Personal information
  4. Payment processing
- Progress indicator
- Booking summary

### 5. User Authentication & Dashboard
- Registration page with form validation
- Login page with authentication
- User dashboard with upcoming/past treks
- Profile management
- Proper flow: Register → Login → Dashboard → Booking

### 6. Admin Panel
- Secure admin login
- Trek management (CRUD operations)
- Booking statistics
- Slot availability monitoring
- Safety alert system

### 7. Safety Guidelines (safety.html)
- Pre-trek checklist
- During trek safety measures
- Weather safety guidelines
- Emergency contacts
- SOS information

## Technology Stack

### Frontend
- **HTML5, CSS3, JavaScript**
- **Bootstrap 5** for responsive design
- **Custom CSS** for Maharashtra-themed styling

### Backend
- **Python Flask** as the web framework
- **MongoDB** for data storage
- **PyMongo** for database operations
- **Flask-Mail** for email notifications
- **Flask-Session** for session management
- **bcrypt** for password hashing
- **qrcode** for generating QR codes

## Color Scheme

- Maharashtra Green: #228B22
- Dark Green: #006400
- Brown: #8B4513
- Light Brown: #D2B48C
- Sky Blue: #87CEEB

## Image Placeholders

The portal includes a comprehensive placeholder system for all required images:

1. **Logo**: `maharashtra-logo.png` (800x200)
2. **Hero Image**: `rajgad-fort.jpg` (1920x1080)
3. **Trek Images**: 14+ images (800x600 each)

### Using Placeholders

All images include automatic fallback to SVG placeholders if the actual image files are missing. This ensures the site works even without images.

### Replacing Placeholders

To replace placeholders with actual images:

1. View `static/images/placeholder.html` for a visual guide
2. Follow the guidelines in `static/images/README.md`
3. Use the image replacement guide in `static/images/image_replacement_guide.md`
4. Optionally run `generate_placeholders.py` to create basic placeholder images

### Generating Basic Placeholders

Run the placeholder generation script:
```bash
python generate_placeholders.py
```

This requires the Pillow library:
```bash
pip install Pillow
```

## Database Setup

The application uses MongoDB for data storage. To initialize the database:

1. Ensure MongoDB is running on localhost:27017
2. Run the initialization script:
   ```bash
   python init_db.py
   ```

This will create:
- Sample trek data from `treks_data.json`
- Default admin user (username: admin, password: admin123)
- Sample user for testing (email: user@example.com, password: password123)

## Running the Application

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start MongoDB server (if not already running)

3. Initialize the database:
   ```bash
   python init_db.py
   ```

4. Run the Flask application:
   ```bash
   python app.py
   ```

5. Access the application at `http://localhost:5000`

6. For first-time use, you can register a new account or use the sample user:
   - Email: user@example.com
   - Password: password123

7. Admin access:
   - Admin URL: `http://localhost:5000/admin`
   - Default credentials: username: admin, password: admin123

8. User flow:
   - New users: Register at `/register`
   - After registration: Login at `/login`
   - After login: Redirected to landing page (not dashboard)
   - From landing page: Browse treks and book slots

## User Flow

The application implements a proper user flow:

1. **Registration**: Users register at `/register` with name, email, mobile, and password
2. **Login**: After registration, users login at `/login`
3. **Landing Page**: Successful login redirects to landing page (not dashboard)
4. **Profile Management**: Users can access profile at `/profile` through user menu
5. **Booking**: From landing page or trek pages, users can book treks at `/book/<trek_id>`
6. **Session Management**: Users stay logged in until they logout or session expires

## API Endpoints

The backend provides several API endpoints for AJAX requests:

- `/api/treks` - Get all treks in JSON format
- `/api/check_availability` - Check trek availability for booking

## Security Features

- Password hashing with bcrypt
- Session management with Flask-Session
- Form validation and sanitization
- Role-based access control (user/admin)

## Booking Process

The portal now includes a simplified booking process without payment requirements:

- **Direct Booking** - No payment required
- **Instant Confirmation** - Bookings confirmed immediately
- **Trek Pass Generation** - QR code pass generated upon booking
- **Slot Management** - Real-time slot availability tracking

### Booking Flow

1. Select trek and date
2. Choose time slot (morning or afternoon)
3. Enter personal details
4. Confirm booking
5. Download trek pass with QR code

## Sample Data

The `treks_data.json` file contains sample data for 12 popular Sahyadri treks:
1. Rajgad Fort
2. Torna Fort
3. Sinhagad Fort
4. Harishchandragad Fort
5. Visapur Fort
6. Lohagad Fort
7. Mahuli Fort
8. Raigad Fort
9. Korigad Fort
10. Pratapgad Fort
11. Trimbakeshwar Fort
12. Purandar Fort

Each trek entry includes comprehensive information such as difficulty level, historical background, trail details, and safety information.