# ייבוא סיפריות מחלקה
import mysql
from mysql.connector import Error

from System_Menu import current_user
from conf_MySQL import connect_database
from Core.Person import Person
from Core.Course import Course
from Core.Request import Request
from Core.Teacher import Teacher

# ייבוא סיפריות עזר
from abc import ABC
from queue import Queue
from typing import Set, List
import re


class Student(Person, ABC):
    # ---------------------------------------------------------------- Summary -----------------------------------------
    """
    מחלקת תלמיד המייצגת תלמיד עם שם, מזהה, גיל, אימייל הורה, וקורס מועדף.
    """
    # הודעות שגיאה
    INVALID_AGE_MSG = "Age must be a positive integer."
    INVALID_PREFERRED_COURSE_MSG = "Preferred course must be a string."

    # -------------------------------------------------------------- Constructor ---------------------------------------
    def __init__(self, name: str, id: int, age: int, parent_email: str, preferred_course: str):
        super().__init__(name, id)
        self._name = name
        self._id = id
        self._age = age
        self._parent_email = parent_email
        self._preferred_course = preferred_course

        # List & Set
        self._courses: Set[Course] = set()  # קורסים שהתלמיד לומד
        self._requests: Queue[Request] = Queue()  # רשימת הקורסים שהתלמיד ביקש להירשם אליהם
        self._student_actions: List[str] = []  # מערך לשמירת פעולות התלמיד במערכת

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
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError(self.INVALID_AGE_MSG)

        self._age = value

    @property
    def email(self) -> str:
        return self._parent_email

    @email.setter
    def email(self, value: str):
        """
        מאמתת ומגדירה את כתובת האימייל.
        - חייבת להיות מחרוזת בפורמט אימייל תקין.
        """
        if not isinstance(value, str) or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise ValueError("Invalid email format. Please provide a valid email address.")

        self._parent_email = value

    @property
    def preferred_course(self) -> str:
        return self._preferred_course

    @preferred_course.setter
    def preferred_course(self, value: str):
        if not isinstance(value, str):
            raise ValueError(self.INVALID_PREFERRED_COURSE_MSG)
        self._preferred_course = value

    @property
    def courses(self) -> Set[Course]:
        return self._courses

    @property
    def requests(self) -> Queue:
        return self._requests

    @property
    def student_actions(self) -> List[str]:
        return self._student_actions

    # ---------------------------------------------------- Basic Functions ---------------------------------------------
    def __str__(self) -> str:
        """
        מחזירה מחרוזת עם פרטי התלמיד בפורמט קריא.
        """
        return (
            f"Student Details:\n"
            f"Name: {self._name}\n"
            f"ID: {self._id}\n"
            f"Age: {self._age}\n"
            f"Parent Email: {self._parent_email}\n"
            f"Preferred Course: {self._preferred_course}"
        )

    def __eq__(self, other) -> bool:
        """
        משווה בין שני אובייקטים של תלמיד על פי כל התכונות.
        """
        if not isinstance(other, Student):
            return False
        return (
                self._name == other._name and
                self._id == other._id and
                self._age == other._age and
                self._parent_email == other._parent_email and
                self._preferred_course == other._preferred_course
        )

    def __hash__(self) -> int:
        """
        יוצר hash עבור האובייקט על בסיס כל התכונות.
        """
        return hash((
            self._name,
            self._id,
            self._age,
            self._parent_email,
            self._preferred_course
        ))

    # ------------------------------------------------------ Advanced Functions ----------------------------------------
    def view_personal_assignments_and_grades(self) -> str:
        """
        מציגה לוח זמנים וציונים בקורסים שהתלמיד רשום בהם.
        """
        if not self.courses:
            return f"{self.name} is not registered in any courses."

        report = [f"Personal Schedule for {self.name} (ID: {self.id}):",
                  f"-------------------------------------------------"]
        for course in self.courses:
            assignments = course.assignments.get(self.name, "No assignments assigned")
            grades = course.grades.get(self.name, "No grades available")
            schedules = course.personal_schedules.get(self.name, "No schedules available")
            report.append(f"Course: {course.course_name}")
            report.append(f"  Assignments: {assignments}")
            report.append(f"  Grades: {grades}")
            report.append(f"  Schedules: {schedules}")
            report.append("================================")  # שורה ריקה בין קורסים להפרדה

        return "\n".join(report)

    def receive_registration_updates(self) -> str:
        """
        מחזיר עדכונים על מצב הרישום לקורסים והסטטוס עבור כל קורס שהתלמיד ביקש להירשם אליו.
        """
        Report = f"Registration Status for {self._name} (ID: {self._id}):\n"

        # המרת התור לרשימה כדי לעבור על הבקשות
        requests_list = list(self._requests.queue)

        # לולאה על הקורסים בתור הבקשות
        for course in requests_list:
            # בודק את המיקום של התלמיד ברשימת ההמתנה בקורס
            if self in course.Requests.queue:
                waitlist_position = list(course.Requests.queue).index(self) + 1
                Report += f"Course: {course.course_name}, Waitlist Position: {waitlist_position}\n"
            else:
                Report += f"Course: {course.course_name}, Status: Not on waitlist\n"

        return Report

    # פונקציה להסרת בקשה מהתור
    def remove_request(self, request: Request, course: Course):
        """
        מסיר בקשה מהתור של הסטודנט ומכל התורים של הישויות הקשורות.
        לשימוש למחלקת המנהל ולמחלקת הילד, קרי הסטודנט.
        """
        queue_length = self._requests.qsize()
        for _ in range(queue_length):
            current_request = self._requests.get()

            # אם הבקשה תואמת את הבקשה המבוקשת, נמחק אותה
            if current_request == request:

                self.student_actions.append(
                    f"Student {self.name} has canceled the waitlist for course {course.course_name}.")

                # קריאה לפונקציה של הקורס להסרת הבקשה
                course.remove_registration_request(current_request)

                return f"Request for student {self._name} to course {current_request.course_id} has been removed from wait-list."

            else:
                # אם הבקשה לא מתאימה, נחזיר אותה לתור
                self.student_actions.append(
                    f"Student {self.name} has been moved back to the waitlist for course {course.course_name}.")

    # פונקציה להצגת לוח הזמנים
    def display_personal_schedule(self, course: Course) -> None:
        """
        מציגה את לוח הזמנים האישי בצורה מסודרת עם מספר רץ.
        """
        # שימוש ב-get כדי למנוע KeyError
        personal_schedule = course.personal_schedules.get(self.name, [])

        if not personal_schedule:
            print("The personal schedule is currently empty.")
        else:
            print(f"Personal Schedule for {self._name} (ID: {self._id}):")
            for index, item in enumerate(personal_schedule, start=1):  # הוספת מספר רץ
                print(f"{index}. {item}")

    def register_for_course(self, course: Course, teacher: Teacher) -> str:  # מקבל קורס ומורה
        """
        מנסה להירשם לקורס. אם הקורס מתאים לגיל התלמיד ויש מקום, התלמיד יירשם.
        אחרת, ייכנס לרשימת המתנה.
        בנוסף, יש לוודא שהמורה מתמחה בקורס.
        """
        if not isinstance(course, Course):           # בדיקת קלט
            raise ValueError("Course must be an instance of the Course class.")

        if not isinstance(teacher, Teacher):         # בדיקת קלט
            raise ValueError("Teacher must be an instance of the Teacher class.")

        if self.name in course.students:             # נבדוק האם הסטודנט כבר לומד בקורס
            return f"The Student is already in the Course."

        if course.course_age != self.age:
            return f"{self.name} does not meet the age requirements for {course.course_name}."

        if teacher.expertise not in course.course_name:
            return f"Teacher {teacher.name} is not qualified to teach {course.course_name}."

        # רישום או הכנסה לרשימת המתנה
        if course.registered_students < course.capacity:    # אם מספר הרשומים קטן ממספר ההגבלה

            course.students.add(self.name)
            course.registered_students += 1                 # עדכון כמות רשומים בקורס

            self.student_actions.append(f"Student {self.name} has registered for course {course.course_name}.")

            return f"{self.name} successfully registered for {course.course_name}."

        else:
            student_request = Request(course_id=course.course_id,
                                      student_id=self.id,
                                      )
            course.Requests.put(student_request)
            self.student_actions.append(f"Student {self.name} has been added to the waitlist for course {course.course_name}.")
            return f"{course.course_name} is full. {self.name} added to the waitlist."

    def Search_Teacher_By_name(self, teacher_name: str):
        for course in self.courses:  # נעבור על רשימת הקורסים בהם לומד התלמיד
            for teacher in course.teachers:
                if teacher == teacher_name:
                    Teacher_name = teacher
                    Teacher_id = course.teacher_id
                    Teacher_expertise = course.course_name
                    return Teacher(Teacher_name, Teacher_id, Teacher_expertise)
        return "Teacher not found, please contact the teacher or administrator to register."


# ======================================================================================================================
# ----------------------------------------------------------------- Menu Student ---------------------------------------
class Student_Menu:
    def __init__(self, student: Student):
        self.student = student

    def display_menu(self):
        while True:
            try:
                print("\n================ 👨‍🎓 Student Menu 👨‍🎓 ================")
                print("1. View Personal Schedules 📅")
                print("2. View Personal Grades and Assignments 📊")
                print("3. View Waitlists Status ⏳")
                print("4. Exit Student Menu 🔙")
                print("======================================================")
                choice = input("Enter your choice (1-7): ").strip()

                # בדיקת חוקיות הקלט
                if not choice.isdigit() or not (1 <= int(choice) <= 5):
                    print("❌ Invalid choice. Please enter a number between 1 and 5.")
                    continue

                choice = int(choice)

                if choice == 1:
                    self.view_personal_schedules()
                elif choice == 2:
                    self.view_personal_grades_assignments()
                elif choice == 3:
                    self.view_waitlist_status()
                elif choice == 4:
                    print("🔙 Exiting Student Menu...")
                    break

            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}")

    @staticmethod
    def view_personal_schedules():
        """
        מציג את לוח הזמנים האישי של הסטודנט, כאשר הוא יכול לבחור באילו קורסים לצפות.
        """
        try:
            student_id = current_user["id"]
            student_name = current_user["name"]

            with connect_database() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # שליפת רשימת הקורסים בהם הסטודנט רשום
                    cursor.execute("""
                        SELECT c.course_id, c.course_name
                        FROM Student_Course sc
                        JOIN Courses c ON sc.course_id = c.course_id
                        WHERE sc.student_id = %s
                    """, (student_id,))

                    student_courses = cursor.fetchall()

                    if not student_courses:
                        print(f"✅ No courses found for {student_name} (ID: {student_id}).")
                        return

                    # הצגת רשימת הקורסים לבחירה
                    print(f"\n📚 Courses enrolled by {student_name} (ID: {student_id}):")
                    for count, course in enumerate(student_courses, start=1):
                        print(f"  {count}. {course['course_name']} (Course ID: {course['course_id']})")

                    selected_courses = []
                    while True:
                        try:
                            course_id = int(input("\nEnter Course ID to view schedule (or 0 to finish): "))
                            if course_id == 0:
                                break
                            elif course_id not in [c["course_id"] for c in student_courses]:
                                print("❌ Invalid selection. Please choose a course from the list.")
                            else:
                                selected_courses.append(course_id)
                        except ValueError:
                            print("❌ Invalid input! Please enter a valid integer for Course ID.")

                    if not selected_courses:
                        print("❌ No courses selected. 🔙 Returning to Student Menu...")
                        return

                    # שליפת לוחות הזמנים עבור הקורסים שנבחרו
                    cursor.execute("""
                        SELECT c.course_name, sc.schedule
                        FROM Student_Course sc
                        JOIN Courses c ON sc.course_id = c.course_id
                        WHERE sc.student_id = %s AND sc.course_id IN (%s)
                    """ % (student_id, ",".join(map(str, selected_courses))))  # בניית שאילתת IN בצורה בטוחה

                    schedules = cursor.fetchall()

                    if not schedules:
                        print(f"✅ No schedules available for the selected courses.")
                    else:
                        print(f"\n📆 Personal Schedule for {student_name} (ID: {student_id}):")
                        for count, entry in enumerate(schedules, start=1):
                            course_name = entry["course_name"]
                            schedule = entry["schedule"] if entry["schedule"] else "No schedule available"
                            print(f"  {count}. 📖 Course: {course_name}\n     🕒 Schedule: {schedule}")

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")

    @staticmethod
    def view_personal_grades_assignments():
        """
        מציג את הציונים והמשימות של הסטודנט המחובר, עם אפשרות לבחור קורס ספציפי.
        """
        try:
            student_id = current_user["id"]
            student_name = current_user["name"]

            with connect_database() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # שליפת רשימת הקורסים בהם הסטודנט רשום
                    cursor.execute("""
                        SELECT c.course_id, c.course_name
                        FROM Student_Course sc
                        JOIN Courses c ON sc.course_id = c.course_id
                        WHERE sc.student_id = %s
                    """, (student_id,))

                    student_courses = cursor.fetchall()

                    if not student_courses:
                        print(f"✅ No courses found for {student_name} (ID: {student_id}).")
                        return

                    # הצגת רשימת הקורסים לבחירה
                    print(f"\n📚 Courses enrolled by {student_name} (ID: {student_id}):")
                    for count, course in enumerate(student_courses, start=1):
                        print(f"  {count}. {course['course_name']} (Course ID: {course['course_id']})")

                    selected_courses = []
                    while True:
                        try:
                            course_id = int(input("\nEnter Course ID to view grades & assignments (or 0 to finish): "))
                            if course_id == 0:
                                break
                            elif course_id not in [c["course_id"] for c in student_courses]:
                                print("❌ Invalid selection. Please choose a course from the list.")
                            else:
                                selected_courses.append(course_id)
                        except ValueError:
                            print("❌ Invalid input! Please enter a valid integer for Course ID.")

                    if not selected_courses:
                        print("❌ No courses selected. 🔙 Returning to Student Menu...")
                        return

                    # שליפת ציונים ומשימות לקורסים שנבחרו
                    cursor.execute("""
                        SELECT c.course_name, sc.grades, sc.assignments
                        FROM Student_Course sc
                        JOIN Courses c ON sc.course_id = c.course_id
                        WHERE sc.student_id = %s AND sc.course_id IN (%s)
                    """ % (student_id, ",".join(map(str, selected_courses))))  # בניית שאילתת IN בצורה בטוחה

                    courses = cursor.fetchall()

                    if not courses:
                        print(f"✅ No grade or assignment records found for the selected courses.")
                    else:
                        print(f"\n📚 Grades & Assignments for {student_name} (ID: {student_id}):")
                        for count, course in enumerate(courses, start=1):
                            course_name = course["course_name"]
                            grade = course["grades"] if course["grades"] is not None else "No grade recorded"
                            assignments = course["assignments"] if course["assignments"] else "No assignments recorded"

                            print(f"  {count}. 📖 Course: {course_name}")
                            print(f"     📊 Grade: {grade}")
                            print(f"     📝 Assignments: {assignments}")

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")

    @staticmethod
    def view_waitlist_status():
        """
        מציג את מצב הרישום של הסטודנט המחובר לתורים (Waitlists) לפי קורסים נבחרים.
        """
        try:
            student_id = current_user["id"]
            student_name = current_user["name"]

            with connect_database() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # שליפת רשימת הקורסים שבהם הסטודנט מחכה בתור
                    cursor.execute("""
                        SELECT DISTINCT c.course_id, c.course_name
                        FROM Waitlists w
                        JOIN Courses c ON w.course_id = c.course_id
                        WHERE w.student_id = %s
                        ORDER BY w.course_id;
                    """, (student_id,))

                    waitlist_courses = cursor.fetchall()

                    if not waitlist_courses:
                        print(f"✅ {student_name} (ID: {student_id}) is not on any waitlist.")
                        return

                    # הצגת הקורסים שבהם הסטודנט מחכה בתור
                    print(f"\n⏳ Courses with Waitlist for {student_name} (ID: {student_id}):")
                    for count, course in enumerate(waitlist_courses, start=1):
                        print(f"  {count}. {course['course_name']} (Course ID: {course['course_id']})")

                    selected_courses = []
                    while True:
                        try:
                            course_id = int(input("\nEnter Course ID to view waitlist status (or 0 to finish): "))
                            if course_id == 0:
                                break
                            elif course_id not in [c["course_id"] for c in waitlist_courses]:
                                print("❌ Invalid selection. Please choose a course from the list.")
                            else:
                                selected_courses.append(course_id)
                        except ValueError:
                            print("❌ Invalid input! Please enter a valid integer for Course ID.")

                    if not selected_courses:
                        print("❌ No courses selected. 🔙 Returning to Student Menu.")
                        return

                    # שליפת רשימת התורים לקורסים שנבחרו
                    cursor.execute("""
                        SELECT c.course_name, w.date,
                               (SELECT COUNT(*) FROM Waitlists w2 WHERE w2.course_id = w.course_id AND w2.date <= w.date) 
                               AS queue_position
                        FROM Waitlists w
                        JOIN Courses c ON w.course_id = c.course_id
                        WHERE w.student_id = %s AND w.course_id IN (%s)
                        ORDER BY w.date ASC;
                    """ % (student_id, ",".join(map(str, selected_courses))))  # בניית שאילתת IN בצורה בטוחה

                    waitlists = cursor.fetchall()

                    if not waitlists:
                        print(f"✅ No waitlist records found for the selected courses.")
                    else:
                        print(f"\n⏳ Waitlist Status for {student_name} (ID: {student_id}):")
                        for count, waitlist in enumerate(waitlists, start=1):
                            course_name = waitlist["course_name"]
                            queue_position = waitlist["queue_position"]
                            date_registered = waitlist["date"]

                            print(f"  {count}. 📖 Course: {course_name}")
                            print(f"     🔢 Position in Waitlist: {queue_position}")
                            print(f"     📅 Date Registered: {date_registered}")

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")
