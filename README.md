# OrganiByRima - Club Management System

## 1. Project Overview
**OrganiByRima** is a comprehensive web-based application designed to streamline the management of school clubs and organizations. It provides a centralized platform for administrators to manage members, organize events, track attendance, and handle financial records.

This project demonstrates the integration of a **Python (Flask)** backend with a **MySQL** relational database, utilizing **HTML/CSS/JavaScript** for a responsive and user-friendly frontend.

---

## 2. Technical Architecture

The application follows the **Model-View-Controller (MVC)** architectural pattern (adapted for Flask):

*   **Backend (Controller)**: Python with the Flask framework handles HTTP requests, processes business logic, and interacts with the database.
*   **Database (Model)**: MySQL is used for persistent data storage. It stores relational data for members, events, attendance, and payments.
*   **Frontend (View)**: HTML5 templates (Jinja2), CSS3 (Bootstrap 5 + Custom Styles), and JavaScript provide the user interface.

### Python & MySQL Integration
The core of this project is the robust connection between the Python application and the MySQL database.

1.  **Connector**: We use the `mysql-connector-python` library to establish communication.
2.  **Connection Management**:
    *   The database connection is managed in `db.py`.
    *   We utilize Flask's `g` object (global namespace) to store the database connection for the duration of a single request.
    *   **`get_db()`**: Checks if a connection exists for the current request; if not, it creates one.
    *   **`teardown_appcontext`**: Ensures the database connection is automatically closed after every request, preventing resource leaks.
3.  **CRUD Operations**: The application performs Create, Read, Update, and Delete operations using SQL queries executed via Python cursors.

---

## 3. How It Works (Feature Walkthrough)

### A. Dashboard & Statistics
*   **Functionality**: Upon logging in, the user is presented with a dashboard showing real-time statistics.
*   **Technical**: The backend executes `SELECT COUNT(*)` and `SELECT SUM()` queries to aggregate data (e.g., total members, total revenue) and passes these values to the `index.html` template.

### B. Member Management
*   **Adding a Member**:
    1.  User navigates to the "Members" page and fills out the "Add New Member" form.
    2.  **Python**: The `POST` request is captured in `app.py`.
    3.  **SQL**: An `INSERT INTO members (full_name, email, class_name) ...` query is executed.
    4.  The page reloads to show the updated list.
*   **Listing Members**: A `SELECT * FROM members` query retrieves all records, which are then looped through in the HTML template to display the table.

### C. Event Management
*   Allows the creation of events with details like Title, Description, Date, and Price.
*   Events are stored in the `events` table and sorted by date (`ORDER BY date_event DESC`) to show the most relevant ones first.

### D. Attendance Tracking
*   Links **Members** to **Events**.
*   **Technical**: This uses a Many-to-Many relationship. The `attendance` table stores `id_member` and `id_event` as foreign keys.
*   **Logic**: When marking attendance, the system performs an `INSERT ... ON DUPLICATE KEY UPDATE` to ensure a member's status can be updated (e.g., from Absent to Present) without creating duplicate records.

### E. Financials (Payments)
*   Records payments made by members for specific events.
*   Tracks the Payment Method (Cash, Card, Transfer).
*   Calculates total revenue dynamically for the dashboard.

---

## 4. Database Schema

The system relies on four main tables:
1.  **`members`**: Stores student details (ID, Name, Email, Class).
2.  **`events`**: Stores event details (ID, Title, Date, Price).
3.  **`attendance`**: Junction table linking Members and Events with a status (Present/Absent).
4.  **`payments`**: Records financial transactions linked to Members and Events.

---

## 5. Setup & Installation

### Prerequisites
*   Python 3.10+
*   MySQL Server (XAMPP, WAMP, or Workbench)

### Installation Steps
1.  **Clone/Download** the project folder.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Database Configuration**:
    *   Open your MySQL client.
    *   Import `database/schema.sql` to create the database structure.
    *   Open `db.py` and update the `DB_CONFIG` dictionary with your MySQL credentials:
        ```python
        DB_CONFIG = {
            'user': 'root',      # Your MySQL username
            'password': '',      # Your MySQL password
            'host': 'localhost',
            'database': 'smart_club'
        }
        ```
4.  **Run the Application**:
    ```bash
    python app.py
    ```
5.  **Access**: Open your browser and visit `http://127.0.0.1:5000`.

---

*Developed by Rima for the Mini Projet BD.*
