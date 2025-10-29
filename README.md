# 🏢 AI-Enhanced HRMS Portal

> A next-generation, AI-integrated Human Resource Management System built using **Streamlit**, **Python**, and **MongoDB**.

![HRMS Screenshot](https://placehold.co/1000x450/8a2be2/FFFFFF/png?text=HRMS+Portal+Dashboard)

---

## 📘 Overview

The **AI-Enhanced HRMS Portal** is a smart, web-based solution designed to streamline key HR operations such as **attendance tracking**, **leave management**, and **employee communication**.  

Developed as part of a 3-month internship project, the system leverages **Ollama’s Llama 3 AI model** to automatically generate professional leave letters for employees — showcasing the power of AI in real-world HR applications.

---

## ✨ Core Features

### 👤 Employee Features
- 🧭 **Personalized Dashboard:** View attendance KPIs, leave status, and HR announcements.  
- ⏱ **Real-time Attendance:** Clock in/out with a live timer displaying total hours worked.  
- 📊 **Visual Analytics:**
  - 180-day heatmap of attendance patterns.  
  - Weekly bar chart for “Hours Worked.”  
  - 30-day attendance summary pie chart.  
- 🤖 **AI Leave Letter Generator:** Instantly create formal leave letters using **Llama 3**.  
- 📁 **Profile Management:** Securely update personal details and passwords.  
- 💬 **HR Chat Module:** Communicate directly with HR in real-time.

### 👑 HR & Admin Features
- 👥 **User Management:** Add, edit, or remove users with role-based permissions.  
- 🧮 **Analytics Dashboard:**  
  - Department-wise employee distribution.  
  - Attendance and leave insights.  
  - New hire analytics.  
- 🗂 **Employee Hub:** Centralized employee profile and performance tracking.  
- 🗓 **Leave Approvals:** Approve or reject leave requests seamlessly.  
- 📢 **Communication Hub:** Post company-wide messages and HR updates.

---

## 🧱 Technology Stack

| Layer | Technology |
|:------|:------------|
| **Frontend** | Streamlit |
| **Backend** | Python 3.10 |
| **Database** | MongoDB (Atlas / Local) |
| **AI Engine** | Ollama (Llama 3) |
| **Data Analysis** | Pandas |
| **Visualization** | Plotly / Plotly Express |
| **Authentication** | Passlib (bcrypt) |
| **UI Enhancements** | streamlit-option-menu |
| **AI Integration** | Requests |

---

## ⚙️ Setup & Installation

### 🧩 Prerequisites
Ensure you have the following installed:
- Python **3.9+**
- **MongoDB Atlas** account *(or local MongoDB instance)*
- [**Ollama**](https://ollama.com/) installed and configured

---

### 🔧 Step 1: Clone the Repository
```bash
git clone https://github.com/HARI-45-FAV/northface_intern.git
cd hrms_steamlit
⚙️ Step 2: Configuration
Create a .env file in the root directory:

ini
Copy code
MONGO_USER="your_mongo_user"
MONGO_PASS="your_mongo_password"
MONGO_CLUSTER="your.cluster.mongodb.net"
Pull the AI model using Ollama:

bash
Copy code
ollama pull llama3
(Optional) Add dummy users for testing:

bash
Copy code
python create_dummy_users.py
Default Test Logins:

Role	Username	Password
Admin	admin	adminpassword123
HR	hr	hrpassword123
Employee	david.chen	password123

🚀 Step 3: Run the Application
Start Ollama in one terminal:

bash
Copy code
ollama serve
Run Streamlit in another:

bash
Copy code
streamlit run app.py
Access the app at:
🔗 http://localhost:8501

📁 Project Structure
bash
Copy code
hrms_steamlit/
├── app.py                   # Main app router & login logic
├── db.py                    # MongoDB connection handler
├── auth.py                  # Authentication & password hashing
├── requirements.txt
├── .env                     # Environment variables (excluded from Git)
├── create_dummy_users.py    # Script to generate sample users
└── modules/
    ├── admin_hr_dashboard.py  # HR/Admin dashboard
    ├── attendance.py          # Attendance tracking logic
    ├── communication.py       # Chat & announcements
    ├── employee_dashboard.py  # Employee view
    ├── leaves.py              # Leave management + AI integration
    └── profile_page.py        # User profile management
🎓 Internship Project Summary
This project was developed as part of an academic internship focused on integrating AI technologies into modern HR systems.
The portal demonstrates the use of Streamlit, MongoDB, and AI-powered automation to optimize HR workflows.

Key Focus Areas:

Full-stack web development using Streamlit & MongoDB

AI integration via Ollama’s Llama 3 model

Interactive data visualization using Plotly

Secure authentication & role-based access control

🙌 Acknowledgements
Developed as part of the NorthFace Internship Program.

Thanks to the Streamlit, Plotly, and Ollama teams for their open-source tools.

Supervised and guided by mentors and peers during the internship.
