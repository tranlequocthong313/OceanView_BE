# 🌊 OceanView - Apartment Management Project 🏢

The **OceanView** Apartment Management Project is a management system designed for apartment buildings, offering a wide range of features and utilities for both administrators and residents. Below are some key features of the project:

- **👤 Account Management:** Administrators can create and manage accounts for residents.
- **💳 Fee Payments:** Residents can pay fees such as management fees, parking fees, and other services through online payment methods.
- **🧾 Invoice Management:** Residents can view and manage their paid invoices on the system.
- **🚗 Parking Card Management:** Residents can register for parking cards for their family members to access parking and entry gates.
- **📢 Feedback Submission:** Residents can submit feedback on issues for the management board to address.
- **📊 Surveys and Statistics:** The management board can create and analyze survey results from residents regarding activities and services at the apartment complex.

And many other features! 🌟

## 🛠️ Installation and Project Setup Guide

### 1. 🖥️ System Requirements

- 🐍 Python (version 3.x)
- 🗄️ MySQL
- 📦 pip (for managing the Python virtual environment)

### 2. 🚀 Project Installation

1. **Clone the project from the repository:** 

   ```
   git clone https://github.com/tranlequocthong313/OceanView_BE.git
   ```

2. **Navigate to the project directory:**

   ```
   cd OceanView_BE
   ```

3. **Create and activate a virtual environment:**

   ```
   python -m venv venv
   source venv/Scripts/activate
   ```

4. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```

### 3. 🔧 Environment Variables Configuration

Create a `.env` file in the root directory of the project and configure the necessary environment variables, including the MySQL database settings.

### 4. 📂 Database Initialization

1. **Create a MySQL database** with the information configured in the `.env` file.

2. **Run migrations to create tables and update the database:**

   ```
   python manage.py migrate
   ```

### 5. 🎉 Running the Project

After completing the above steps, you can start the development server with the following command:

```
python manage.py runserver
```

Open your browser and go to `http://127.0.0.1:8000/` to view the OceanView project. 🌐

Enjoy managing your apartment complex with OceanView! 🏡✨

---

## 📌 Use Cases
   
   ![Use Case](path_to_image)

---

## 🛠️ System Design

The OceanView system is designed with a focus on scalability and ease of use:

1. **📊 Database Schema:** The database schema is structured to efficiently handle large amounts of resident and transaction data.
   
   ![Database Schema](path_to_image)

3. **🖥️ Backend Architecture:** The backend architecture is built using Python and Django, with RESTful APIs for interaction between the client and server.

   ![Backend Architecture](path_to_image)

---

## 📷 Results and Outcomes

Here are screenshots showcasing the various user interfaces of the OceanView system:

1. **🏠 Dashboard:** The main dashboard for residents, displaying key information such as outstanding fees, upcoming events, and recent notices.

   ![Dashboard](path_to_image)

2. **💳 Payment Portal:** The payment interface where residents can view and pay their bills online.

   ![Payment Portal](path_to_image)

3. **🧾 Invoice Management:** A screen for viewing and managing invoices, with options to download or print receipts.

   ![Invoice Management](path_to_image)

4. **📢 Feedback Submission:** The feedback submission form where residents can report issues or provide suggestions.

   ![Feedback Submission](path_to_image)

5. **🚗 Parking Card Management:** The interface for managing parking card registrations and access.

   ![Parking Card Management](path_to_image)

---
