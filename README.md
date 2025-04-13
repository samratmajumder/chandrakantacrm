# Chandrakanta CRM

A web-based Customer Relationship Management (CRM) system for creating and managing customer estimates.

## Features

- **Authentication**: Google OAuth-based login system
- **Dashboard**: View statistics on estimates, customers, and products
- **Customer Management**: Add, search, and manage customer information
- **Estimate Creation**: Create detailed estimates with multiple items
- **Search Functionality**: Search estimates by customer or date
- **Print-Ready Estimates**: Generate professional, printable estimates

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask
- **Database**: SQLite
- **Authentication**: Google OAuth
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Charts**: Chart.js

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/chandrakantacrm.git
   cd chandrakantacrm
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the project root
   - Add the following variables:
     ```
     SECRET_KEY=your_secret_key
     GOOGLE_CLIENT_ID=your_google_client_id
     GOOGLE_CLIENT_SECRET=your_google_client_secret
     ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application at `http://localhost:5000`

## Project Structure

```
chandrakantacrm/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── database.py            # Database models and operations
├── requirements.txt       # Python dependencies
├── static/                # Static assets
│   ├── css/               # CSS stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images and uploads
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── login.html         # Login page
│   ├── dashboard.html     # Dashboard page
│   ├── customers.html     # Customer management
│   ├── search.html        # Search functionality
│   ├── estimate_form.html # Estimate creation form
│   └── estimate_view.html # Estimate view/print
└── .env                   # Environment variables (not in repo)
```

## Usage

1. **First-time Login**: The first user to log in with Google will be automatically added to the allowed users list.
2. **Dashboard**: View key statistics and trends.
3. **Customers**: Add and manage customer information.
4. **Create Estimate**: Create detailed estimates for customers.
5. **Search**: Find estimates by customer name, mobile number, or date.
6. **View/Print Estimate**: View estimate details and print them.

## Configuration

You can modify the store information in `config.py`:

- Store name
- Store address
- Contact information
- Allowed users (email addresses)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Bootstrap for the UI components
- Font Awesome for the icons
- Chart.js for the dashboard charts
