# Campus Event Management System

A small web application to organize events, manage student sign-ups, record check-ins, and see reports — everything in a single application.

## Features

- **Event Management**: Create, view, and organize campus events
- **User Registration**: Students can sign up for events
- **Check-in System**: Real-time event check-in system
- **Analytics Dashboard**: Event statistics and insights
- **Role-based Access**: Admin, Staff, and Student roles
- **Responsive Design**: Desktop and mobile support

## Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package installer)

### Installation & Run Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app_simple.py
   ```
**Note**: If you encounter SQLAlchemy compatibility issues with Python 3.13, use `app_simple.py` in place of `app.py` instead. The simple app depends on Flask and SQLite only and does not involve any SQLAlchemy dependencies.

3. **Access the Application**
   - Navigate your web browser to: `http://localhost:5000`
   - Automatically creates the database from some sample data

### Demo Accounts

- **Admin**: admin@campus.edu / admin123
- **Staff**: staff@campus.edu / staff123
- **Student**: student1@campus.edu / student123

## Project Structure

```
CampusDrive_Webknot_<YourName>.zip
│
├── app.py                  # Flask backend application
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── templates/
```
│   └── index.html         # Main web interface
│

├── AI_Conversation_Log/   # Screenshots of AI brainstorming
│   └── log1.png
│   └── log2.png
│

├── Design_Document/
│   └── Design_Document.pdf   # ER diagram, schema, APIs
│

└── Reports/
    └── Reports.txt           # Database queries and results
├── screenshots.png       # API/DB output screenshots
```

## API Endpoints

- `GET /` - Main application interface
- `POST /login` - User authentication
- `GET /api/events` - List all events
- `POST /api/registrations/<event_id>` - Register for event
- `DELETE /api/registrations/<event_id>` - Cancel registration
- `GET /api/my-registrations` - Get user's registrations
- `POST /api/checkin/<event_id>` - Check in to event
- `GET /api/analytics` - Get analytics data

## Database Schema

The application uses SQLite with the following top-level tables:
- Users (student, staff, admin)
- Events (event data and metadata)
- Registrations (user event registrations)
- CheckIns (event check-in tracking)
- EventCategories (event categorization)

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based
- **Styling**: Custom CSS with responsive design

## Features Implemented

✅ User authentication and role management
✅ Event creation and management
✅ Event registration system
✅ Check-in functionality
✅ Analytics dashboard
✅ Responsive web design
✅ Initialization of database with test data
✅ RESTful API routes

## Development Notes

- The app creates the database and test data on initial run automatically
- All user passwords are hashed securely using Werkzeug
- Session management takes care of user authentication
- The interface is completely responsive and functional on mobile devices
- Error handling and user feedback are included throughout

## Troubleshooting

If you're having trouble:
1. Make sure Python 3.7+ is installed
2. Make sure all the dependencies are installed: `pip install -r requirements.txt`
3. Make sure port 5000 is free for usage by another application
4. Check the console for any error messages

## Contact

In the event of having questions or needing support, please refer to the project documentation or reach out to the development team.