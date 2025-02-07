# 📚 Tomorrow's Academy Management System

## 📝 Project Description
Tomorrow's Academy is a comprehensive system designed to manage an educational institution. It provides functionalities for different user roles, including administrators, teachers, students, parents, and general workers. The system allows efficient management of courses, student enrollments, teacher workloads, payment tracking, and maintenance requests.

## 💻 Technologies Used
- **Programming Language:** Python
- **Database:** MySQL
- **Frameworks/Libraries:**
  - `mysql.connector` for database interactions
  - Regular expressions (`re`) for input validation
  - `pandas` for data analysis

## 📂 Project Structure
```
Tomorrow's Academy/
│── Core/
│   ├── Manager.py
│   ├── Teacher.py
│   ├── Student.py
│   ├── Parent.py
│   ├── General_Worker.py
│   ├── Task.py
│   ├── Request.py
│   ├── Course.py
│   ├── Person.py
│── Database/
│   ├── conf_MySQL.py
│── Files/
│   ├── learning_center_project_data/
│   ├── UML - "אקדמיית המחר".svg
│   ├── הנחיות לפרויקט גמר.pdf
│── Init/
│   ├── System_Menu.py
│   ├── Create_Objects_To_Sys.py
│── Utils/
│   ├── task_status.py
│   ├── UrgencyLevel.py
│── README.md
```

## 🚀 Installation & Setup
### Prerequisites:
1. Install Python (version 3.8+ recommended)
2. Install MySQL Server
3. Install required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Setting up the database
Run the following command to create the database and tables automatically:
```sh
python System_Menu.py
```

## 🔐 First-time Login
After setting up the system, log in as a **Manager** using the following credentials:
- **User ID:** `1`
- **Password:** `admin1234`

Once logged in, you can create users, manage courses, and generate reports.

## 🎯 Main Features
### 🔹 User Roles & Functionalities
- **Manager 👨‍💼**
  - Create, update, and remove users (teachers, students, parents, workers)
  - Generate various reports (payment tracking, student progress, teacher workload, maintenance logs, waitlists)
  - Manage courses and student enrollments
  - Review course waitlists and suggest opening new courses

- **Teacher 👩‍🏫**
  - Assign grades and track student progress
  - View students enrolled in their courses

- **Student 🎓**
  - View personal schedules
  - Check grades and assignments
  - Track enrollment status in waitlists

- **Parent 👪**
  - Enroll children in courses
  - Track children’s progress (grades, schedules, waitlists)
  - Make payments for enrolled courses
  - Generate payment reports

- **General Worker 🛠️**
  - Update maintenance task statuses
  - View assigned tasks

### 📊 Reports
1. **Teacher Workload Report** – Displays the number of courses assigned to each teacher.
2. **Payment & Debts Report** – Tracks payments made by parents and outstanding fees.
3. **Student Performance Report** – Summarizes student grades and assignments.
4. **Maintenance Report** – Logs maintenance tasks assigned to general workers.
5. **Course Waitlist Overview** – Suggests opening new courses if demand is high.
6. **Student Enrollment Report** – Tracks student registrations across courses.

## 🎯 Example Usage
1. **Starting the system:**
   ```sh
   python System_Menu.py
   ```
2. **Logging in as a manager and creating users.**
3. **Enrolling students in courses.**
4. **Generating financial reports.**
5. **Updating teacher workloads and student performance tracking.**

## ⚠️ Notes
- Payments are processed manually, assuming a fixed course fee of **$500** per enrollment.
- When a student is added to a waitlist, their position in the queue is displayed.

## 📌 Future Improvements
- Add email notifications for parents regarding payments and enrollments.
- Improve graphical reporting with `matplotlib`.

---
✅ Developed for **Tomorrow's Academy Final Project**

