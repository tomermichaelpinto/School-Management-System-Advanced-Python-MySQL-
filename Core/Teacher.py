# ייבוא סיפריות מחלקה
from datetime import datetime

import mysql
from mysql.connector import Error

from System_Menu import current_user
from conf_MySQL import connect_database
from Core.Person import Person
from Core.Course import Course
from Core.Task import Task
from Utils.UrgencyLevel import UrgencyLevel
from Utils.task_status import TaskStatus

# ייבוא סיפריות עזר
from abc import ABC
from typing import Dict, List
import re


class Teacher(Person, ABC):
    # ---------------------------------------------------------------- Summary -----------------------------------------
    """
    מחלקת מורה המייצגת מורה עם שם, מזהה, התמחות, רשימת קורסים, ותכונות נוספות.
    """
    # הודעות שגיאה
    INVALID_COURSE_MSG = "Course must be an instance of the Course class."
    INVALID_EXPERTISE_MSG = "Expertise must be a string."
    INVALID_STUDENT_MSG = "The student name must be of type 'string'."
    COURSE_NOT_FOUND_MSG = "Course not found in the teacher's course list."

    # -------------------------------------------------------------- Constructor ---------------------------------------
    def __init__(self, name: str, id: int, expertise: str, salary: float = 2300):
        super().__init__(name, id)
        self._name = name
        self._id = id
        self._expertise = expertise
        self._salary = salary

        # Dict: קורסים לפי מזהה
        self._courses: Dict[int, Course] = {}
        self._personal_reports: List[Task] = []
        self._teacher_actions: List[str] = []  # מערך לשמירת פעולות המורה במערכת

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
    def expertise(self) -> str:
        return self._expertise

    @expertise.setter
    def expertise(self, val: str):
        if not isinstance(val, str):
            raise ValueError(self.INVALID_EXPERTISE_MSG)
        self._expertise = val

    @property
    def salary(self) -> float:
        return self._salary

    @salary.setter
    def salary(self, val: float):
        if not isinstance(val, (int, float)) or val <= 0:
            raise ValueError("Salary must be a non-negative number.")
        self._salary = val

    @property
    def courses(self) -> Dict[int, Course]:
        return self._courses

    @property
    def teacher_actions(self) -> List[str]:
        return self._teacher_actions

    @property
    def personal_reports(self) -> List[Task]:
        return self._personal_reports

    # ---------------------------------------------------- Basic Functions ---------------------------------------------
    def __str__(self) -> str:
        """
        מחזירה מחרוזת עם פרטי המורה בפורמט קריא.
        """
        courses_details = '\n'.join(
            f"- Course ID: {course_id}, Course Name: {course.course_name}" for course_id, course in
            self._courses.items()) if self._courses else "No courses assigned"
        return (
            f"Teacher Details:\n"
            f"Name: {self.name}\n"
            f"ID: {self.id}\n"
            f"Expertise: {self.expertise}\n"
            f"Courses:\n{courses_details}"
        )

    def __hash__(self):
        """
        יוצר hash המבוסס על תכונות ייחודיות של האובייקט (id, name, expertise).
        """
        return hash((self._id, self._name, self._expertise))

    def __eq__(self, other):
        """
        משווה בין שני אובייקטי Teacher לפי id, name ו-expertise.
        """
        if not isinstance(other, Teacher):
            return False
        return (
                self._id == other.id and
                self._name == other._name and
                self._expertise == other._expertise
        )

    # ------------------------------------------------------ Advanced Functions ----------------------------------------
    def get_course_students(self, course_id: int) -> str:
        """
        מחזירה את רשימת התלמידים הרשומים מקורס מסוים.
        """
        if course_id not in self._courses:
            raise ValueError(self.COURSE_NOT_FOUND_MSG)
        course = self._courses[course_id]
        StudentList = f"The students studying in course {course.course_name} are:\n"
        count = 1
        for student in course.students:
            StudentList += f"{count}) {student}, \n"
        StudentList += f"Total students in the course: {len(course.students)}.\n"
        return StudentList

    def students_Inlay_preview(self):
        """
        מחזירה את רשימת התלמידים הרשומים מכל קורס שהמורה מלמד.
        """
        courses = self._courses.values()
        Report = ""

        for course in courses:
            Report += f"{course.course_name}:\n"
            Report += "-" * len(course.course_name) + "\n"

            if course.students:  # בדיקה אם יש תלמידים בקורס
                student_list = "\n".join([f"{i + 1}. {student}" for i, student in enumerate(course.students)])
                Report += student_list + "\n"
            else:
                Report += "No students enrolled.\n"

            Report += f"Total students in the course: {len(course.students)}.\n\n"

        return Report

    def assign_student(self, course: Course, student: str):
        """
        שיבוץ תלמיד לקורס מסוים.
        """
        if not isinstance(student, str):
            raise ValueError(self.INVALID_STUDENT_MSG)

        # בדיקה אם הקורס נמצא בקורסים של המורה
        if course.course_id not in self._courses:
            raise ValueError(self.COURSE_NOT_FOUND_MSG)

        if student not in course.students:
            if len(course.students) < course.capacity:
                course.students.add(student)
                self.teacher_actions.append(
                    f"Teacher {self.name} assigned student {student} to course {course.course_name}.\n")
                print(f"Student {student} successfully assigned to course {course.course_name}.")

        else:
            self.teacher_actions.append(f"Teacher {self.name} was unable to assign student {student} to course"
                                        f" {course.course_name}.\n")
            print(f"Student {student} is already assigned to course {course.course_name}.")

    def remove_student(self, course: Course, student: str):
        """
        הסרת סטודנט מקורס מסוים.
        """
        if not isinstance(student, str):
            raise ValueError(self.INVALID_STUDENT_MSG)

        # בדיקה אם הקורס נמצא בקורסים של המורה
        if course.course_id not in self._courses:
            raise ValueError(self.COURSE_NOT_FOUND_MSG)

        # בדיקה אם הסטודנט רשום לקורס
        if student.lower() in course.students:
            course.students.remove(student)  # הסרה מרשימת הסטודנטים של הקורס
            self.teacher_actions.append(
                f"Teacher {self.name} removed student {student} from course {course.course_name}.\n")
            print(f"Student {student} has been removed from course {course.course_name}.")

        else:
            self.teacher_actions.append(f"Teacher {self.name} was unable to remove student {student} from course"
                                        f" {course.course_name}.\n")
            print(f"Student {student} is not enrolled in course {course.course_name}.")

    def assign_grade(self, course: Course, student: str, grade: float):
        """
        הזנת ציון לתלמיד בקורס מסוים.
        """
        if not (0 <= grade <= 100):
            print("Error: Grade must be between 0 and 100.")
        if not isinstance(student, str):
            raise ValueError(self.INVALID_STUDENT_MSG)

        # בדיקה אם הקורס קיים ברשימת הקורסים של המורה
        if course.course_id not in self._courses:
            print(f"Error: The course '{course.course_name}' (ID: {course.course_id}) is not assigned to this teacher.")
            return

        # בדיקה אם הסטודנט רשום לקורס
        if student not in course.students:
            print(
                f"Error: Student '{student}'"
                f" is not enrolled in the course '{course.course_name}'.")
            return

        course.grades[student] = grade
        print(f"Grade {grade} assigned to student {student} for course {course.course_name}.")

    def Problem_Reports(self, name: str, description: str, status: TaskStatus = None, urgency: UrgencyLevel = None,
                        additional_info: str = None):
        """
        דיווחי בעיות תחזוקה בכיתה.

        :param name: שם המשימה (לדוגמה: "תיקון מזגן").
        :param description: תיאור הבעיה (לדוגמה: "התקלה במערכת הקירור בקומה 2").
        :param status: סטטוס המשימה (TaskStatus), ברירת מחדל None.
        :param urgency: רמת הדחיפות (Low, Medium, High) מסוג UrgencyLevel, ברירת מחדל None.
        :param additional_info: מידע נוסף רלוונטי (אופציונלי).
        """
        try:
            # יצירת אובייקט משימה עם פרטי הדיווח
            task = Task(
                name=name,
                description=f"{description}\n, Additional Info: {additional_info if additional_info else 'None'}",
                status=status if status else TaskStatus.PENDING,  # אם לא נמסר סטטוס, ברירת המחדל היא PENDING
                urgency=urgency if urgency else UrgencyLevel.MEDIUM,  # אם לא נמסרה דחיפות, ברירת המחדל היא Medium
                reporter=self.name,
                reporter_id=self.id
            )

            # הוספת הדיווח לרשימת הדיווחים האישיים
            self.personal_reports.append(task)
            print("The report was successfully sent to the manager.")

            try:
                with connect_database() as connection:
                    with connection.cursor() as cursor:
                        # הוספת המשימה לטבלה
                        cursor.execute("""
                            INSERT INTO Tasks (id, name, description, reporter_id)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            task.task_id, task.name, task.description, task.reporter_id))
                        connection.commit()

                        print("The problem report was successfully submitted.")

            except Error as e:
                print(f"An error occurred while submitting the problem report: {e}")

        except Exception as e:
            print(f"Failed to send the report: {str(e)}")

    def Viewing_Student_Performance(self, student: str, course: Course):
        """
        פונקציה שמחזירה את ביצועי התלמיד ולוחות הזמן שלו.
        """
        if not isinstance(student, str):
            raise ValueError(self.INVALID_STUDENT_MSG)

        if student not in course.students:  # בדיקה אם התלמיד רשום לקורסים
            print(f"Student {student} is not enrolled in any courses.")
            return

        for stu in course.students:
            if stu == student:
                print(f"Student: {stu}")
                print(f"Course: {course.course_name}")
                print(f"Grade: {course.grades[stu]}")
                print(f"The student's schedule is: {course.personal_schedules[stu]}")
                print(f"The student's tasks are: {course.assignments[stu]}")

                """
                פונקציה שמחזירה את ביצועי התלמיד ולוחות הזמן שלו ממסד הנתונים.
                :param student_name: שם התלמיד.
                :param course_name: שם הקורס.
                """
                try:
                    with connect_database() as connection:
                        with connection.cursor() as cursor:
                            # בדיקת הרשמת התלמיד לקורס
                            cursor.execute("""
                                SELECT s.name AS student_name, c.course_name, sc.grades, sc.schedule, sc.assignments
                                FROM Students s
                                JOIN Student_Course sc ON s.id = sc.student_id
                                JOIN Courses c ON sc.course_id = c.course_id
                                WHERE s.name = %s AND c.course_name = %s
                            """, (student, course.course_name))

                            student_performance = cursor.fetchone()

                            if not student_performance:
                                print(f"Student {student} is not enrolled in the course {course.course_name}.")
                                return

                            # הצגת ביצועי התלמיד
                            print(f"Student: {student_performance[0]}")
                            print(f"Course: {student_performance[1]}")
                            print(f"Grade: {student_performance[2]}")
                            print(f"The student's schedule is: {student_performance[3]}")
                            print(f"The student's tasks are: {student_performance[4]}")

                except mysql.connector.Error as e:
                    print(f"An error occurred while retrieving student performance: {e}")

                return


# ======================================================================================================================
# ----------------------------------------------------------------- Menu Teacher ---------------------------------------
class Teacher_Menu:
    def __init__(self, teacher: Teacher):
        self.teacher = teacher  # מאתחל את אובייקט המורה

    def display_menu(self):
        while True:
            try:
                # הצגת תפריט המורה
                print("\n================== 👩‍🏫 Teacher Menu 👩‍🏫 ==================")
                print("1. View Students in Course 👨‍🎓")
                print("2. Assign Grade to Student 📝")
                print("3. Report a Classroom Issue ⚠️")
                print("4. View All Students' Performance 📊")
                print("5. Assign Course Assignment 📌")
                print("6. Exit Teacher Menu 🔙")
                print("======================================================")
                choice = input("Please choose an option (1-6): ").strip()

                # בדיקת חוקיות הקלט
                if not choice.isdigit() or not (1 <= int(choice) <= 6):
                    print("❌ Invalid choice. Please enter a number between 1 and 6.")
                    continue

                choice = int(choice)

                if choice == 1:
                    self.view_students_course()
                elif choice == 2:
                    self.assign_grade_student()
                elif choice == 3:
                    self.report_classroom_issue()
                elif choice == 4:
                    self.view_students_performance()
                elif choice == 5:
                    self.assign_course_assignment()
                elif choice == 6:
                    print("🔙 Exiting Teacher Menu...")
                    break

            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}")

    @staticmethod
    def view_students_course():
        """ מציג רשימת התלמידים בקורסים של המורה המחובר בלבד. """

        try:
            teacher_id = current_user["id"]
            teacher_name = current_user["name"]

            with connect_database() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # שליפת רשימת הקורסים שהמורה מלמד
                    cursor.execute("""
                        SELECT course_id, course_name 
                        FROM Courses 
                        WHERE teacher_id = %s
                    """, (teacher_id,))

                    teacher_courses = cursor.fetchall()

                    if not teacher_courses:
                        print(f"❌ No courses found for {teacher_name} (ID: {teacher_id}).")
                        return

                    while True:
                        # הצגת רשימת הקורסים לבחירה
                        print(f"\n📚 Courses taught by {teacher_name} (ID: {teacher_id}):")
                        for count, course in enumerate(teacher_courses, start=1):
                            print(f"  {count}. {course['course_name']} (Course ID: {course['course_id']})")

                        print("  0. 🔙 Return to Teacher Menu.")

                        # בחירת קורס מתוך הרשימה
                        try:
                            course_id = int(input("\nEnter Course ID to view students (or 0 to exit): "))
                            if course_id == 0:
                                print("🔙 Returning to Teacher Menu...")
                                break
                            elif course_id not in [c["course_id"] for c in teacher_courses]:
                                print("❌ Invalid selection. Please choose a course from the list.")
                                continue
                        except ValueError:
                            print("❌ Invalid input! Please enter a valid integer for Course ID.")
                            continue

                        # שליפת שמות התלמידים הרשומים בקורס
                        cursor.execute("""
                            SELECT Students.name
                            FROM Student_Course
                            JOIN Students ON Student_Course.student_id = Students.id
                            WHERE Student_Course.course_id = %s
                        """, (course_id,))

                        students = cursor.fetchall()

                        course_name = next(c["course_name"] for c in teacher_courses if c["course_id"] == course_id)

                        if not students:
                            print(f"✅ No students are enrolled in '{course_name}' (ID {course_id}).")
                        else:
                            print(f"\n📚 The students enrolled in '{course_name}' (Course ID: {course_id}) are:")
                            for count, student in enumerate(students, start=1):
                                print(f"  {count}. {student[0]}")
                            print(f"📊 Total students in the course: {len(students)}.")

        except mysql.connector.Error as e:
            print(f"❌ An error occurred while fetching students from the course: {e}")

    @staticmethod
    def assign_grade_student():
        """ פונקציה להזנת ציון לתלמיד – המורה בוחר קורס מהרשימה ואז תלמיד מהרשימה """

        try:
            teacher_id = current_user["id"]
            teacher_name = current_user["name"]

            with connect_database() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # שליפת רשימת הקורסים שהמורה מלמד
                    cursor.execute("""
                        SELECT course_id, course_name 
                        FROM Courses 
                        WHERE teacher_id = %s
                    """, (teacher_id,))

                    teacher_courses = cursor.fetchall()

                    if not teacher_courses:
                        print(f"❌ No courses found for {teacher_name} (ID: {teacher_id}).")
                        return

                    # הצגת רשימת הקורסים לבחירה
                    print(f"\n📚 Courses taught by {teacher_name} (ID: {teacher_id}):")
                    for count, course in enumerate(teacher_courses, start=1):
                        print(f"  {count}. {course['course_name']} (Course ID: {course['course_id']})")

                    # בחירת קורס מתוך הרשימה
                    while True:
                        try:
                            course_id = int(input("\nEnter Course ID to assign a grade: "))
                            if course_id not in [c["course_id"] for c in teacher_courses]:
                                print("❌ Invalid selection. Please choose a course from the list.")
                            else:
                                break
                        except ValueError:
                            print("❌ Invalid input! Please enter a valid integer for Course ID.")

                    course_name = next(c["course_name"] for c in teacher_courses if c["course_id"] == course_id)

                    while True:  # לולאת הזנת ציונים
                        # שליפת רשימת התלמידים הרשומים בקורס
                        cursor.execute("""
                            SELECT s.id AS student_id, s.name AS student_name
                            FROM Student_Course sc
                            JOIN Students s ON sc.student_id = s.id
                            WHERE sc.course_id = %s
                        """, (course_id,))

                        students = cursor.fetchall()

                        if not students:
                            print(f"✅ No students are enrolled in '{course_name}' (Course ID: {course_id}).")
                            return

                        # הצגת רשימת התלמידים לבחירה
                        print(f"\n📖 Students enrolled in '{course_name}' (Course ID: {course_id}):")
                        for count, student in enumerate(students, start=1):
                            print(f"  {count}. {student['student_name']} (Student ID: {student['student_id']})")

                        # בחירת תלמיד מתוך הרשימה
                        while True:
                            try:
                                student_id = int(input("\nEnter Student ID to assign a grade: "))
                                if student_id not in [s["student_id"] for s in students]:
                                    print("❌ Invalid selection. Please choose a student from the list.")
                                else:
                                    break
                            except ValueError:
                                print("❌ Invalid input! Please enter a valid integer for Student ID.")

                        student_name = next(s["student_name"] for s in students if s["student_id"] == student_id)

                        # קלט ציון
                        while True:
                            try:
                                grade = float(input(f"Enter grade for {student_name}: "))
                                if grade < 0 or grade > 100:
                                    print("❌ Grade must be between 0 and 100. Please try again.")
                                else:
                                    break
                            except ValueError:
                                print("❌ Invalid input! Please enter a valid grade between 0 and 100.")

                        # בדיקה אם לסטודנט כבר יש ציון בקורס
                        cursor.execute("""
                            SELECT grades FROM Student_Course
                            WHERE student_id = %s AND course_id = %s
                        """, (student_id, course_id))

                        existing_grade = cursor.fetchone()

                        if existing_grade and existing_grade["grades"] is not None:
                            # עדכון ציון קיים
                            cursor.execute("""
                                UPDATE Student_Course
                                SET grades = %s
                                WHERE student_id = %s AND course_id = %s
                            """, (grade, student_id, course_id))
                            print(
                                f"🔄 Grade updated to {grade} for {student_name} in '{course_name}' (ID: {course_id}).")
                        else:
                            # הוספת ציון חדש
                            cursor.execute("""
                                INSERT INTO Student_Course (student_id, course_id, grades)
                                VALUES (%s, %s, %s)
                            """, (student_id, course_id, grade))
                            print(f"✅ Grade {grade} assigned to {student_name} in '{course_name}' (ID: {course_id}).")

                        connection.commit()

                        # לשאול את המורה אם להמשיך להזין ציונים
                        more_grades = input(
                            "\nDo you want to assign another grade in this course? (yes/no): ").strip().lower()
                        if more_grades != "yes":
                            break

        except mysql.connector.Error as e:
            print(f"❌ An error occurred while assigning grade: {e}")

    @staticmethod
    def report_classroom_issue():
        """
        פונקציה לדיווח על תקלה בכיתה.
        התקלה תירשם כמשימה (Task) בטבלת 'Tasks' עם סטטוס 'PENDING'.
        """
        try:
            # קלט שם המשימה/עבודת התחזוקה (תיאור קצר של התקלה)
            while True:
                task_name = input("Enter Task Name (e.g., 'Broken Projector'): ").strip()
                if not task_name:
                    print("❌ Task name cannot be empty. Please enter a valid task name.")
                else:
                    break

            # קלט מזהה המדווח ובדיקת תקינות
            while True:
                try:
                    reporter_id = int(input("Enter your ID: "))
                    if reporter_id <= 0:
                        print("❌ Reporter ID must be a positive integer. Please try again.")
                    else:
                        break
                except ValueError:
                    print("❌ Invalid input! Please enter a valid integer for Reporter ID.")

            # קלט תיאור התקלה (פירוט מלא)
            while True:
                issue_description = input("Enter Issue Description: ").strip()
                if not issue_description:
                    print("❌ Issue description cannot be empty. Please enter a valid description.")
                else:
                    break

            with connect_database() as connection:
                with connection.cursor() as cursor:
                    # בדיקה אם המדווח קיים במערכת
                    cursor.execute("SELECT COUNT(*) FROM Passwords_Users WHERE id = %s", (reporter_id,))
                    if cursor.fetchone()[0] == 0:
                        print(f"❌ No user found with ID {reporter_id}. Please check and try again.")
                        return

                    # בדיקה אם כבר קיימת תקלה פתוחה שדווחה על ידי משתמש זה
                    cursor.execute("""
                        SELECT COUNT(*) FROM Tasks 
                        WHERE name = %s AND reporter_id = %s AND status IN ('PENDING', 'IN_PROGRESS')
                    """, (task_name, reporter_id))
                    existing_issues = cursor.fetchone()[0]

                    if existing_issues > 0:
                        print(f"❌ You have already reported an open issue for '{task_name}'.")
                        return

                    # הכנסת התקלה לטבלת המשימות עם `MEDIUM` כברירת מחדל
                    cursor.execute("""
                        INSERT INTO Tasks (name, description, status, urgency, reporter_id)
                        VALUES (%s, %s, 'PENDING', 'MEDIUM', %s)
                    """, (task_name, issue_description, reporter_id))

                    connection.commit()
                    print(f"✅ Issue '{task_name}' reported successfully by User ID {reporter_id}.")

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")

    @staticmethod
    def view_students_performance():
        """
        מציגה את ביצועי כל התלמידים בקורס מסוים לפי course_id.
        הנתונים נאספים מטבלת Student_Course.
        """
        try:
            # קלט מזהה קורס ובדיקת תקינות
            while True:
                try:
                    course_id = int(input("Enter Course ID: "))  # קלט מזהה קורס
                    if course_id <= 0:
                        print("❌ Course ID must be a positive integer. Please try again.")
                    else:
                        break
                except ValueError:
                    print("❌ Invalid input! Please enter a valid integer for Course ID.")

            with connect_database() as connection:
                with connection.cursor() as cursor:
                    # בדיקה אם הקורס קיים
                    cursor.execute("SELECT COUNT(*) FROM Courses WHERE course_id = %s", (course_id,))
                    if cursor.fetchone()[0] == 0:
                        print(f"❌ No course found with ID {course_id}.")
                        return

                    # שליפת ביצועי כל התלמידים בקורס (שם ותוצאה)
                    cursor.execute("""
                        SELECT s.id, s.name, sc.grades
                        FROM Student_Course sc
                        JOIN Students s ON sc.student_id = s.id
                        WHERE sc.course_id = %s
                        ORDER BY sc.grades DESC
                    """, (course_id,))

                    students_performance = cursor.fetchall()

                    if not students_performance:
                        print(f"✅ No students found in the course with ID {course_id}.")
                    else:
                        print(f"\n📊 Performance Report for Course ID {course_id}:\n")
                        print("🔹 Student Performance:")
                        for count, (student_id, student_name, grade) in enumerate(students_performance, start=1):
                            grade_display = grade if grade is not None else "No Grade Yet"
                            print(f"  {count}. {student_name} (ID: {student_id}) - Grade: {grade_display}")

                        avg_grade = sum(s[2] for s in students_performance if s[2] is not None) / len(
                            [s for s in students_performance if s[2] is not None]) if any(
                            s[2] is not None for s in students_performance) else "No Grades Yet"

                        print(f"\n📈 Average Course Grade: {avg_grade}")

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")

    @staticmethod
    def assign_course_assignment():
        """
        מאפשרת למורה ליצור מטלה חדשה לכל הסטודנטים הרשומים לקורס שבחרה מתוך רשימת הקורסים שלה.
        כולל תאריך הגשה.
        """
        try:
            teacher_id = current_user["id"]
            teacher_name = current_user["name"]

            with connect_database() as connection:
                with connection.cursor(dictionary=True) as cursor:
                    # 🔹 שליפת כל הקורסים שהמורה מלמדת
                    cursor.execute("""
                        SELECT c.course_id, c.course_name
                        FROM Course_Teacher ct
                        JOIN Courses c ON ct.course_id = c.course_id
                        WHERE ct.teacher_id = %s
                    """, (teacher_id,))

                    courses = cursor.fetchall()

                    if not courses:
                        print(f"❌ No courses found for teacher '{teacher_name}' (ID: {teacher_id}).")
                        return

                    # הצגת רשימת הקורסים של המורה
                    print(f"\n📚 Courses taught by '{teacher_name}' (ID: {teacher_id}):")
                    for count, course in enumerate(courses, start=1):
                        print(f"  {count}. {course['course_name']} (Course ID: {course['course_id']})")

                    # בחירת קורס
                    while True:
                        try:
                            course_id = int(input("\nEnter Course ID to assign an assignment: ").strip())
                            if course_id not in [c["course_id"] for c in courses]:
                                print("❌ Invalid selection. Please choose a course from your list.")
                            else:
                                break
                        except ValueError:
                            print("❌ Invalid input! Please enter a valid Course ID.")

                    course_name = next(c["course_name"] for c in courses if c["course_id"] == course_id)

                    # 🔹 בדיקה האם יש תלמידים בקורס
                    cursor.execute("""
                        SELECT student_id 
                        FROM Student_Course 
                        WHERE course_id = %s
                    """, (course_id,))

                    students = cursor.fetchall()

                    if not students:
                        print(
                            f"❌ No students are enrolled in '{course_name}' (Course ID: {course_id}). Cannot assign an assignment.")
                        return

                    # קלט שם המטלה
                    assignment_name = input("Enter Assignment Name: ").strip()
                    if not assignment_name:
                        print("❌ Assignment name cannot be empty.")
                        return

                    # קלט תאריך הגשה
                    while True:
                        due_date = input("Enter Due Date (YYYY-MM-DD): ").strip()
                        try:
                            datetime.strptime(due_date, "%Y-%m-%d")  # לוודא שהתאריך תקין
                            break
                        except ValueError:
                            print("❌ Invalid date format. Please enter the date in YYYY-MM-DD format.")

                    # הוספת המטלה לכל הסטודנטים הרשומים לקורס
                    for student in students:
                        cursor.execute("""
                            UPDATE Student_Course 
                            SET assignments = CONCAT_WS(', ', IFNULL(assignments, ''), %s)
                            WHERE student_id = %s AND course_id = %s
                        """, (f"{assignment_name} (Due: {due_date})", student["student_id"], course_id))

                    connection.commit()
                    print(
                        f"✅ Assignment '{assignment_name}' has been assigned to all students in '{course_name}' (Due: {due_date}).")

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")
