# ייבוא של ספריות עזר של מסד הנתונים
import mysql.connector
from conf_MySQL import create_database, initialize_the_system, connect_database

# -------------------------------------------------- Summary  ----------------------------------------------------------
"""
בחלק זה נעסוק ביצירת תפריט המערכת שתרוץ בקומפיילר,
בחלק הזה נפעיל את התפריט ביחד עם הפונקציונליות לכל ישות,
כלומר כאן נממש את הפונקציות השונות לכל מחלקה ובהתאם לתפריט שנבחר.
"""

# ------------------------------------------------ Utility Functions ----------------------------------------------------
# משתנה גלובלי לשמירת המשתמש המחובר
current_user = {"id": None, "name": None, "type": None}


def get_user_from_database(cursor, user_type, user_id, password):
    """Retrieve user details from the database."""
    # בדיקת פרטי ההתחברות בטבלת Passwords_Users
    cursor.execute(
        """
        SELECT COUNT(*) FROM Passwords_Users
        WHERE id = %s AND password = %s
        """,
        (user_id, password),
    )
    user_exists = cursor.fetchone()[0]
    if user_exists:
        query = f"SELECT name FROM {user_type}s WHERE id = %s"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()
    return None


# ------------------------------------------ Main Menu Function --------------------------------------------------------
def main_menu():
    while True:
        print("\n======= 🎓 Welcome to Tomorrow's Academy System 🎓 ========")
        print("1. Manager 👨‍💼")
        print("2. Teacher 👩‍🏫")
        print("3. Student 👨‍🎓")
        print("4. Parent 👪")
        print("5. General Worker 🛠️")
        print("6. Exit The System 🚪")
        print("============================================================")
        choice = input("Enter your choice (1-6): ").strip()

        if choice in ["1", "2", "3", "4", "5"]:
            user_type = ["Manager", "Teacher", "Student", "Parent", "General Worker"][
                int(choice) - 1]  # הוצאה לפי אינדקס
            login(user_type)  # שליחה לתפריט הרלוונטי
        elif choice == "6":
            print("\nExiting The System... 🚪")
            exit()
        else:
            print("\n❌ Invalid choice. Please choose a valid option (1-6).")


# ------------------------------------------ Login Function ------------------------------------------------------------
def login(user_type):
    print(f"\n--- 🔐 {user_type} Login ---")

    for attempt in range(3):  # מאפשר 3 ניסיונות לכל סוג משתמש
        try:
            user_id_input = input("Enter ID number: ").strip()
            if not user_id_input.isdigit():
                raise ValueError("❌ Invalid ID format. ID must be a number.")
            user_id = int(user_id_input)

            password = input("Enter password: ").strip()
            if not password:
                raise ValueError("❌ Password cannot be empty.")

            with connect_database() as connection:
                with connection.cursor() as cursor:
                    result = get_user_from_database(cursor, user_type, user_id, password)

                    if result:
                        name = result[0]

                        # 🔹 שמירת פרטי המשתמש המחובר
                        global current_user
                        current_user["id"] = user_id
                        current_user["name"] = name
                        current_user["type"] = user_type  # לדוגמה: Student, Teacher וכו'

                        print(f"\n✅ Login successful! Welcome, {name}! 👋")
                        process_user_menu(cursor, user_type, user_id)
                        return
                    else:
                        print("❌ \nUser not found. Please check your credentials and try again.")

        except mysql.connector.Error as e:
            print(f"❌ An error occurred while connecting to the database: {e}")
        except ValueError as ve:
            print(f"❌ Input error: {ve}")

        print(f"❗ Invalid credentials. You have {2 - attempt} attempts left.\n")

    print("❌ Too many failed attempts. Returning to main menu... 🔙")
    main_menu()  # חזרה לתפריט הראשי אם נרשמו 3 ניסיונות כושלים


# ------------------------------------------ Process User Menu ---------------------------------------------------------
def process_user_menu(cursor, user_type, user_id):
    """Fetch user data and display their menu."""
    try:
        if user_type == "Manager":
            from Core.Manager import Manager, Manager_Menu  # ✅ יבוא דחוי
            cursor.execute("""
                SELECT id, name, school_budget
                FROM Managers
                WHERE id = %s
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                manager_name, user_id, school_budget = result
                user_object = Manager(manager_name, user_id, school_budget)
                menu = Manager_Menu(user_object)
            else:
                raise ValueError(f"❌ No manager found with ID {user_id}.")

        elif user_type == "Teacher":
            from Core.Teacher import Teacher, Teacher_Menu  # ✅ יבוא דחוי
            cursor.execute("""
                SELECT id, name, expertise, salary
                FROM Teachers
                WHERE id = %s
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                teacher_name, user_id, expertise, salary = result
                user_object = Teacher(teacher_name, user_id, expertise, salary)
                menu = Teacher_Menu(user_object)
            else:
                raise ValueError(f"❌ No teacher found with ID {user_id}.")

        elif user_type == "Student":
            from Core.Student import Student, Student_Menu  # ✅ יבוא דחוי
            cursor.execute("""
                SELECT id, name, age, parent_email, preferred_course
                FROM Students
                WHERE id = %s
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                student_name, user_id, age, parent_email, preferred_course = result
                user_object = Student(student_name, user_id, age, parent_email, preferred_course)
                menu = Student_Menu(user_object)
            else:
                raise ValueError(f"❌ No student found with ID {user_id}.")

        elif user_type == "Parent":
            from Core.Parent import Parent, Parent_Menu  # ✅ יבוא דחוי
            cursor.execute("""
                SELECT id, name, email
                FROM Parents
                WHERE id = %s
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                parent_name, user_id, email = result
                user_object = Parent(parent_name, user_id, email)
                menu = Parent_Menu(user_object)
            else:
                raise ValueError(f"❌ No parent found with ID {user_id}.")

        elif user_type == "General Worker":
            from Core.General_Worker import General_Worker, General_Worker_Menu  # ✅ יבוא דחוי
            cursor.execute("""
                SELECT id, name, salary
                FROM General_Workers
                WHERE id = %s
            """, (user_id,))
            result = cursor.fetchone()
            if result:
                general_worker_name, user_id, salary = result
                user_object = General_Worker(general_worker_name, user_id, salary)
                menu = General_Worker_Menu(user_object)
            else:
                raise ValueError(f"❌ No general worker found with ID {user_id}.")

        else:
            raise ValueError("❌ Invalid user type.")

        menu.display_menu()
        main_menu()

    except ValueError as ve:
        print(ve)


# -------------------------------------------- Run System --------------------------------------------------------------
if __name__ == "__main__":
    create_database()
    initialize_the_system()
    main_menu()
