import mysql.connector
from mysql.connector import Error


def connect_database():
    """
    חיבור למסד הנתונים tomorrows_academy.

    :return: חיבור למסד הנתונים.
    """
    try:
        connection = mysql.connector.connect(
            host="",  # שם השרת (localhost = השרת המקומי)
            user="",  # שם המשתמש
            password="",  # סיסמה למשתמש root
            database=""  # שם מסד הנתונים שברצונך להתחבר אליו
        )

        return connection
    except Error as e:
        print(f"שגיאה בחיבור למסד הנתונים: {e}")


def create_database():
    """
    יצירת מסד הנתונים tomorrows_academy אם הוא לא קיים.
    """
    try:
        with mysql.connector.connect(
                host="",  # שם השרת (localhost = השרת המקומי)
                user="",  # שם המשתמש
                password="",  # סיסמה למשתמש root
        ) as connection:
            with connection.cursor() as cursor:
                # בדיקה אם מסד הנתונים כבר קיים
                cursor.execute("SHOW DATABASES")
                databases = [db[0] for db in cursor.fetchall()]

                if "tomorrows_academy" in databases:
                    return  # אם מסד הנתונים קיים, אין צורך ליצור אותו מחדש

                # יצירת מסד הנתונים
                cursor.execute("CREATE DATABASE tomorrows_academy")
                print("✅ מסד הנתונים נוצר בהצלחה!")

    except Error as e:
        print(f"❌ שגיאה ביצירת מסד הנתונים: {e}")


# ------------------------------------------------------- Create Tables ------------------------------------------------
def create_manager_table(cursor):
    """
    יצירת טבלת מנהלים (Managers) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Managers (
        id INT UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        school_budget FLOAT DEFAULT 32000,
        PRIMARY KEY (id)
    );
    """)


def create_parents_table(cursor):
    """
    יצירת טבלת הורים (Parents) אם היא לא קיימת, כולל עמודת payment.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Parents (
        id INT UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) DEFAULT NULL,
        payment FLOAT DEFAULT 0,
        PRIMARY KEY (id)
    );
    """)


def create_students_table(cursor):
    """
    יצירת טבלת תלמידים (Students) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        id INT UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        age INT NOT NULL,
        parent_email VARCHAR(100) NOT NULL,
        preferred_course VARCHAR(100) NOT NULL,
        PRIMARY KEY (id)
    );
    """)


def create_teachers_table(cursor):
    """
    יצירת טבלת מורים (Teachers) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Teachers (
        id INT UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        expertise VARCHAR(100) NOT NULL,
        salary FLOAT DEFAULT 2300 NOT NULL,
        PRIMARY KEY (id)
    );
    """)


def create_general_workers_table(cursor):
    """
    יצירת טבלת עובדים כלליים (General_Workers) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS General_Workers (
        id INT UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        salary FLOAT DEFAULT 2000 NOT NULL,
        PRIMARY KEY (id)
    );
    """)


def create_courses_table(cursor):
    """
    יצירת טבלת קורסים (Courses) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Courses (
        course_id INT AUTO_INCREMENT NOT NULL,
        course_name VARCHAR(100) NOT NULL,
        teacher_id INT,
        capacity INT NOT NULL,
        registered_students INT DEFAULT 0 NOT NULL,
        course_age INT DEFAULT 12 NOT NULL,
        PRIMARY KEY (course_id),
        FOREIGN KEY (teacher_id) REFERENCES Teachers(id)
    );
    """)


def create_waitlists_table(cursor):
    """
    יצירת טבלת תורים (Waitlists) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Waitlists (
        id INT AUTO_INCREMENT NOT NULL,
        course_id INT NOT NULL,
        student_id INT NOT NULL,
        date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (course_id) REFERENCES Courses(course_id),
        FOREIGN KEY (student_id) REFERENCES Students(id)
    );
    """)


def create_tasks_table(cursor):
    """
    יצירת טבלת משימות (Tasks) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tasks (
        id INT AUTO_INCREMENT NOT NULL,
        name VARCHAR(100) NOT NULL,
        description VARCHAR(255) NOT NULL,
        status ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED') DEFAULT 'PENDING',
        urgency ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
        reporter_id INT NOT NULL,
        PRIMARY KEY (id)
    );
    """)


def create_passwords_users_table(cursor):
    """
    יצירת טבלת משתמשים וסיסמאות (Passwords_Users) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Passwords_Users (
        id INT UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        password VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
    );
    """)


# ------------------------------------------------------- Relationship Tables ------------------------------------------
def create_course_teacher_table(cursor):
    """
    יצירת טבלת קשר בין קורסים למורים (Course_Teacher) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Course_Teacher (
        course_id INT NOT NULL,
        teacher_id INT NOT NULL,
        PRIMARY KEY (course_id, teacher_id),
        FOREIGN KEY (course_id) REFERENCES Courses(course_id),
        FOREIGN KEY (teacher_id) REFERENCES Teachers(id)
    );
    """)


def create_student_course_table(cursor):
    """
    יצירת טבלת קשר בין תלמידים לקורסים (Student_Course) אם היא לא קיימת.
    כולל עמודת payment_status לבדיקה אם ההורה שילם עבור הקורס.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Student_Course (
        student_id INT NOT NULL,
        course_id INT NOT NULL,
        assignments TEXT, -- רשימת משימות של התלמיד בקורס
        grades FLOAT, -- ציונים בקורס
        schedule TEXT, -- לוח זמנים בקורס
        payment_status ENUM('PAID', 'UNPAID') DEFAULT 'UNPAID',
        FOREIGN KEY (student_id) REFERENCES Students(id),
        FOREIGN KEY (course_id) REFERENCES Courses(course_id)
    );
    """)


def create_student_parent_table(cursor):
    """
    יצירת טבלת קשר בין סטודנטים להורים (Student_Parent) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Student_Parent (
        student_id INT NOT NULL,
        parent_id INT NOT NULL,
        PRIMARY KEY (student_id, parent_id),
        FOREIGN KEY (student_id) REFERENCES Students(id),
        FOREIGN KEY (parent_id) REFERENCES Parents(id)
    );
    """)


def create_task_worker_table(cursor):
    """
    יצירת טבלת קשר בין משימות לעובדים כלליים (Task_Worker) אם היא לא קיימת.
    """
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Task_Worker (
        task_id INT NOT NULL,
        worker_id INT NOT NULL,
        PRIMARY KEY (task_id, worker_id),
        FOREIGN KEY (task_id) REFERENCES Tasks(id),
        FOREIGN KEY (worker_id) REFERENCES General_Workers(id)
    );
    """)


# ---------------------------------------------------- Create Admin User -----------------------------------------------
def ensure_admin_exists(cursor):
    """
    לוודא קיום מנהל ראשוני (admin) במערכת.
    אם אין מנהל, המנהל הראשוני יווצר.
    """
    # בדיקה אם קיים מנהל במערכת
    cursor.execute("SELECT COUNT(*) FROM Managers")
    manager_count = cursor.fetchone()[0]

    if manager_count == 0:
        # יצירת מנהל ראשוני
        admin_id = 1  # מזהה ייחודי למנהל הראשוני
        admin_name = "Admin User"
        admin_password = "admin1234"
        school_budget = None

        # הוספה לטבלת Managers
        cursor.execute("""
        INSERT INTO Managers (id, name, school_budget)
        VALUES (%s, %s, %s)
        """, (admin_id, admin_name, school_budget))

        # הוספה לטבלת passwords_users
        cursor.execute("""
        INSERT INTO Passwords_Users (id, name, password)
        VALUES (%s, %s, %s)
        """, (admin_id, admin_name, admin_password))

        return True  # מנהל חדש נוצר

    return False  # מנהל כבר קיים


# --------------------------------------------------------------- Initialized Tables -----------------------------------
def initialize_the_system():
    """
    יצירת כל הטבלאות הנדרשות במסד הנתונים אם הן לא קיימות.
    """
    try:
        with connect_database() as connection:
            with connection.cursor() as cursor:
                # בדיקה אם קיימות טבלאות
                cursor.execute("SHOW TABLES")
                existing_tables = [table[0] for table in cursor.fetchall()]

                if existing_tables:  # אם כבר קיימות טבלאות, לא יוצרים שוב
                    return

                # יצירת כל הטבלאות
                create_manager_table(cursor)
                create_parents_table(cursor)
                create_students_table(cursor)
                create_teachers_table(cursor)
                create_general_workers_table(cursor)
                create_courses_table(cursor)
                create_waitlists_table(cursor)
                create_tasks_table(cursor)
                create_passwords_users_table(cursor)
                create_course_teacher_table(cursor)
                create_student_course_table(cursor)
                create_student_parent_table(cursor)
                create_task_worker_table(cursor)

                # יצירת מנהל ראשוני אם אין
                admin_created = ensure_admin_exists(cursor)

                connection.commit()

                # הדפסת הודעה אם כל הטבלאות נוצרו לראשונה
                print("✅ כל הטבלאות נוצרו בהצלחה!")

                # הדפסת הודעה רק אם נוצר מנהל חדש
                if admin_created:
                    print("✅ מנהל ראשוני נוצר בהצלחה: Admin User!")

    except Error as e:
        print(f"❌ שגיאה ביצירת הטבלאות: {e}")
