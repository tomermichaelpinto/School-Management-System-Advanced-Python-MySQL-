# ייבוא סיפריות מחלקה
import mysql
from mysql.connector import Error
from DataBase.conf_MySQL import connect_database
from Core.Person import Person
from Core.Student import Student
from Core.Course import Course

# ייבוא סיפריות עזר
import re
from abc import ABC
from typing import Set, Dict, List

from System_Menu import current_user


class Parent(Person, ABC):
    # ---------------------------------------------------------------- Summary -----------------------------------------
    """
    מחלקת הורה היורשת מ- Person ומנהלת ילדים, קורסים ותשלומים.
    """

    INVALID_NAME_MSG = "Parent name must be a valid string."
    INVALID_ID_MSG = "Parent ID must be a positive integer."
    INVALID_EMAIL_MSG = "Email must be a valid email address."

    # -------------------------------------------------------------- Constructor ---------------------------------------
    def __init__(self, name: str, id: int, email: str = None):
        super().__init__(name, id)
        self._name = name
        self._id = id
        self._email = email
        self._Charges = self.calculate_charges()  # חיובים

        # Set & Dict
        self._children: Set[Student] = set()  # רשימת ילדים מסוג Set
        self._parent_actions: List[str] = []  # מערך לשמירת פעולות ההורה במערכת
        """
        # מילון המעדכן את סך התשלומים של ההורה, כאשר המפתח הוא מזהה ההורה (self._id)
         והערך הוא הסכום הכולל של התשלומים שבוצעו עבור כל הילדים של ההורה.
        """
        self._payments: Dict[int, float] = {}  # שומר את הסכום ששולם (סכום שמצטבר לאורך התשלומים של ההורה)

    # -------------------------------------------------------- Setters & Getters ---------------------------------------
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        """
        מאמתת ומגדירה את השם.
        - חייב להיות מחרוזת שאינה ריקה.
        - חייב להתאים לפורמט: שתי מילים עם אות ראשונה גדולה והשאר קטנות (לדוגמה: 'John Doe').
        """
        if not isinstance(val, str) or not val.strip():
            raise ValueError("Name must be a non-empty string.")

        # בדיקה אם השם תואם לפורמט הנדרש
        if not re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", val):
            raise ValueError(
                "Invalid name format. Name must be in 'First Last' format, with each word starting with a capital letter."
            )

        self._name = val

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, val: int):
        """
        מאמתת ומגדירה את ה-ID.
        - חייב להיות מספר שלם חיובי.
        """
        if not isinstance(val, int) or val <= 0:
            raise ValueError("Invalid ID. ID must be a positive integer.")

        self._id = val

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        """
        מאמתת ומגדירה את כתובת האימייל.
        - חייבת להיות מחרוזת בפורמט אימייל תקין.
        """
        if not isinstance(value, str) or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise ValueError("Invalid email format. Please provide a valid email address.")

        self._email = value

    @property
    def Charges(self) -> int or float:
        return self._Charges

    @Charges.setter
    def Charges(self, value: int or float):
        if not isinstance(value, (int, float)):
            raise ValueError("Charges must be a number.")
        self._Charges = value

    @property
    def payments(self) -> Dict[int, float]:
        return self._payments

    @property
    def parent_actions(self) -> List[str]:
        return self._parent_actions

    @property
    def children(self):
        return self._children

    # ---------------------------------------------------- Basic Functions ---------------------------------------------
    def __str__(self) -> str:
        """
        מציגה את פרטי ההורה בצורה קריאה.
        """
        children_details = '\n'.join(
            f"- {child.name} (ID: {child.id})" for child in self._children) if self._children else "No children"
        return (
            f"Parent Details:\n"
            f"Name: {self.name}\n"
            f"ID: {self.id}\n"
            f"Email: {self._email or 'No email provided'}\n"
            f"Children:\n{children_details}"
        )

    def __eq__(self, other) -> bool:
        """
        השוואה בין שני אובייקטי Parent לפי כל התכונות.
        """
        if isinstance(other, Parent):
            return (
                    self.name == other.name and
                    self.id == other.id and
                    self._email == other._email and
                    self._children == other._children
            )
        return False

    def __hash__(self) -> int:
        """
        מחזיר את ה-hash של אובייקט Parent. מבוסס על כל התכונות.
        """
        return hash((self.name, self.id, self._email, tuple(self._children)))

    # ------------------------------------------------------ Advanced Functions ----------------------------------------
    def remove_child(self, child: Student):
        """
        מסיר ילד מהרשימה של הילדים של ההורה.
        :param child: אובייקט התלמיד שיש להסיר.
        """
        if child not in self._children:
            raise ValueError(f"{child.name} is not associated with this parent.")

        # הסרת הילד מהרשימה של ההורה
        self._children.remove(child)
        print(f"Child {child.name} removed successfully.")

    @staticmethod  # אין שימוש ב self
    def add_to_waitlist(child: Student, course: Course):
        """
        מוסיף את התלמיד לרשימת המתנה של הקורס אם הוא לא נמצא שם.
        :param child: אובייקט התלמיד.
        :param course: אובייקט הקורס.
        """
        # בדוק אם הילד כבר נמצא ברשימת המתנה
        if child in course.Requests:
            print(f"Student {child.name} is already on the waitlist for course {course.course_name}.")
            return

        # הוספת התלמיד לרשימת המתנה של הקורס ושל התלמיד
        child.requests.put(child)  # הוספת התלמיד לרשימה שלו
        course.Requests.put(child)  # הוספת התלמיד לרשימת ההמתנה של הקורס

        # הודעה על הצלחה
        print(f"Student {child.name} added to the waitlist for course {course.course_name}.")

    def enroll_child_to_course(self, child: Student, course: Course):
        """
        רושם את ילדו לקורס, במידה והקורס מלא, הילד ייכנס לרשימת המתנה.
        :param child: אובייקט התלמיד שצריך להירשם.
        :param course: אובייקט הקורס שאליו רוצים לרשום את התלמיד.
        """
        if child not in self._children:
            raise ValueError(f"{child.name} is not associated with this parent.")

        if course.registered_students == course.capacity:  # אם הקורס מלא, התלמיד ייכנס לרשימת המתנה
            self.add_to_waitlist(child, course)
            self._parent_actions.append(f"The parent {self.name} added child {child.name} to the waiting list.\n")

        else:  # אחרת, הקורס אינו מלא, התלמיד יירשם ישירות
            course.students.add(child.name)  # הוספה לרשימת התלמידים הרשומים לקורס
            child.courses.add(course)  # הוספה לרשימת הקורסים בהם לומד התלמיד
            self._parent_actions.append(f"The parent {self.name} added child {child.name} to the course"
                                        f" {course.course_name}.\n")
            print(f"Student {child.name} enrolled in {course.course_name}.")

    def track_child_progress(self, child: Student):
        """
        מעקב אחרי התקדמות הילד: ציונים, לוחות זמנים ומיקום בתורים.
        """
        if child not in self._children:
            raise ValueError(f"{child.name} is not associated with this parent.")
        print(self.get_progress(child))

    def get_progress(self, child: Student) -> str:  # מתודת עזר
        """
        מחזירה את התקדמות הילד (סטודנט): ציונים ומשימות, לוחות זמנים אישיים, ומיקום בתורים.
        """
        # התחלת דו"ח ההתקדמות עם שם הילד ו-ID
        ReportToParent = f"Progress report for {child.name} (ID: {child.id}):\n"

        # הוספת ציונים ומשימות לילד
        assignments_AND_grades = child.view_personal_assignments_and_grades()
        waitlist_position = child.receive_registration_updates()

        ReportToParent += assignments_AND_grades
        ReportToParent += waitlist_position

        # לולאה על כל הילדים של ההורה והקורסים שלהם
        for student in self.children:
            if student == child:  # מצא את הילד המבוקש, ואז הוסף לו את לוח הזמנים
                for course in student.courses:
                    ReportToParent += student.display_personal_schedule(course)
                break  # לא צריך להמשיך אחרי שמצאנו את הילד המבוקש

        return ReportToParent

    def Checking_Payments(self, child: Student):
        """
        פעולה לבדיקת תשלומים של התלמיד.
        """
        # בדיקה אם התלמיד קשור להורה
        if child not in self._children:
            raise ValueError(f"{child.name} is not associated with this parent.")

        # הצגת כותרת לבדיקה
        print(f"\nChecking payments for {child.name} (ID: {child.id}):")

        # חישוב הסכום הכולל של כל הקורסים
        SumToPay = 0
        Report = "Courses and Payments:\n"  # הכותרת לדיווח הקורסים
        Report += "--------------------" "\n"  # חיץ אסתטי בין הכותרת לתוכן

        # הלולאה כדי להדפיס את פרטי הקורסים
        for course in child.courses:
            Report += f"Course name: {course.course_name} (ID: {course.course_id})\n"
            Report += f"  Cost: {course.course_cost}$\n"  # הדפסת מחיר קורס
            SumToPay += course.course_cost  # סכימת עלות הקורסים

        # הדפסת הסכום הכולל
        Report += "-" * 40 + "\n"  # חיץ אסתטי נוסף
        Report += f"\nThe total amount for all courses is: {SumToPay}$"  # סכום כולל

        # הצגת הדיווח הסופי
        print(Report)

    def calculate_charges(self) -> float:
        """
        חישוב חיובים עבור ההורה על פי מספר הקורסים של הילדים שלו.
        """
        total_charges = 0
        for child in self.children:
            total_charges += len(child.courses) * 500  # מספר קורסים כפול תשלום קבוע בעבור כל ילד
        return total_charges

    def make_payment(self, amount: float) -> str:
        """
        מבצע תשלום עבור החיוב של ההורה ומעדכן את סכום החיוב.

        :param amount: סכום התשלום שההורה מבצע.
        :return: הודעה על הצלחת התשלום או כישלונו.
        """
        if amount <= 0:
            return "Amount must be a positive number."

        if amount > self._Charges:
            excess = amount - self._Charges
            self._Charges = 0
            self._payments[self._id] = self._payments.get(self._id, 0) + (amount - excess)  # רישום תשלום
            return f"Payment successful. Overpayment of {excess} detected. Remaining balance is 0."

        self._Charges -= amount
        self._payments[self._id] = self._payments.get(self._id, 0) + amount  # רישום התשלום
        return f"Payment successful. Remaining balance: {self._Charges}."

    def view_charges(self):
        """
        מציגה את סך החיובים הנוכחיים של ההורה.
        """
        if self._Charges > 0:
            print(f"Total charges for {self.name}: {self._Charges}$")
        else:
            print(f"{self.name} has no charges at the moment.")

    def get_course_by_id(self, course_id: int):
        for child in self.children:  # נעבור על כל הילדים של ההורה
            for course in child.requests.queue:  # נבדוק איזה מן הילדים ביקש להירשם לקורס הספציפי הזה
                if course.course_id == course_id:
                    return course
        print("This course is not found, as the child is not on the waiting list.")  # בכך אנו אוכפים את ההרשמה

    def Email_update(self):
        for child in self.children:
            self.email = child.email
            print("Email successfully updated.")


# ======================================================================================================================
# --------------------------------------------------------------------- Parent Menu ------------------------------------
class Parent_Menu:
    def __init__(self, parent: Parent):
        self.parent = parent

    def display_menu(self):
        while True:
            try:
                print("\n===================== 👪 Parent Menu 👪 ==================")
                print("1. Enroll Child in Course 🧑‍🤝‍🧑")
                print("2. Track Children Progress 📊")
                print("3. Payments Management 💰")
                print("4. Exit Parent Menu 🔙")
                print("======================================================")
                choice = input("Enter your choice (1-4): ").strip()

                # בדיקת חוקיות הקלט
                if not choice.isdigit() or not (1 <= int(choice) <= 4):
                    print("❌ Invalid choice. Please enter a number between 1 and 4.")
                    continue

                choice = int(choice)

                if choice == 1:
                    self.enroll_child_in_course()
                elif choice == 2:
                    self.track_children_progress()
                elif choice == 3:
                    self.payments_management()
                elif choice == 4:
                    print("🔙 Exiting Parent Menu...")
                    break

            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}")

    @staticmethod
    def enroll_child_in_course():
        """
        מתודה לרישום ילד לקורס עבור הורה מחובר.
        ההורה יבחר תחילה ילד מהרשימה ולאחר מכן יוכל לבחור קורס מתאים מבין הקורסים המתאימים לגילו.
        """
        try:
            parent_id = current_user["id"]
            parent_name = current_user["name"]

            with connect_database() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # 🔹 1️⃣ שלב 1 - הצגת כל ילדי ההורה
                    cursor.execute("""
                        SELECT s.id, s.name, s.age 
                        FROM Student_Parent sp
                        JOIN Students s ON sp.student_id = s.id
                        WHERE sp.parent_id = %s
                    """, (parent_id,))

                    children = cursor.fetchall()

                    if not children:
                        print(f"❌ No students found for parent '{parent_name}' (ID: {parent_id}).")
                        return

                    print(f"\n👨‍👩‍👦 Students of '{parent_name}' (ID: {parent_id}):")
                    for count, child in enumerate(children, start=1):
                        print(f"  {count}. {child['name']} (ID: {child['id']}), Age: {child['age']}")

                    # 🔹 2️⃣ שלב 2 - בחירת ילד לרישום
                    while True:
                        try:
                            student_id = int(input("\nEnter Student ID to enroll: ").strip())
                            if student_id not in [c["id"] for c in children]:
                                print("❌ Invalid selection. Please choose a student from your list.")
                            else:
                                break
                        except ValueError:
                            print("❌ Invalid input! Please enter a valid Student ID.")

                    student = next(c for c in children if c["id"] == student_id)

                    # 🔹 3️⃣ שלב 3 - שליפת רק קורסים שמתאימים לגיל התלמיד
                    cursor.execute("""
                        SELECT course_id, course_name, course_age, capacity, registered_students
                        FROM Courses
                        WHERE course_age <= %s
                    """, (student["age"],))

                    courses = cursor.fetchall()

                    if not courses:
                        print(f"❌ No courses available for student '{student['name']}' (ID: {student['id']}).")
                        return

                    print(f"\n📚 Available Courses for '{student['name']}' (ID: {student['id']}):")
                    for count, course in enumerate(courses, start=1):
                        status = "✅ Open" if course["registered_students"] < course["capacity"] else "⏳ Full (Waitlist)"
                        print(f"  {count}. {course['course_name']} (ID: {course['course_id']}), Status: {status}")

                    # 🔹 4️⃣ שלב 4 - בחירת קורס לרישום (רק מתוך הרשימה המתאימה)
                    while True:
                        try:
                            course_id = int(input("\nEnter Course ID to enroll in: ").strip())
                            if course_id not in [c["course_id"] for c in courses]:
                                print("❌ Invalid selection. Please choose a course from the list.")
                            else:
                                break
                        except ValueError:
                            print("❌ Invalid input! Please enter a valid Course ID.")

                    course = next(c for c in courses if c["course_id"] == course_id)

                    # 🔹 5️⃣ שלב 5 - בדיקה אם הילד כבר רשום לקורס
                    cursor.execute(
                        "SELECT COUNT(*) FROM Student_Course WHERE student_id = %s AND course_id = %s",
                        (student_id, course_id))
                    if cursor.fetchone()["COUNT(*)"] > 0:
                        print(f"❌ Student '{student['name']}' is already enrolled in '{course['course_name']}'.")
                        return

                    # 🔹 6️⃣ שלב 6 - רישום לקורס או לתור המתנה
                    if course["registered_students"] < course["capacity"]:
                        cursor.execute("""
                            INSERT INTO Student_Course (student_id, course_id, payment_status)
                            VALUES (%s, %s, 'UNPAID')
                        """, (student_id, course_id))

                        cursor.execute("""
                            UPDATE Courses 
                            SET registered_students = registered_students + 1 
                            WHERE course_id = %s
                        """, (course_id,))

                        print(
                            f"✅ Student '{student['name']}' has been successfully enrolled in '{course['course_name']}', but payment is still pending.")

                    else:
                        # חישוב המיקום בתור לפני הוספה
                        cursor.execute("""
                            SELECT COUNT(*) + 1 AS queue_position
                            FROM Waitlists
                            WHERE course_id = %s
                        """, (course_id,))
                        queue_position = cursor.fetchone()["queue_position"]

                        # הוספה לרשימת המתנה
                        cursor.execute("""
                            INSERT INTO Waitlists (course_id, student_id)
                            VALUES (%s, %s)
                        """, (course_id, student_id))

                        print(
                            f"⏳ Student '{student['name']}' has been added to the waitlist for '{course['course_name']}'.")
                        print(f"🔢 Current position in waitlist: {queue_position}")

                    connection.commit()

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")

    @staticmethod
    def track_children_progress():
        """
        מתודה למעקב אחר התקדמות הילדים, כולל ציונים, לוחות זמנים ומיקומם בתורים.
        יוצג להורה דוח מפורט עם המידע.
        """
        try:
            parent_id = current_user["id"]
            parent_name = current_user["name"]

            with connect_database() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # 🔹 1️⃣ שלב 1 - שליפת כל הילדים של ההורה
                    cursor.execute("""
                        SELECT s.id, s.name, s.age 
                        FROM Student_Parent sp
                        JOIN Students s ON sp.student_id = s.id
                        WHERE sp.parent_id = %s
                    """, (parent_id,))

                    children = cursor.fetchall()

                    if not children:
                        print(f"❌ No students found for parent '{parent_name}' (ID: {parent_id}).")
                        return

                    report_lines = [f"\n📊 Child Progress Report for '{parent_name}' (ID: {parent_id})\n",
                                    "=========================================="]

                    # 🔹 2️⃣ שלב 2 - לולאה עבור כל ילד להצגת המידע הרלוונטי
                    for child in children:
                        student_id = child["id"]
                        student_name = child["name"]
                        student_age = child["age"]

                        report_lines.append(
                            f"\n👦 **Student:** {student_name} (ID: {student_id}), Age: {student_age}")

                        # 📊 **Grades & Assignments**
                        cursor.execute("""
                            SELECT c.course_name, sc.grades, sc.assignments
                            FROM Student_Course sc
                            JOIN Courses c ON sc.course_id = c.course_id
                            WHERE sc.student_id = %s
                        """, (student_id,))

                        courses = cursor.fetchall()

                        if courses:
                            report_lines.append("\n📚 **Grades & Assignments:**")
                            for course in courses:
                                grade = course["grades"] if course[
                                                                "grades"] is not None else "No grade recorded"
                                assignments = course["assignments"] if course[
                                    "assignments"] else "No assignments recorded"
                                report_lines.append(f"  - 📖 **Course:** {course['course_name']}")
                                report_lines.append(f"    📊 **Grade:** {grade}")
                                report_lines.append(f"    📝 **Assignments:** {assignments}")
                        else:
                            report_lines.append("\n📚 **Grades & Assignments:** ❌ No enrolled courses.")

                        # 📆 **Schedules**
                        cursor.execute("""
                            SELECT c.course_name, sc.schedule
                            FROM Student_Course sc
                            JOIN Courses c ON sc.course_id = c.course_id
                            WHERE sc.student_id = %s
                        """, (student_id,))

                        schedules = cursor.fetchall()

                        if schedules:
                            report_lines.append("\n📆 **Schedules:**")
                            for schedule in schedules:
                                schedule_details = schedule["schedule"] if schedule[
                                    "schedule"] else "No schedule available"
                                report_lines.append(f"  - 📖 **Course:** {schedule['course_name']}")
                                report_lines.append(f"    🕒 **Schedule:** {schedule_details}")
                        else:
                            report_lines.append("\n📆 **Schedules:** ❌ No schedule found.")

                        # ⏳ **Waitlist Status**
                        cursor.execute("""
                            SELECT c.course_name, w.date,
                                   (SELECT COUNT(*) FROM Waitlists w2 WHERE w2.course_id = w.course_id AND w2.date <= w.date) 
                                   AS queue_position
                            FROM Waitlists w
                            JOIN Courses c ON w.course_id = c.course_id
                            WHERE w.student_id = %s
                            ORDER BY w.date ASC;
                        """, (student_id,))

                        waitlists = cursor.fetchall()

                        if waitlists:
                            report_lines.append("\n⏳ **Waitlist Status:**")
                            for waitlist in waitlists:
                                queue_position = waitlist["queue_position"]
                                date_registered = waitlist["date"]
                                report_lines.append(f"  - 📖 **Course:** {waitlist['course_name']}")
                                report_lines.append(f"    🔢 **Position in Waitlist:** {queue_position}")
                                report_lines.append(f"    📅 **Date Registered:** {date_registered}")
                        else:
                            report_lines.append("\n⏳ **Waitlist Status:** ✅ Not in any waitlist.")

                        report_lines.append("==========================================")

                    # 🔹 3️⃣ שלב 3 - הדפסת הדוח
                    print("\n".join(report_lines))

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")

    @staticmethod
    def payments_management():
        while True:
            print("\n ===================== 💳 Payments Menu 💳 =====================")
            print("1. Pay for a child's course ➕")
            print("2. Check Payments 📄")
            print("3. Exit Payments Menu 🔙")
            print("==============================================================")
            pay_choice = input("Enter your choice (1-3): ").strip()

            # בדיקת חוקיות הקלט
            if not pay_choice.isdigit() or not (1 <= int(pay_choice) <= 3):
                print("❌ Invalid choice. Please enter a number between 1 and 3.")
                continue

            action_choice = int(pay_choice)

            if action_choice == 3:
                print("🔙 Exiting Payments Menu...")
                break

            elif pay_choice == 1:
                """
                מתודה לביצוע תשלום עבור קורס של ילד.
                """
                try:
                    parent_id = current_user["id"]
                    parent_name = current_user["name"]

                    with connect_database() as connection:
                        with connection.cursor(dictionary=True) as cursor:
                            # 🔹 שלב 1️⃣ - שליפת כל הילדים של ההורה
                            cursor.execute("""
                                SELECT s.id, s.name, s.age 
                                FROM Student_Parent sp
                                JOIN Students s ON sp.student_id = s.id
                                WHERE sp.parent_id = %s
                            """, (parent_id,))

                            children = cursor.fetchall()

                            if not children:
                                print(f"❌ No students found for parent '{parent_name}' (ID: {parent_id}).")
                                continue

                            print(f"\n👨‍👩‍👦 Students of '{parent_name}' (ID: {parent_id}):")
                            for count, child in enumerate(children, start=1):
                                print(f"  {count}. {child['name']} (ID: {child['id']}), Age: {child['age']}")

                            # 🔹 שלב 2️⃣ - בחירת ילד לתשלום
                            while True:
                                try:
                                    student_id = int(input("\nEnter Student ID to pay for: ").strip())
                                    if student_id not in [c["id"] for c in children]:
                                        print("❌ Invalid selection. Please choose a student from your list.")
                                    else:
                                        break
                                except ValueError:
                                    print("❌ Invalid input! Please enter a valid Student ID.")

                            student = next(c for c in children if c["id"] == student_id)

                            # 🔹 שלב 3️⃣ - שליפת קורסים שטרם שולמו
                            cursor.execute("""
                                SELECT c.course_id, c.course_name
                                FROM Student_Course sc
                                JOIN Courses c ON sc.course_id = c.course_id
                                WHERE sc.student_id = %s AND sc.payment_status = 'UNPAID'
                            """, (student_id,))

                            courses = cursor.fetchall()

                            if not courses:
                                print(f"✅ No pending payments for '{student['name']}' (ID: {student['id']}).")
                                continue

                            print(f"\n💳 Courses pending payment for '{student['name']}' (ID: {student['id']}):")
                            for count, course in enumerate(courses, start=1):
                                print(f"  {count}. {course['course_name']} (ID: {course['course_id']})")

                            # 🔹 שלב 4️⃣ - בחירת קורס לתשלום
                            while True:
                                try:
                                    course_id = int(input("\nEnter Course ID to pay for: ").strip())
                                    if course_id not in [c["course_id"] for c in courses]:
                                        print("❌ Invalid selection. Please choose a course from the list.")
                                    else:
                                        break
                                except ValueError:
                                    print("❌ Invalid input! Please enter a valid Course ID.")

                            # 🔹 שלב 5️⃣ - ביצוע תשלום
                            cursor.execute("""
                                UPDATE Student_Course
                                SET payment_status = 'PAID'
                                WHERE student_id = %s AND course_id = %s
                            """, (student_id, course_id))

                            cursor.execute("""
                                UPDATE Parents 
                                SET payment = payment + 500
                                WHERE id = %s
                            """, (parent_id,))

                            connection.commit()
                            print(f"💵 Payment completed! '{student['name']}' is now fully enrolled in '{course['course_name']}'.")

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")

            elif pay_choice == 2:
                """
                מתודה להפקת דו"ח תשלומים עבור הורה מחובר.
                הדו"ח כולל את כל הילדים של ההורה, פירוט הקורסים שלהם, מצב התשלום עבור כל קורס, וסכום כולל ששולם/נותר לתשלום.
                """
                try:
                    parent_id = current_user["id"]
                    parent_name = current_user["name"]

                    with connect_database() as connection:
                        with connection.cursor(dictionary=True) as cursor:
                            # 🔹 שליפת רשימת הילדים של ההורה
                            cursor.execute("""
                                SELECT s.id, s.name
                                FROM Student_Parent sp
                                JOIN Students s ON sp.student_id = s.id
                                WHERE sp.parent_id = %s
                            """, (parent_id,))

                            children = cursor.fetchall()

                            if not children:
                                print(f"❌ No students found for parent '{parent_name}' (ID: {parent_id}).")
                                continue

                            report_lines = [f"\n📊 Payment Report for '{parent_name}' (ID: {parent_id})\n", "=" * 50]

                            total_paid = 0
                            total_due = 0

                            for child in children:
                                student_id = child["id"]
                                student_name = child["name"]

                                # 🔹 שליפת רשימת הקורסים של הילד ומצב התשלום
                                cursor.execute("""
                                    SELECT c.course_name, sc.payment_status
                                    FROM Student_Course sc
                                    JOIN Courses c ON sc.course_id = c.course_id
                                    WHERE sc.student_id = %s
                                """, (student_id,))

                                courses = cursor.fetchall()

                                if not courses:
                                    report_lines.append(
                                        f"\n👦 {student_name} (ID: {student_id}) is not enrolled in any courses.")
                                else:
                                    report_lines.append(f"\n👦 {student_name} (ID: {student_id}) - Course Payments:")
                                    for course in courses:
                                        course_name = course["course_name"]
                                        payment_status = course["payment_status"]

                                        if payment_status == "PAID":
                                            total_paid += 1000  # מחיר הקורס
                                            report_lines.append(f"   ✅ {course_name} - Paid")
                                        else:
                                            total_due += 1000  # מחיר הקורס
                                            report_lines.append(f"   ❌ {course_name} - Not Paid (1000$ Due)")

                            report_lines.append("=" * 50)
                            report_lines.append(f"💰 Total Paid: {total_paid}$")
                            report_lines.append(f"💳 Total Due: {total_due}$")

                            print("\n".join(report_lines))

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")