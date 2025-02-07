# ייבוא סיפריות מחלקה
import mysql
from mysql.connector import Error
from conf_MySQL import connect_database
from Core.Person import Person
from Core.Student import Student
from Core.Teacher import Teacher
from Core.Parent import Parent
from Core.Course import Course
from Core.Task import Task
from Core.Request import Request
from Core.General_Worker import General_Worker
from Utils import task_status

# ייבוא של סיפריות עזר
from abc import ABC
from typing import Dict, List
from collections import deque
import re
import pandas as pd
import os
from queue import Queue


class Manager(Person, ABC):
    # ---------------------------------------------------------------- Summary -----------------------------------------
    """
    מחלקת מנהל היורשת מ- Person ומוסיפה את הפונקציות לניהול תלמידים, מורים, עובדים כלליים, הורים וקורסים.
    למעשה מחלקה זו היא זו שמנהלת את בית הספר
    """

    # -------------------------------------------------------------- Constructor ---------------------------------------

    def __init__(self, name: str, id: int, school_budget: float = 32000):
        super().__init__(name, id)
        self._name = name
        self._id = id
        self._school_budget = school_budget  # תקציב בית הספר

        # List & Dict לאחסון אובייקטים לפי מזהה (ID)
        self._students: Dict[int, Student] = {}  # מערך לאחסון כל התלמידים בבית הספר
        self._teachers: Dict[int, Teacher] = {}  # מערך לאחסון כל המורים בבית הספר
        self._parents: Dict[int, Parent] = {}  # מערך לאחסון כל ההורים שרשמו את ילדיהם לבית הספר
        self._courses: Dict[int, Course] = {}  # מערך לאחסון הקורסים הנלמדים בבית הספר
        self._general_workers: Dict[int, General_Worker] = {}
        self._requests: deque = deque()  # תור לאחסון הבקשות מהמנהל
        self._Maintenance_Problem_Reports: List[Task] = []  # מערך לאחסון הודעות תחזוקה (גם מהמורות וגם מהעובדים הכללים)
        self._Messages: List[str] = []  # מערך לאחסון הודעות המערכת

        self._Popular_courses_opened: List[Course] = []  # מערך לשמירת הקורסים החדשים שנפתחו

    # ------------------------------------------------------- Setters & Getters: Personality ---------------------------
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
    def school_budget(self) -> float:
        return self._school_budget

    @school_budget.setter
    def school_budget(self, val: float):
        if not isinstance(val, (int, float)) or val <= 0:
            raise ValueError("School budget must be a non-negative number.")
        self._school_budget = val

    # ------------------------------------------------------- Setters & Getters: Management ----------------------------
    @property
    def Maintenance_Problem_Reports(self):
        return self._Maintenance_Problem_Reports

    @property
    def Messages(self):
        return self._Messages

    @property
    def requests(self):
        return self._requests

    @property
    def students(self):
        return self._students

    @property
    def teachers(self):
        return self._teachers

    @property
    def parents(self):
        return self._parents

    @property
    def courses(self):
        return self._courses

    @property
    def general_workers(self):
        return self._general_workers

    @property
    def popular_courses_opened(self):
        return self._Popular_courses_opened

    # ------------------------------------------------ Creation functions ----------------------------------------------
    def add_student(self, student: Student):
        if not isinstance(student, Student):
            raise ValueError("Student must be an instance of the Student class.")
        self._students[student.id] = student

    def add_teacher(self, teacher: Teacher):
        if not isinstance(teacher, Teacher):
            raise ValueError("Teacher must be an instance of the Teacher class.")
        self._teachers[teacher.id] = teacher

    def add_worker(self, worker: General_Worker):
        if not isinstance(worker, General_Worker):
            raise ValueError("Worker must be an instance of the General_Worker class.")
        self._general_workers[worker.id] = worker
        worker.manager = self  # מקצה מנהל לעובד

    def add_parent(self, parent: Parent):
        if not isinstance(parent, Parent):
            raise ValueError("Parent must be an instance of the Parent class.")
        self._parents[parent.id] = parent

    def add_course(self, course: Course):
        if not isinstance(course, Course):
            raise ValueError("Course must be an instance of the Course class.")
        self._courses[course.course_id] = course

    def add_request(self, request: Request, stu: Student):  # הוספת בקשה למערך של המנהל
        """
        מוסיף בקשת הרשמה לקורס ומעדכן את כל הישויות הרלוונטיות.
        :param request: אובייקט מסוג Request שמייצג את הבקשה.
        :param stu: אובייקט מסוג Student שמייצג את התלמיד.
        """
        if not isinstance(request, Request):
            raise ValueError("Request must be an instance of the Request class.")
        if not isinstance(stu, Student):
            raise ValueError("Student must be an instance of the Student class.")

        # הוספת הבקשה לרשימת הבקשות של המנהל
        self.requests.append(request)

        # בדיקה אם הקורס קיים והוספת הבקשה לתור ההמתנה שלו
        if request.course_id in self._courses:
            course = self._courses[request.course_id]  # משיכת הקורס הספציפי מתוך רשימת הקורסים הקיימים בבית הספר
            course.Requests.put(request)  # פונקציה בקורס שמוסיפה את הבקשה לתור ההמתנה

            Manager.System_Recommendation(self)  # בדיקה אוטומטית (הפעלת הפונקציה) אם יש צורך בפתיחת קורס

        else:
            raise ValueError(f"Course with ID {request.course_id} not found.")

        # עדכון רשימת הבקשות של התלמיד
        stu.requests.put(request)  # פונקציה בתלמיד שמוסיפה בקשה לתלמיד

        # הודעה על הצלחה
        print(f"Request for student {stu.id} to course {request.course_id} has been added successfully.")

    # --------------------------------------------- Delete functions ---------------------------------------------------
    def remove_student(self, student_id: int):
        if student_id in self._students:
            del self._students[student_id]
        else:
            raise ValueError("Student not found.")

    def remove_teacher(self, teacher_id: int):
        if teacher_id in self._teachers:
            del self._teachers[teacher_id]
        else:
            raise ValueError("Teacher not found.")

    def remove_worker(self, worker_id: int):
        if worker_id in self._general_workers:
            del self._general_workers[worker_id]
        else:
            raise ValueError("Worker not found.")

    def remove_parent(self, parent_id: int):
        if parent_id in self._parents:
            del self._parents[parent_id]
        else:
            raise ValueError("Parent not found.")

    def remove_course(self, course_id: int):
        if course_id in self._courses:
            del self._courses[course_id]
        else:
            raise ValueError("Course not found.")

    # ---------------------------------------------------------- Printing functions ------------------------------------
    def __str__(self) -> str:
        """
        מציגה את פרטי המנהל ואת התכולה הניהולית שלו בצורה קריאה ומסודרת.
        """
        students_str = ', '.join(f"{student.id}: {student.name}" for student in self._students.values())
        teachers_str = ', '.join(f"{teacher.id}: {teacher.name}" for teacher in self._teachers.values())
        parents_str = ', '.join(f"{parent.id}: {parent.name}" for parent in self._parents.values())
        courses_str = ', '.join(f"{course.course_id}: {course.course_name}" for course in self._courses.values())
        workers_str = ', '.join(f"{worker.id}: {worker.name}" for worker in self._general_workers.values())

        # סידור הודעות תחזוקה
        if self._Maintenance_Problem_Reports:
            maintenance_reports_str = '\n'.join(
                f"Task name: {task.name}, Status: {task.status}, Urgency: {task.urgency} "
                f"Reporter: {task.reporter if task.reporter else 'Unknown'}, "
                f"Reporter ID: {task.reporter_id}"
                f"Description: {task.description}"
                for task in self._Maintenance_Problem_Reports)
        else:
            maintenance_reports_str = "No maintenance reports."

        # חישוב כמות ישויות
        num_students = len(self._students)
        num_teachers = len(self._teachers)
        num_parents = len(self._parents)
        num_courses = len(self._courses)
        num_workers = len(self._general_workers)
        num_maintenance_reports = len(self._Maintenance_Problem_Reports)
        num_requests = len(self._requests)

        # בניית המחרוזת עם אימוג'ים
        return (
            f"Manager Details:\n"
            f"Name: {self._name} 👨‍💼\n"
            f"ID: {self._id}\n"
            f"-------------------\n"
            f"Managed Entities:\n"
            f"Students: {students_str if students_str else 'No students'} ({num_students} 🧑‍🎓)\n"
            f"Teachers: {teachers_str if teachers_str else 'No teachers'} ({num_teachers} 👩‍🏫)\n"
            f"Parents: {parents_str if parents_str else 'No parents'} ({num_parents} 👨‍👩‍👧‍👦)\n"
            f"Courses: {courses_str if courses_str else 'No courses'} ({num_courses} 📚)\n"
            f"General Workers: {workers_str if workers_str else 'No workers'} ({num_workers} 👷‍♂️)\n\n"
            f"Maintenance Problem Reports: {num_maintenance_reports} 🛠️\n{maintenance_reports_str}\n"
            f"Pending Requests: {num_requests} 📝 requests in queue."
        )

    def display_students(self):
        return [str(student) for student in self._students.values()]

    def display_teachers(self):
        return [str(teacher) for teacher in self._teachers.values()]

    def display_courses(self):
        return [str(course) for course in self._courses.values()]

    def display_requests(self):
        """
        מציג את הבקשות בתור.
        """
        requests_list = []
        for req in list(self._requests):  # הפיכת התור לרשימה לצורך מעבר
            requests_list.append(f"Student ID: {req.student_id}, Course ID: {req.course_id}")
        return requests_list

    def display_maintenance_reports(self):
        """
        מציגה את כל הודעות התחזוקה של המנהל בצורה קריאה ומסודרת.
        """
        if not self._Maintenance_Problem_Reports:
            print("No maintenance reports.")
            return

        print("Maintenance Problem Reports:")
        for task in self._Maintenance_Problem_Reports:
            print(f"Task name: {task.name}")
            print(f"Status: {task.status}")
            print(f"Urgency level: {task.urgency}")
            print(f"Description: {task.description}")
            print(f"Reporter: {task.reporter} ({task.reporter_id})")
            print("-" * 40)  # מפריד בין משימות

    # ------------------------------------------------------ Advanced Functions ----------------------------------------
    def assign_teacher_to_course(self, teacher_id: int, course_id: int):

        if teacher_id not in self.teachers.keys():  # נבדוק אם במערך המנהל
            raise ValueError("Teacher not found.")

        if course_id not in self.courses.keys():  # נבדוק אם במערך המנהל
            raise ValueError("Course not found.")

        teacher = self.teachers[teacher_id]  # נבצע שליפה אם כן
        course = self.courses[course_id]  # נבצע שליפה אם כן

        # ביצוע הוספות לישויות המעורבות
        teacher.courses[course_id] = course
        course.teachers.add(teacher.name)

    def add_student_to_waitlist(self, request: Request, student: Student):
        """
        מוסיף בקשת הרשמה לקורס הספציפי ומעדכן את כל הישויות הרלוונטיות.
        :param request: אובייקט מסוג Request שמייצג את הבקשה.
        :param student: אובייקט מסוג Student שמייצג את התלמיד.
        """

        if not isinstance(request, Request):  # בדיקת קלט
            raise ValueError("Request must be an instance of the Request class.")

        if not isinstance(student, Student):  # בדיקת קלט
            raise ValueError("Student must be an instance of the Student class.")

        course = self.courses.get(request.course_id)  # משיכת הקורס לפי מספר מזהה מהמילון

        if student.name in course.students:  # נבדוק האם הסטודנט כבר לומד בקורס
            return f"The Student is already in the Course."

        # אם הגענו עד לכאן אז הבקשה היא לגיטימית
        if course:  # אם נמצא הקורס אז נמשיך
            course.Requests.put(request)  # הוספת לרשימת ההמתנה בקורס
            student.requests.put(request)  # הוספת לרשימת ההמתנה בקורס אצל התלמיד

            try:
                self.System_Recommendation()  # בדיקה אוטומטית (הפעלת הפונקציה) אם יש צורך בפתיחת קורס
            except Exception as e:
                print(f"Warning: System_Recommendation failed with error: {e}")

            # הודעה על הצלחה
            return f"Request for student {student.id} to course {request.course_id} has been added successfully."
        else:
            raise ValueError(f"Course with ID {request.course_id} not found.")

    def remove_student_from_waitlist(self, request: Request, student: Student):
        """
        מסיר בקשה מהתור של המנהל ומשאר התורים הרלוונטים.
        """
        if len(self._requests) == 0:
            raise ValueError("No requests to remove.")

        # משתנה למעקב אחר אם הבקשה נמצאה
        found = False
        queue_length = len(self._requests)  # מספר הבקשות בתור

        for _ in range(queue_length):
            removed_request = self._requests.popleft()  # מקבלים מהלולאה כל בקשה ובוחנים אותה

            # אם הבקשה תואמת את פרטי הסטודנט והקורס
            if removed_request == request and removed_request.student_id == student.id:
                found = True
                # הסרת הבקשה מהתור של המנהל ושל כל הישויות הקשורות
                print(
                    f"Request for student {removed_request.student_id} to course {removed_request.course_id}"
                    f"has been removed.")

                course = self._courses[request.course_id]  # איתור הפרויקט לצורך שרשרת הסרה
                student.remove_request(request, course)  # הסרת הבקשה גם מהתור של הסטודנט

                Manager.process_next_request(self)  # קידום התור באופן אוטומטי (הפעלת הפונקציה לקידום)

            else:
                # החזרת הבקשה לתור אם היא לא תואמת
                self._requests.append(removed_request)

        if not found:
            raise ValueError(f"No matching request for student {student.id} found.")

    def add_task_to_worker(self, worker_id: int, task: Task):
        """
        מוסיף משימה לעובד כללי ומעדכן את הסטטוס שלה.
        :param worker_id: מזהה העובד הכללי
        :param task: אובייקט המשימה
        """
        if worker_id not in self._general_workers:
            raise ValueError("Worker not found.")

        worker = self._general_workers[worker_id]  # משיכת העובד הכללי מתוך כלל העובדים הכללים
        if not isinstance(task, Task):
            raise ValueError("Task must be an instance of the Task class.")

        # Assign task to worker
        worker.add_task(task)

        """
        שיוך משימה לעובד כללי ועדכון בטבלת Task_Worker.

        :param task_id: מזהה המשימה.
        :param worker_id: מזהה העובד הכללי.
        """
        try:
            with connect_database() as connection:
                with connection.cursor() as cursor:
                    # 1. בדיקת קיום העובד הכללי
                    cursor.execute("""
                        SELECT * FROM General_Workers
                        WHERE id = %s
                    """, (worker_id,))
                    worker = cursor.fetchone()

                    if not worker:
                        raise ValueError(f"Worker with ID {worker_id} not found.")

                    # 2. בדיקת קיום המשימה
                    cursor.execute("""
                        SELECT * FROM Tasks
                        WHERE id = %s
                    """, (task.task_id,))
                    task = cursor.fetchone()

                    if not task:
                        raise ValueError(f"Task with id {task.task_id} not found.")

                    # 3. הוספת רשומה לטבלת Task_Worker
                    cursor.execute("""
                        INSERT INTO Task_Worker (task_id, worker_id)
                        VALUES (%s, %s)
                    """, (task.task_id, worker_id))
                    connection.commit()

                    print(f"Task {task.task_id} has been successfully assigned to worker {worker_id}.")
        except Error as e:
            print(f"Error assigning task to worker: {e}")
        except ValueError as ve:
            print(ve)

    def update_task_status(self, worker_id: int, task: Task, status: task_status):
        """
        מעדכן את הסטטוס של משימה עבור עובד כללי.
        :param worker_id: מזהה העובד הכללי
        :param task: שם המשימה
        :param status: סטטוס המשימה החדש
        """
        worker = self._general_workers[worker_id]  # משיכת העובד הכללי מתוך כלל העובדים הכללים
        worker.update_task_status(task, status)

    def process_next_request(self):  # **אין צורך במתודה זו מכיוון שהתור מתקדם באופן אוטומטי**
        """
        מעבדת את הבקשה הראשונה בתור:
        - בודקת אם יש מקום בקורס.
        - אם יש מקום, מכניסה את התלמיד לקורס ומסירה את הבקשה מהתור.
        - אם אין מקום, הבקשה נשארת בתור.
        """
        if len(self.requests) == 0:
            print("No requests to process.")
            return

        # שליפת הבקשה הראשונה בתור
        request = self.requests.popleft()
        course_id = request.course_id
        student_id = request.student_id

        # בדיקה אם הקורס קיים
        if course_id not in self.courses:
            print(f"Course with ID {course_id} not found.")
            return

        course = self.courses[course_id]

        # בדיקה אם יש מקום בקורס
        if len(course.students) < course.capacity:  # בודקים אם כמות הרשומים קטן מהכמות המותרת בקורס
            # הוספת התלמיד לקורס
            student = self.students.get(student_id)  # שליפה מתוך כלל הסטודנטים
            if not student:
                print(f"Student with ID {student_id} not found.")
                return

            course.add_student(student.name)  # הוספה הסטודנט לקורס
            student.courses.add(course)  # הוספת הקורס לסטודנט

            course.remove_registration_request(request)  # נסיר מרשימת ההמתנה של הקורס עצמו
            student.remove_request(request, course)  # נסיר מרשימת ההמתנה של הסטודנט עצמו

            return f"Student {student_id} has been successfully enrolled in course {course_id}."

            # """
            # עיבוד הבקשה הבאה בטבלת Requests (מחיקת הבקשה הראשונה).
            #
            # :param cursor: מצביע למסד הנתונים.
            # """
            # try:
            #     with connect_database() as connection:
            #         with connection.cursor() as cursor:
            #             # מחיקת הבקשה הראשונה לפי request_date
            #             cursor.execute("""
            #                 DELETE FROM Requests
            #                 ORDER BY request_date ASC
            #                 LIMIT 1
            #             """)
            #
            #             cursor.execute("""
            #                     INSERT INTO Student_Course (student_id, course_id)
            #                     VALUES (%s, %s)
            #                 """, (student_id, course_id))
            #
            #             cursor.execute("""
            #                 UPDATE Courses
            #                 SET registered_students = registered_students + 1
            #                 WHERE course_id = %s
            #             """, (course_id,))
            #             connection.commit()
            #
            #             print("Next request processed successfully!")
            # except Error as e:
            #     print(f"Error processing next request: {e}")

        else:
            # אם אין מקום, מחזירים את הבקשה לתור
            self.requests.appendleft(request)
            return f"Course {course_id} is full. Request remains in queue."

    @staticmethod  # מתודה סטטית שאינה תלויה באובייקטי המחלקה, נעודה כפונקציית עזר
    def Adding_problem_reports(report: Task):  # לשימוש מחלקת עובד כללי
        """
        הוספת דיווחי בעיות אחזקה למנהל
        """
        Manager.Maintenance_Problem_Reports.append(report)
        print("The problem was reported successfully.")

    def Deleting_Problem(self, report: Task):
        """
        מחיקת דיווחי בעיות אחזקה ממנהל
        """
        if report in self._Maintenance_Problem_Reports:
            self._Maintenance_Problem_Reports.remove(report)
            print("The problem was deleted successfully.")
        else:
            print("The problem was not found.")

    def Overview_of_waiting_lines(self):
        """
        החזרת דו״ח תורי המתנה בעבור כל קורס
        """
        report = "Overview of waiting lines:\n"
        report += "=========================\n"

        for course_id, course in self._courses.items():
            course_iteration = self._courses[course_id]
            report += f"Course Name: {course_iteration.course_name} (Course ID: {course_id}):\n"
            report += "----------------------------------------------------------------------\n"

            if course_iteration.Requests.qsize() == 0:  # אם התור ריק
                report += "  No students in the waiting list.\n"
            else:
                count = 1
                report += "The waiting list for the course is:\n"
                report += "-----------------------------------\n"
                for waiting in list(course_iteration.Requests.queue):  # גישה ישירה לתור מבלי לשנות אותו
                    report += f"{count}) Student ID: {waiting.student_id}, Name: {waiting.name}\n"
                    count += 1
            report += "=====================================================================\n"

        return report

    def Loading_maintenance_problem_reports(self):
        """
        מילוי מערך ההודעות של המנהל ע״י מעבר על הדיווחים של
        העובדים הכללים.
        """
        for worker_id, worker in self._general_workers.items():
            general_worker = self._general_workers[worker_id]
            for report in general_worker.personal_reports:
                self._Maintenance_Problem_Reports.append(report)  # הוספת הדיווים למערך הודעות האחזקה של המנהל
        print("General maintenance problem reports have been successfully loaded.")

        for teacher_id, teacher in self._teachers.items():
            teacher_iteration = self._teachers[teacher_id]
            for report in teacher_iteration.personal_reports:
                self._Maintenance_Problem_Reports.append(report)  # הוספת הדיווים למערך ההועות האחזקה של המנהל
        print("Classroom maintenance problem reports have been successfully loaded.")

    def Loading_regular_messages(self):
        """
        מילוי מערך ההודעות הרגילות של המנהל ע״י מעבר על
        המחלקות ( תלמיד, מורה, הורה ) שבהם אין לנו מעקב סדור.
        """
        for student_id, student in self._students.items():  # בי��ו�� אי��רצי�� בעבו�� כל ��למי��
            student_iteration = self._students[student_id]
            for response in student_iteration.student_actions:
                self._Messages.append(response)  # הוספת הודעות המערכת למערך ההדעות של המנהל

        for teacher_id, teacher in self._teachers.items():  # בי��ו�� אי��רצי�� בעבו�� כל מו��ה
            teacher_iteration = self._teachers[teacher_id]
            for response in teacher_iteration.teacher_actions:
                self._Messages.append(response)  # הוספת הודעות המערכת למערך ההדעות של המנהל

        for parent_id, parent in self._parents.items():
            parent_iteration = self._parents[parent_id]
            for response in parent_iteration.parent_actions:
                self._Messages.append(response)  # הוספת הודעות המערכת למערך ההדעות של המנהל

        print("System messages loaded successfully.")

    # ---------------------------------------------------------- System functions --------------------------------------

    def System_Recommendation(self):
        """
        הצעת מהלכים למנהל בהתאם לכמות התלמידים שברשימת ההמתנה.
        """
        # בדיקה אם אין קורסים כלל
        if not self._courses:
            self._Messages.append("No courses available in the system.\n")
            return

        for course_id, course in list(self._courses.items()):
            # בדיקה אם יש רשימת המתנה בקורס
            waiting_list = course.Requests  # רשימת ההמתנה שמאוחסנת ב-_requests
            student_count = waiting_list.qsize()  # מספר הסטודנטים ברשימת ההמתנה

            # אם אין רשימת המתנה
            if student_count == 0:
                continue  # לא לעשות כלום, לעבור לקורס הבא

            # מקרה 1: כמות הסטודנטים ברשימת ההמתנה בין 20 ל-30
            elif 20 <= student_count <= 30:
                self._add_message_for_recommendation(course, course_id, student_count)

            # מקרה 2: כמות הסטודנטים ברשימת ההמתנה מעל 30
            elif student_count >= 30:
                self._add_message_for_automatic_opening(course, course_id, student_count)
                new_course = Course(course_name=course.course_name + ' ( Popular Course - Another Opening )',
                                    course_id=course.course_id,
                                    teacher_id=course.teacher_id,
                                    capacity=course.capacity,
                                    registered_students=0
                                    )

                self.popular_courses_opened.append(new_course)  # שמירת הקורס החדש במערך ייחודי
                self._add_students_to_course(new_course, waiting_list)

            # מקרה 3: כמות הסטונים ברשימת ההמתנה היא מעל 5
            elif 5 > student_count:
                self._add_message_for_recommendation(course, course_id, student_count)

    def _add_message_for_recommendation(self, course, course_id, student_count):
        """הוספת הודעה למנהל להמלצה על פתיחת קורס"""
        self._Messages.append(
            f"The number of students on the waiting list for the course '{course.course_name}' ({course_id}) is"
            f" {student_count}. The system recommends opening this course.\n"
        )

    def _add_message_for_automatic_opening(self, course, course_id, student_count):
        """הוספת הודעה למנהל על פתיחת קורס אוטומטית"""
        self._Messages.append(
            f"The number of students on the waiting list for the course '{course.course_name}' ({course_id}) is"
            f" {student_count}. As per the system's guidelines, this course will be opened automatically.\n"
        )

    def _add_students_to_course(self, course: Course, waiting_list: Queue):  # מקבלת את הקורס החדש ורשימת ההמתנה המלאה
        """הוספת סטודנטים לקורס"""
        report = f"Students have been added to the course '{course.course_name}':\n"

        for request in list(waiting_list.queue):  # המרת ה-Queue לרשימה

            student = self.students.get(request.student_id)  # משיכת הסטודנט מתוך מילון הסטודנטים ע״י id נתון
            if (student.name not in course.students) and (
                    request in list(course.Requests.queue)):  # לוודא שהסטודנט לא כבר רשום

                course.students.add(request)  # הוספת תלמיד לקורס
                student.courses.add(course)

                report += f"Student {student} has been added to the course '{course.course_name}'.\n"
            else:
                report += f"Student {student} is already enrolled in the course '{course.course_name}'.\n"

        self._Messages.append(report)  # שליחת דיווח המערכת

    def System_Updates_On_Open_Issues(self):
        """
        פונקציה המדפיסה דו״ח של כל המשימות הפתוחות של העובדים הכללים
        """
        Report_Open_Tasks = "Open Tasks Report: \n"
        for worker_id, worker in self._general_workers.items():
            worker_iteration = self._general_workers[worker_id]  # שליפת העובד הכללי מתוך כלל העובדים הכללים
            Report_Open_Tasks += (f"The open tasks of Employee "
                                  f"'{worker_iteration.name}' ({worker_iteration.id}) are: \n")
            for task in worker_iteration.tasks:  # ביצוע איטרציות על המשימות שלו, נבדוק איזה מהם פתוחות
                if (task.status == "Pending") or (task.status == "In Progress"):
                    Report_Open_Tasks += task
                    Report_Open_Tasks += "\n"
            Report_Open_Tasks += "------------------------- End of reporting for this employee ----------------------\n"
        print(Report_Open_Tasks)

    def Payment_Tracking_System(self):
        """
        מעקב אחרי תשלומי הורים והוצאות על משכורות ומשימות תחזוקה.
        """
        # סך כל ההכנסות וההוצאות
        total_payments_from_parents = 0
        total_teacher_expenses = 0
        total_general_worker_expenses = 0

        # יצירת רשימה להכנת הדיווח
        report_lines = ["Payment Detail Report:\n"]

        # חישוב התשלומים מההורים
        for parent_id, parent in self._parents.items():
            for child in parent.children:
                total_payments_from_parents += len(child.courses) * 500  # 500 ש"ח עבור כל קורס של הילד

        report_lines.append(f"The total payments from all parents is: {total_payments_from_parents}₪\n")

        # חישוב הוצאות על מורים
        for teacher_id, teacher in self._teachers.items():
            total_teacher_expenses += teacher.salary

        report_lines.append(f"The total expenses for all teachers is: {total_teacher_expenses}₪\n")

        # חישוב הוצאות על עובדים כלליים
        for general_worker_id, general_worker in self._general_workers.items():
            total_general_worker_expenses += general_worker.salary

        report_lines.append(f"The total expenses for all general employees are: {total_general_worker_expenses}₪\n")

        # חישוב רווח כולל
        total_profit = total_payments_from_parents - (total_teacher_expenses + total_general_worker_expenses)

        report_lines.append(f"Total profit: {total_profit}₪")
        report_lines.append(f"Total payments: {total_teacher_expenses + total_general_worker_expenses}₪")

        # הצגת הדיווח
        return "\n".join(report_lines)

    def take_request(self, request: Request):

        if not isinstance(request, Request):
            return "Invalid request type."

        student = self.students.get(request.student_id)  # משיכת הסטודנט מהמילון
        course = self.courses.get(request.course_id)  # - " - - " -
        # teacher = self.teachers.get(course.teacher_id)

        if course.registered_students < course.capacity:  # אם הקורס המקורי הראשון מלא, אז נחפש בקורסים החדשים

            if course:
                # הוספת התלמיד לקורס
                student = self.students.get(student.id)  # שליפה מתוך כלל הסטודנטים

                if student.age != course.course_age:
                    return "Student's age does not match the course's age."

                # if teacher.expertise not in course.course_name:
                #     return f"Teacher '{teacher.name}' does not have the expertise required for the course '{course.course_name}'."

                course.add_student(student.name)  # הוספה הסטודנט לקורס
                student.courses.add(course)  # הוספת הקורס לסטודנט

                course.remove_registration_request(request)  # נסיר מרשימת ההמתנה של הקורס עצמו
                student.remove_request(request, course)  # נסיר מרשימת ההמתנה של הסטודנט עצמו

                return f"Student {student.id} has been successfully enrolled in course {course.course_id}."

            else:
                # אם אין מקום, מחזירים את הבקשה לתור
                self.requests.appendleft(request)
                return f"Course {course.course_id} is full. Request remains in queue."

        else:
            self.System_Recommendation()  # המלצות אוטומטיות על קורסים

            for course in self.popular_courses_opened:
                if (course.course_id == request.course_id) and (
                        course.registered_students < course.capacity):  # אם ה ID המקורי שווה ל ID של אותו הקורס אך החדש

                    if student.age != course.course_age:
                        return "Student's age does not match the course's age."

                    # if teacher.expertise not in course.course_name:
                    #     return f"Teacher '{teacher.name}' does not have the expertise required for the course '{course.course_name}'."

                    course.add_student(student.name)  # הוספה הסטודנט לקורס
                    student.courses.add(course)  # הוספת הקורס לסטודנט

                    course.remove_registration_request(request)  # נסיר מרשימת ההמתנה של הקורס עצמו
                    student.remove_request(request, course)  # נסיר מרשימת ההמתנה של הסטודנט עצמו

                    self.System_Recommendation()  # המלצות אוטומטיות על קורסים

                    return f"Student {student.id} has been successfully enrolled in course {course.course_id}."
                continue  # בעצם נמשיך לחפש את אותו הקורס בעל אותו ה ID רק עם מקומות פנויים

            else:
                self.requests.append(request)  # נחזיר לסוף התור
                self.System_Recommendation()
                return f"Course {course.course_id} is full. Request remains in queue."


# ======================================================================================================================
# ---------------------------------------------------------------- Manager Menu ----------------------------------------
class Manager_Menu:
    def __init__(self, manager_sys: Manager):
        self.manager = manager_sys

    def display_menu(self):
        while True:
            try:
                print("\n================== 👨‍💼 Manager Menu 👨‍💼 ======================")
                print("1. Manage Users 🧑‍💻")
                print("2. Manage Courses 📚")
                print("3. Manage Workers' Tasks 🛠️")
                print("4. Payment Tracking Report 💳")
                print("5. Reports 📊")
                print("6. Exit Manager Menu 🔙")
                print("============================================================")
                choice = input("Please enter your choice (1-6): ").strip()

                # בדיקת חוקיות הקלט
                if not choice.isdigit() or not (1 <= int(choice) <= 6):
                    print("❌ Invalid choice. Please enter a number between 1 and 6.")
                    continue

                choice = int(choice)

                # טיפול בבחירות המשתמש
                if choice == 1:
                    self.manage_users()
                elif choice == 2:
                    self.manage_courses()
                elif choice == 3:
                    self.manage_workers()
                elif choice == 4:
                    self.payment_tracking_report()
                elif choice == 5:
                    self.reports()
                elif choice == 6:
                    print("🔙 Exiting Manager Menu...")
                    break

            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}")

    @staticmethod
    def manage_users():
        while True:
            print("\n====== 👥 Users Management Menu 👥 =======")
            print("1. Add new user ➕")
            print("2. Remove user ➖")
            print("3. Exit Users Management Menu 🔙")
            print("===========================================")
            action_choice = input("Enter your choice (1-3): ").strip()

            # בדיקת חוקיות הקלט
            if not action_choice.isdigit() or not (1 <= int(action_choice) <= 3):
                print("❌ Invalid choice. Please enter a number between 1 and 3.")
                continue

            action_choice = int(action_choice)

            if action_choice == 3:
                print("🔙 Exiting Users Management Menu...")
                break

            if action_choice == 1:
                while True:
                    print("\n====== ➕ Add New User Menu ➕ ========")
                    print("1. Manager 👨‍💼")
                    print("2. Teacher 👩‍🏫")
                    print("3. Student 🎓")
                    print("4. Parent 👨‍👩‍👧‍👦")
                    print("5. General Worker 🛠️")
                    print("6. Exit Add New User Menu 🔙")
                    print("===========================================")
                    add_choice = input("Enter your choice (1-6): ").strip()

                    # בדיקת חוקיות הקלט
                    if not add_choice.isdigit() or not (1 <= int(add_choice) <= 6):
                        print("❌ Invalid choice. Please enter a number between 1 and 6.")
                        continue

                    add_choice = int(add_choice)

                    if add_choice == 6:
                        print("🔙 Exiting Add New User Menu...")
                        break

                    while True:
                        try:
                            user_id = int(input("Enter ID: ").strip())
                            if user_id <= 0:
                                raise ValueError("❌ ID must be a positive number.")
                            break
                        except ValueError as ve:
                            print(f"❌ Invalid input: {ve}. Please try again.")

                    # Check if user exists
                    try:
                        with connect_database() as connection:
                            with connection.cursor() as cursor:
                                cursor.execute("SELECT COUNT(*) FROM Passwords_Users WHERE id = %s", (user_id,))
                                if cursor.fetchone()[0] > 0:
                                    print(f"❌ User with ID {user_id} already exists. Please choose a different ID.")
                                    continue
                    except mysql.connector.Error as e:
                        print(f"❌ Database error: {e}")
                        continue

                    # Validate name (First and Last name with one space in between)
                    while True:
                        user_name = input("Enter name: ").strip()
                        if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", user_name):
                            break
                        else:
                            print("❌ Invalid name format. Please enter a valid name (e.g., 'John Doe').")

                    # Validate password
                    while True:
                        user_password = input("Enter password: ").strip()
                        if len(user_password) >= 6:
                            break
                        else:
                            print("❌ Password must be at least 6 characters long. Please try again.")

                    # Add user by type
                    try:
                        with connect_database() as connection:
                            with connection.cursor() as cursor:
                                if add_choice == 1:  # Manager
                                    while True:
                                        try:
                                            school_budget = float(input("Enter school budget: ").strip())
                                            if school_budget <= 0:
                                                raise ValueError("❌ Budget must be a positive number.")
                                            break
                                        except ValueError as ve:
                                            print(f"❌ Invalid input: {ve}. Please try again.")
                                    cursor.execute(
                                        "INSERT INTO Managers (id, name, school_budget) VALUES (%s, %s, %s)",
                                        (user_id, user_name, school_budget)
                                    )
                                    print(f"✅ User '{user_name}' (ID: {user_id}) added successfully.")

                                elif add_choice == 2:  # Teacher
                                    while True:
                                        expertise = input("Enter teacher expertise: ").strip()
                                        # בדיקת תקינות של expertise
                                        if re.match(r"^[A-Z][a-z]*$", expertise):
                                            break
                                        else:
                                            print(
                                                "❌ Invalid expertise format. Please enter one word starting with a capital letter (e.g., 'Math').")
                                    while True:
                                        try:
                                            salary = float(input("Enter teacher salary: ").strip())
                                            if salary <= 0:
                                                raise ValueError("❌ Salary must be a positive number.")
                                            break
                                        except ValueError as ve:
                                            print(f"❌ Invalid input: {ve}. Please try again.")
                                    cursor.execute(
                                        "INSERT INTO Teachers (id, name, expertise, salary) VALUES (%s, %s, %s, %s)",
                                        (user_id, user_name, expertise, salary)
                                    )
                                    print(f"✅ User '{user_name}' (ID: {user_id}) added successfully.")

                                elif add_choice == 3:  # Student
                                    while True:
                                        try:
                                            age = int(input("Enter student age: ").strip())
                                            if age <= 0:
                                                raise ValueError("❌ Age must be a positive number.")
                                            break
                                        except ValueError as ve:
                                            print(f"❌ Invalid input: {ve}. Please try again.")

                                    while True:
                                        parent_email = input("Enter parent's email: ").strip()
                                        if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", parent_email):
                                            break
                                        else:
                                            print("❌ Invalid email format. Please try again.")

                                    while True:
                                        preferred_course = input("Enter preferred course: ").strip()
                                        # בדיקת תקינות של preferred course
                                        if re.match(r"^[A-Z][a-z]+$", preferred_course):
                                            break
                                        else:
                                            print(
                                                "❌ Invalid expertise format. Please enter one word starting with a capital letter (e.g., 'Math').")

                                    # הכנסה לטבלת Students
                                    cursor.execute(
                                        "INSERT INTO Students (id, name, age, parent_email, preferred_course) VALUES (%s, %s, %s, %s, %s)",
                                        (user_id, user_name, age, parent_email, preferred_course)
                                    )

                                    # 🔹 **חיבור אוטומטי בין סטודנט להורה אם קיים אימייל תואם**
                                    cursor.execute("SELECT id FROM Parents WHERE email = %s", (parent_email,))
                                    parent = cursor.fetchone()

                                    if parent:
                                        parent_id = parent[0]
                                        cursor.execute(
                                            "INSERT INTO Student_Parent (student_id, parent_id) VALUES (%s, %s)",
                                            (user_id, parent_id))
                                        print(
                                            f"🔗 Student '{user_name}' (ID: {user_id}) linked automatically to Parent (ID: {parent_id}).")
                                    print(f"✅ User '{user_name}' (ID: {user_id}) added successfully.")

                                elif add_choice == 4:  # Parent
                                    while True:
                                        parent_email = input("Enter email: ").strip()
                                        if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", parent_email):
                                            break
                                        else:
                                            print("❌ Invalid email format. Please try again.")

                                    # הכנסה לטבלת Parents
                                    cursor.execute(
                                        "INSERT INTO Parents (id, name, email) VALUES (%s, %s, %s)",
                                        (user_id, user_name, parent_email)
                                    )

                                    # 🔹 **חיבור אוטומטי בין הורה לתלמידים אם קיים אימייל תואם**
                                    cursor.execute("SELECT id FROM Students WHERE parent_email = %s", (parent_email,))
                                    students = cursor.fetchall()

                                    if students:
                                        for student in students:
                                            student_id = student[0]
                                            cursor.execute(
                                                "INSERT INTO Student_Parent (student_id, parent_id) VALUES (%s, %s)",
                                                (student_id, user_id))

                                        print(
                                            f"🔗 Parent '{user_name}' (ID: {user_id}) linked automatically to {len(students)} student(s).")

                                    print(f"✅ User '{user_name}' (ID: {user_id}) added successfully.")

                                elif add_choice == 5:  # General Worker
                                    while True:
                                        try:
                                            salary = float(input("Enter worker salary: ").strip())
                                            if salary <= 0:
                                                raise ValueError("❌ Salary must be a positive number.")
                                            break
                                        except ValueError as ve:
                                            print(f"❌ Invalid input: {ve}. Please try again.")
                                    cursor.execute(
                                        "INSERT INTO General_Workers (id, name, salary) VALUES (%s, %s, %s)",
                                        (user_id, user_name, salary)
                                    )
                                    print(f"✅ User '{user_name}' (ID: {user_id}) added successfully.")

                                # Add user to Passwords_Users table
                                cursor.execute(
                                    "INSERT INTO Passwords_Users (id, name, password) VALUES (%s, %s, %s)",
                                    (user_id, user_name, user_password)
                                )
                                connection.commit()

                    except mysql.connector.Error as e:
                        print(f"❌ An error occurred: {e}")

            elif action_choice == 2:
                while True:
                    print("\n======== ➖ Remove User Menu ➖ ===========")
                    print("1. Manager 👨‍💼")
                    print("2. Teacher 👩‍🏫")
                    print("3. Student 🎓")
                    print("4. Parent 👨‍👩‍👧‍👦")
                    print("5. General Worker 🛠️")
                    print("6. Exit Remove User Menu 🔙")
                    print("===========================================")
                    remove_choice = input("Enter your choice (1-6): ").strip()

                    # בדיקת חוקיות הקלט
                    if not remove_choice.isdigit() or not (1 <= int(remove_choice) <= 6):
                        print("❌ Invalid choice. Please enter a number between 1 and 6.")
                        continue

                    remove_choice = int(remove_choice)

                    if remove_choice == 6:
                        print("🔙 Exiting Remove User Menu...")
                        break

                    while True:
                        try:
                            user_id = int(input("Enter ID: ").strip())
                            if user_id <= 0:
                                raise ValueError("❌ ID must be a positive number.")
                            break
                        except ValueError as ve:
                            print(f"❌ Invalid input: {ve}. Please try again.")

                    try:
                        with connect_database() as connection:
                            with connection.cursor() as cursor:
                                # בדיקה אם המשתמש קיים בטבלת הסיסמאות
                                cursor.execute("SELECT name FROM Passwords_Users WHERE id = %s", (user_id,))
                                user_record = cursor.fetchone()

                                if not user_record:
                                    print(f"❌ User with ID {user_id} not found in system.")
                                    continue

                                user_name = user_record[0]  # שם המשתמש

                                # מיפוי טבלאות לסוגי המשתמשים
                                user_roles = {
                                    1: "Managers",
                                    2: "Teachers",
                                    3: "Students",
                                    4: "Parents",
                                    5: "General_Workers"
                                }

                                table_name = user_roles.get(remove_choice)

                                # בדיקה אם המשתמש קיים בטבלה הייעודית
                                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE id = %s", (user_id,))
                                if cursor.fetchone()[0] == 0:
                                    print(
                                        f"❌ User '{user_name}' (ID: {user_id}) was not found in {table_name}, no deletion occurred.")
                                    continue

                                # טיפול בקשרים לפני מחיקה
                                if remove_choice == 2:  # Teacher
                                    cursor.execute("DELETE FROM Course_Teacher WHERE teacher_id = %s", (user_id,))
                                    cursor.execute("UPDATE Courses SET teacher_id = NULL WHERE teacher_id = %s",
                                                   (user_id,))

                                elif remove_choice == 3:  # Student
                                    cursor.execute("DELETE FROM Student_Course WHERE student_id = %s", (user_id,))
                                    cursor.execute("DELETE FROM Student_Parent WHERE student_id = %s", (user_id,))
                                    cursor.execute("DELETE FROM Waitlists WHERE student_id = %s", (user_id,))

                                elif remove_choice == 4:  # Parent
                                    cursor.execute("DELETE FROM Student_Parent WHERE parent_id = %s", (user_id,))

                                elif remove_choice == 5:  # General Worker
                                    cursor.execute("DELETE FROM Task_Worker WHERE worker_id = %s", (user_id,))

                                # מחיקת המשתמש מהטבלה הייעודית
                                cursor.execute(f"DELETE FROM {table_name} WHERE id = %s", (user_id,))
                                cursor.execute("DELETE FROM Passwords_Users WHERE id = %s", (user_id,))

                                connection.commit()
                                print(f"✅ User '{user_name}' (ID: {user_id}) has been removed successfully.")

                    except mysql.connector.Error as e:
                        print(f"❌ An error occurred: {e}")

    @staticmethod
    def manage_courses():
        while True:
            print("\n====== 📚 Courses Management Menu 📚 ======")
            print("1. Add New Course ➕")
            print("2. Remove Course ➖")
            print("3. Assign Teacher to Course 👨‍🏫")
            print("4. Remove Student From Course")
            print("5. View Waitlists ⏳")
            print("6. Exit Courses Management Menu 🔙")
            print("===========================================")
            action_choice = input("Please enter your choice (1-6): ").strip()

            # בדיקת חוקיות הקלט
            if not action_choice.isdigit() or not (1 <= int(action_choice) <= 6):
                print("❌ Invalid choice. Please enter a number between 1 and 6.")
                continue

            action_choice = int(action_choice)

            if action_choice == 6:
                print("🔙 Exiting Courses Management Menu...")
                break

            elif action_choice == 1:  # Add Course
                try:
                    with connect_database() as connection:
                        with connection.cursor() as cursor:
                            # קלט שם קורס ובדיקת תקינות
                            while True:
                                course_name = input("Enter course name: ").strip()
                                if re.match(r"^[A-Z][a-z]+$", course_name):
                                    break
                                else:
                                    print(
                                        "❌ Invalid course name format. Please enter one word starting with a capital letter (e.g., 'Math').")

                            # קלט קיבולת קורס ובדיקת חיוביות
                            while True:
                                try:
                                    capacity = int(input("Enter course capacity: "))
                                    if capacity <= 0:
                                        print("❌ Please enter a valid positive number for course capacity.")
                                    else:
                                        break
                                except ValueError:
                                    print("❌ Invalid input. Please enter a valid number for course capacity.")

                            # קלט גיל הקורס ובדיקת חיוביות
                            while True:
                                try:
                                    course_age = int(input("Enter course age: "))
                                    if course_age <= 0:
                                        print("❌ Please enter a valid positive number for course age.")
                                    else:
                                        break
                                except ValueError:
                                    print("❌ Invalid input. Please enter a valid number for course age.")

                            # הכנסת הקורס למסד הנתונים (ללא course_id כי הוא רץ אוטומטית)

                            cursor.execute(
                                """
                                INSERT INTO Courses (course_name, capacity, course_age)
                                VALUES (%s, %s, %s)
                                """,
                                (course_name, capacity, course_age)
                            )

                            # קבלת ה-ID של הקורס שנוסף
                            cursor.execute("SELECT LAST_INSERT_ID()")
                            course_id = cursor.fetchone()[0]

                            connection.commit()
                            print(f"✅ Course '{course_name}' (ID: {course_id}) added successfully to the database!")

                except mysql.connector.Error as e:
                    print(f"❌ An error occurred: {e}")

            elif action_choice == 2:  # Remove Course
                try:
                    # קלט ID קורס להסרה ובדיקת חיוביות
                    while True:
                        try:
                            course_id = int(input("Enter course ID to remove: "))
                            if course_id <= 0:  # בדיקת ID חיובי
                                print("❌ Please enter a valid positive number for course ID.")
                            else:
                                break  # קלט תקין, יוצאים מהלולאה
                        except ValueError:
                            print("❌ Invalid input. Please enter a valid number for course ID.")

                    # בדיקת קיום קורס במסד הנתונים והסרתו במידה וקיים
                    with connect_database() as connection:
                        with connection.cursor() as cursor:
                            # שליפת שם הקורס והמורה המשויך (אם קיים)
                            cursor.execute("SELECT course_name, teacher_id FROM Courses WHERE course_id = %s",
                                           (course_id,))
                            course = cursor.fetchone()

                            if not course:
                                print("❌ Course not found in the database.")
                                continue

                            course_name, teacher_id = course

                            # עדכון טבלת Courses להסרת שיוך המורה (אם קיים)
                            if teacher_id:
                                cursor.execute("UPDATE Courses SET teacher_id = NULL WHERE course_id = %s",
                                               (course_id,))

                            # מחיקת כל ההפניות לקורס בטבלאות הקשרים
                            cursor.execute("DELETE FROM Student_Course WHERE course_id = %s", (course_id,))
                            cursor.execute("DELETE FROM Course_Teacher WHERE course_id = %s", (course_id,))

                            # בדיקת תלמידים בהמתנה לפני מחיקה
                            cursor.execute("SELECT student_id FROM Waitlists WHERE course_id = %s", (course_id,))
                            waitlisted_students = cursor.fetchall()

                            if waitlisted_students:
                                print(
                                    f"⚠️ There were {len(waitlisted_students)} students on the waitlist for '{course_name}'. Their requests will be removed.")

                            cursor.execute("DELETE FROM Waitlists WHERE course_id = %s", (course_id,))

                            # מחיקת הקורס עצמו
                            cursor.execute("DELETE FROM Courses WHERE course_id = %s", (course_id,))
                            connection.commit()

                    print(f"✅ Course '{course_name}' (ID: {course_id}) has been successfully removed.")

                except ValueError:
                    print("❌ Invalid input. Please enter a valid course ID.")

                except mysql.connector.Error as e:
                    print(f"❌ An error occurred while removing the course: {e}")

            elif action_choice == 3:  # Assign Teacher to Course
                try:
                    with connect_database() as connection:
                        with connection.cursor() as cursor:
                            # קלט ID קורס ובדיקת חיוביות
                            while True:
                                try:
                                    course_id = int(input("Enter course ID: "))
                                    if course_id <= 0:
                                        print("❌ Please enter a valid positive number for course ID.")
                                    else:
                                        break
                                except ValueError:
                                    print("❌ Invalid input. Please enter a valid number for course ID.")

                            # בדיקה אם הקורס קיים בטבלת הקורסים ושליפת שמו
                            cursor.execute("SELECT course_name, teacher_id FROM Courses WHERE course_id = %s",
                                           (course_id,))
                            course = cursor.fetchone()

                            if not course:
                                print(
                                    f"❌ Course with ID {course_id} not found in the database. Cannot assign a teacher.")
                                continue

                            course_name, existing_teacher_id = course

                            # בדיקה אם כבר יש מורה משובץ לקורס
                            if existing_teacher_id is not None:
                                print(
                                    f"❌ Course '{course_name}' (ID: {course_id}) already has a teacher assigned (ID: {existing_teacher_id}). Cannot assign another teacher.")
                                continue

                            # קלט ID מורה ובדיקת חיוביות
                            while True:
                                try:
                                    teacher_id = int(input("Enter teacher ID: "))
                                    if teacher_id <= 0:
                                        print("❌ Please enter a valid positive number for teacher ID.")
                                    else:
                                        break
                                except ValueError:
                                    print("❌ Invalid input. Please enter a valid number for teacher ID.")

                            # בדיקה שהמורה קיים ושליפת שמו ותחום ההתמחות
                            cursor.execute("SELECT name, expertise FROM Teachers WHERE id = %s", (teacher_id,))
                            teacher = cursor.fetchone()

                            if not teacher:
                                print(
                                    f"❌ Teacher with ID {teacher_id} not found in the database. Cannot be assigned to course '{course_name}' (ID: {course_id}).")
                                continue

                            teacher_name, teacher_expertise = teacher

                            # בדיקה אם המורה מתאים ללמד את הקורס (מבוסס על תחום ההתמחות)
                            if teacher_expertise != course_name:
                                print(
                                    f"❌ Teacher '{teacher_name}' (ID: {teacher_id}) does not match the expertise required for course '{course_name}' (ID: {course_id}).")
                                continue

                            # עדכון teacher_id בטבלת Courses
                            cursor.execute(
                                """
                                UPDATE Courses
                                SET teacher_id = %s
                                WHERE course_id = %s
                                """,
                                (teacher_id, course_id)
                            )

                            # הכנסת קשר בין הקורס למורה בטבלת Course_Teacher
                            cursor.execute(
                                """
                                INSERT INTO Course_Teacher (course_id, teacher_id)
                                VALUES (%s, %s)
                                """,
                                (course_id, teacher_id)
                            )

                            connection.commit()
                            print(
                                f"✅ Teacher '{teacher_name}' (ID: {teacher_id}) successfully assigned to course '{course_name}' (ID: {course_id}).")

                except mysql.connector.Error as e:
                    print(f"❌ An error occurred: {e}")

            elif action_choice == 4:  # Remove Student from Course
                try:
                    with connect_database() as connection:
                        with connection.cursor() as cursor:
                            # קלט מזהה קורס ובדיקת חוקיות
                            while True:
                                try:
                                    course_id = int(input("Enter Course ID: "))
                                    if course_id <= 0:
                                        print("❌ Please enter a valid positive number for Course ID.")
                                    else:
                                        break
                                except ValueError:
                                    print("❌ Invalid input! Please enter a valid integer for Course ID.")

                            # קלט מזהה תלמיד ובדיקת חוקיות
                            while True:
                                try:
                                    student_id = int(input("Enter Student ID: "))
                                    if student_id <= 0:
                                        print("❌ Please enter a valid positive number for Student ID.")
                                    else:
                                        break
                                except ValueError:
                                    print("❌ Invalid input! Please enter a valid integer for Student ID.")

                            # בדיקה אם הקורס והתלמיד קיימים במערכת
                            cursor.execute("SELECT course_name, registered_students FROM Courses WHERE course_id = %s",
                                           (course_id,))
                            course = cursor.fetchone()
                            if not course:
                                print(f"❌ Course with ID {course_id} not found in the database.")
                                continue

                            course_name, registered_students = course

                            cursor.execute("SELECT name FROM Students WHERE id = %s", (student_id,))
                            student = cursor.fetchone()
                            if not student:
                                print(f"❌ Student with ID {student_id} not found in the database.")
                                continue

                            student_name = student[0]

                            # בדיקה אם התלמיד רשום לקורס
                            cursor.execute("SELECT 1 FROM Student_Course WHERE student_id = %s AND course_id = %s",
                                           (student_id, course_id))
                            if not cursor.fetchone():
                                print(
                                    f"❌ Student {student_name} (ID: {student_id}) is not enrolled in course {course_name} (ID: {course_id}).")
                                continue

                            # מחיקת התלמיד מטבלת הקשרים
                            cursor.execute("DELETE FROM Student_Course WHERE student_id = %s AND course_id = %s",
                                           (student_id, course_id))
                            connection.commit()
                            print(
                                f"✅ Student {student_name} (ID: {student_id}) has been removed from course {course_name} (ID: {course_id}).")

                            # עדכון מספר התלמידים בקורס
                            cursor.execute(
                                "UPDATE Courses SET registered_students = registered_students - 1 WHERE course_id = %s",
                                (course_id,))
                            connection.commit()

                            # בדיקה אם יש תלמידים ברשימת ההמתנה
                            cursor.execute("""
                                SELECT student_id FROM Waitlists
                                WHERE course_id = %s
                                ORDER BY date ASC
                                LIMIT 1
                            """, (course_id,))

                            waitlist_student = cursor.fetchone()
                            if waitlist_student:
                                waitlist_student_id = waitlist_student[0]

                                # הוספת התלמיד הראשון מרשימת ההמתנה לקורס
                                cursor.execute("INSERT INTO Student_Course (student_id, course_id) VALUES (%s, %s)",
                                               (waitlist_student_id, course_id))

                                # עדכון מספר התלמידים בקורס
                                cursor.execute(
                                    "UPDATE Courses SET registered_students = registered_students + 1 WHERE course_id = %s",
                                    (course_id,))

                                # מחיקת התלמיד מרשימת ההמתנה
                                cursor.execute("DELETE FROM Waitlists WHERE student_id = %s AND course_id = %s",
                                               (waitlist_student_id, course_id))

                                # קבלת שם התלמיד שעבר מרשימת ההמתנה
                                cursor.execute("SELECT name FROM Students WHERE id = %s", (waitlist_student_id,))
                                new_student_name = cursor.fetchone()[0]

                                connection.commit()
                                print(
                                    f"📌 Student {new_student_name} (ID: {waitlist_student_id}) has been moved from waitlist to course {course_name} (ID: {course_id}).")

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")

            elif action_choice == 5:  # Manage Waitlists
                """
                מציגה את רשימות ההמתנה של כל הקורסים במערכת וממליצה על פתיחת קורסים חדשים במידת הצורך.
                """
                try:
                    with connect_database() as connection:
                        with connection.cursor(dictionary=True) as cursor:
                            print("\n⏳ Generating Course Waitlists Report...\n")

                            # 🔹 שליפת רשימת כל הקורסים עם מספר התלמידים שממתינים בתור
                            cursor.execute("""
                                SELECT c.course_id, c.course_name, COUNT(w.student_id) AS waitlist_count
                                FROM Courses c
                                LEFT JOIN Waitlists w ON c.course_id = w.course_id
                                GROUP BY c.course_id, c.course_name
                                ORDER BY waitlist_count DESC;
                            """)

                            waitlists = cursor.fetchall()

                            if not waitlists:
                                print("✅ No students are currently on any waitlist.")
                                continue

                            report_lines = ["⏳ Course Waitlists Report", "========================================="]
                            course_recommendations = []

                            for course in waitlists:
                                course_id = course["course_id"]
                                course_name = course["course_name"]
                                waitlist_count = course["waitlist_count"]

                                report_lines.append(f"📖 Course: {course_name} (ID: {course_id})")
                                report_lines.append(f"   🔢 Students in Waitlist: {waitlist_count}")

                                # 🔹 בדיקה אם כדאי לפתוח קורס חדש
                                if waitlist_count >= 5:
                                    course_recommendations.append((course_name, waitlist_count))

                            if course_recommendations:
                                report_lines.append("\n💡 Recommended Courses to Open:")
                                for course_name, count in course_recommendations:
                                    report_lines.append(f"   ✅ '{course_name}' - {count} students waiting.")

                            report_lines.append("=========================================")

                            print("\n".join(report_lines))

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")

    @staticmethod
    def manage_workers():
        while True:
            print("\n== 🛠️ Workers Tasks Management Menu 🛠️ ==")
            print("1. Assign Task To Worker ➕")
            print("2. Open Tasks Report 📋")
            print("3. Exit Workers Tasks Management Menu 🔙")
            print("=========================================")
            action_choice = input("Enter your choice (1-3): ").strip()

            # בדיקת חוקיות הקלט
            if not action_choice.isdigit() or not (1 <= int(action_choice) <= 3):
                print("❌ Invalid choice. Please enter a number between 1 and 3.")
                continue

            action_choice = int(action_choice)

            if action_choice == 3:
                print("🔙 Exiting Workers Tasks Management Menu...")
                break

            if action_choice == 1:
                try:
                    # קלט ID משימה ובדיקת חיוביות עם טיפול בשגיאות
                    while True:
                        try:
                            task_id = int(input("Enter task ID: ").strip())
                            if task_id <= 0:
                                raise ValueError("Task ID must be a positive number.")
                            break  # אם הקלט תקין, יוצאים מהלולאה
                        except ValueError as e:
                            print(f"❌ Invalid input: {e}. Please enter a valid positive number for task ID.")

                    # קלט ID עובד ובדיקת חיוביות עם טיפול בשגיאות
                    while True:
                        try:
                            worker_id = int(input("Enter worker ID: ").strip())
                            if worker_id <= 0:
                                raise ValueError("Worker ID must be a positive number.")
                            break  # אם הקלט תקין, יוצאים מהלולאה
                        except ValueError as e:
                            print(f"❌ Invalid input: {e}. Please enter a valid positive number for worker ID.")

                    # בדיקה אם העובד והמשימה קיימים
                    with connect_database() as connection:
                        with connection.cursor() as cursor:
                            # בדיקה אם המשימה קיימת בטבלת `Tasks` ושליפת שמה
                            cursor.execute("SELECT name FROM Tasks WHERE id = %s", (task_id,))
                            task = cursor.fetchone()
                            if not task:
                                print(f"❌ Task with ID {task_id} not found in the database.")
                                continue
                            task_name = task[0]

                            # בדיקה אם העובד קיים בטבלת `General_Workers` ושליפת שמו
                            cursor.execute("SELECT name FROM General_Workers WHERE id = %s", (worker_id,))
                            worker = cursor.fetchone()
                            if not worker:
                                print(f"❌ Worker with ID {worker_id} not found in the database.")
                                continue
                            worker_name = worker[0]

                            # בדיקה אם המשימה כבר קיימת בטבלת `Task_Worker` ללא קשר לעובד
                            cursor.execute("SELECT 1 FROM Task_Worker WHERE task_id = %s", (task_id,))
                            if cursor.fetchone():
                                print(f"❌ Task '{task_name}' (ID: {task_id}) is already assigned to a worker.")
                                continue

                            # הוספת המשימה לעובד
                            cursor.execute("""
                                INSERT INTO Task_Worker (task_id, worker_id)
                                VALUES (%s, %s)
                            """, (task_id, worker_id))

                            connection.commit()
                            print(
                                f"✅ Task '{task_name}' (ID: {task_id}) successfully assigned to worker '{worker_name}' (ID: {worker_id}).")

                except ValueError:
                    print("❌ Invalid input. Please enter numbers where required.")
                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")

            elif action_choice == 2:
                print("\n📌 Generating Open Tasks Report...")
                try:
                    with connect_database() as connection:
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                SELECT 
                                    gw.id AS worker_id,
                                    gw.name AS worker_name,
                                    t.id AS task_id,
                                    t.name AS task_name,
                                    t.description AS task_description,
                                    t.status AS task_status,
                                    t.urgency AS task_urgency
                                FROM 
                                    General_Workers gw
                                JOIN 
                                    Task_Worker tw ON gw.id = tw.worker_id  
                                JOIN 
                                    Tasks t ON tw.task_id = t.id  
                                WHERE 
                                    t.status IN ('PENDING', 'IN_PROGRESS')  
                                ORDER BY 
                                    gw.id, FIELD(t.urgency, 'HIGH', 'MEDIUM', 'LOW');
                            """)

                            open_tasks = cursor.fetchall()
                            if not open_tasks:
                                print("✅ No open tasks found.")
                                continue

                            report = "\n📋 Open Tasks Report\n"
                            current_worker_id = None

                            for task in open_tasks:
                                worker_id, worker_name, task_id, task_name, task_description, task_status, task_urgency = task

                                if worker_id != current_worker_id:
                                    if current_worker_id is not None:
                                        report += "-------------------------\n"
                                    report += f"\n👷 Employee: {worker_name} (ID: {worker_id})\n"
                                    report += "-----------------------------------\n"
                                    current_worker_id = worker_id

                                report += (
                                    f"🔹 Task ID: {task_id} | Name: {task_name}\n"
                                    f"   - Description: {task_description}\n"
                                    f"   - Status: {task_status} | Urgency: {task_urgency}\n"
                                )

                            report += "-------------------------\n"
                            print(report)

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")

    @staticmethod
    def payment_tracking_report():
        try:
            with connect_database() as connection:
                with connection.cursor(dictionary=True) as cursor:

                    print("\n📊 Generating Payment Tracking Report...\n")

                    # 🔹 שליפת סך ההכנסות מהורים
                    cursor.execute("SELECT SUM(payment) AS total_payments FROM Parents")
                    total_payments_from_parents = cursor.fetchone()["total_payments"] or 0

                    # 🔹 שליפת מידע על כל המורים ומשכורותיהם
                    cursor.execute("SELECT name, salary FROM Teachers")
                    teachers = cursor.fetchall()
                    total_teacher_expenses = sum(t["salary"] for t in teachers)

                    # 🔹 שליפת מידע על כל העובדים הכלליים ומשכורותיהם
                    cursor.execute("SELECT name, salary FROM General_Workers")
                    general_workers = cursor.fetchall()
                    total_general_worker_expenses = sum(w["salary"] for w in general_workers)

                    # 🔹 חישוב הוצאות קורסים לפי משתנה capacity
                    cursor.execute("SELECT COUNT(*) AS total_courses FROM Courses")
                    total_courses = cursor.fetchone()["total_courses"] or 0
                    total_course_expenses = total_courses * 500  # נניח שכל קורס עולה 500$

                    # 🔹 חישוב הוצאות משימות תחזוקה (משימות שהושלמו)
                    cursor.execute("""
                        SELECT t.name AS task_name, 
                               (CASE 
                                    WHEN t.urgency = 'LOW' THEN 100 
                                    WHEN t.urgency = 'MEDIUM' THEN 250 
                                    WHEN t.urgency = 'HIGH' THEN 500 
                                    WHEN t.urgency = 'CRITICAL' THEN 1000 
                                    ELSE 0 
                                END) AS task_cost
                        FROM Tasks t
                        WHERE t.status = 'COMPLETED'
                    """)
                    maintenance_tasks = cursor.fetchall()
                    total_maintenance_expenses = sum(task["task_cost"] for task in maintenance_tasks)

                    # 🔹 חישוב כלל ההוצאות
                    total_expenses = (
                            total_teacher_expenses
                            + total_general_worker_expenses
                            + total_course_expenses
                            + total_maintenance_expenses
                    )

                    # 🔹 חישוב הרווח הסופי
                    total_profit = total_payments_from_parents - total_expenses

                    # 📊 **יצירת הדוח**
                    report_lines = [
                        "\n📊 Payment Detail Report\n",
                        "-----------------------------------",
                        f"💰 Total payments received from all parents: {total_payments_from_parents}$",
                        "-----------------------------------",
                        "👨‍🏫 Teacher Salaries Breakdown:",
                    ]

                    if teachers:
                        for teacher in teachers:
                            report_lines.append(f"   - {teacher['name']}: {teacher['salary']}$")
                    else:
                        report_lines.append("   ❌ No teachers found.")

                    report_lines.append("-----------------------------------")
                    report_lines.append("👨‍🔧 General Worker Salaries Breakdown:")

                    if general_workers:
                        for worker in general_workers:
                            report_lines.append(f"   - {worker['name']}: {worker['salary']}$")
                    else:
                        report_lines.append("   ❌ No general workers found.")

                    report_lines.extend([
                        "-----------------------------------",
                        f"📚 Total expenses for all teachers: {total_teacher_expenses}$",
                        f"🛠️ Total expenses for all general employees: {total_general_worker_expenses}$",
                        f"🏫 Total expenses for all courses: {total_course_expenses}$",
                        "-----------------------------------",
                        "🛠️ Maintenance Expenses Breakdown:",
                    ])

                    if maintenance_tasks:
                        for task in maintenance_tasks:
                            report_lines.append(f"   - {task['task_name']}: {task['task_cost']}$")
                    else:
                        report_lines.append("   ❌ No completed maintenance tasks found.")

                    report_lines.extend([
                        "-----------------------------------",
                        f"🛠️ Total Maintenance Expenses: {total_maintenance_expenses}$",
                        "-----------------------------------",
                        f"📉 Total expenses: {total_expenses}$",
                        f"💵 Total profit: {total_profit}$"
                    ])

                    print("\n".join(report_lines))

        except mysql.connector.Error as e:
            print(f"❌ Error generating payment tracking report: {e}")

    @staticmethod
    def reports():
        """
        תפריט הדו"חות למנהל
        """
        while True:
            print("\n======== 📊 Reports Menu 📊 =========")
            print("1. Courses Popularity Report 📚")
            print("2. Teachers Workload Report 👨‍🏫")
            print("3. Payments and Debts Report 💰")
            print("4. Students Performance Report 📈")
            print("5. Maintenances Report 🛠️")
            print("6. Exit Reports Menu 🔙")
            print("=====================================")
            rep_choice = input("Enter your choice (1-6): ").strip()

            # בדיקת חוקיות הקלט
            if not rep_choice.isdigit() or not (1 <= int(rep_choice) <= 6):
                print("❌ Invalid choice. Please enter a number between 1 and 6.")
                continue

            rep_choice = int(rep_choice)

            if rep_choice == 6:
                print("🔙 Exiting Workers Tasks Management Menu...")
                break

            elif rep_choice == 1:
                """
                דו"ח המציג את כמות התלמידים הרשומים לכל קורס, כולל כמות התלמידים ברשימת ההמתנה.
                """
                try:
                    with connect_database() as connection:
                        with connection.cursor(dictionary=True) as cursor:
                            cursor.execute("""
                                SELECT c.course_name, c.registered_students, c.capacity,
                                       (SELECT COUNT(*) FROM Waitlists w WHERE w.course_id = c.course_id) AS waitlist_count
                                FROM Courses c
                                ORDER BY c.registered_students DESC, waitlist_count DESC
                            """)
                            courses = cursor.fetchall()

                            if not courses:
                                print("❌ No courses found.")
                                continue

                            report_lines = ["\n📚 Course Popularity Report"]
                            for course in courses:
                                status = "✅ Open" if course["registered_students"] < course["capacity"] else "⏳ Full"
                                report_lines.append(
                                    f"📖 {course['course_name']} - Students: {course['registered_students']}/{course['capacity']} | Waitlist: {course['waitlist_count']} | {status}")

                            print("\n".join(report_lines))

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")

            elif rep_choice == 2:
                """
                מתודה ליצירת דוח עומס עבודה למורים, כולל מספר הקורסים, מספר התלמידים בכל קורס ומספר המשימות.
                """
                try:
                    with connect_database() as connection:
                        with connection.cursor(dictionary=True) as cursor:
                            print("\n📊 Generating Teacher Workload Report...\n")

                            # שליפת כל המורים
                            cursor.execute("""
                                SELECT t.id, t.name, COUNT(c.course_id) AS total_courses
                                FROM Teachers t
                                LEFT JOIN Courses c ON t.id = c.teacher_id
                                GROUP BY t.id, t.name
                            """)
                            teachers = cursor.fetchall()

                            if not teachers:
                                print("❌ No teachers found in the system.")
                                continue

                            report_lines = ["📊 Teacher Workload Report", "========================================="]

                            for teacher in teachers:
                                teacher_id = teacher["id"]
                                teacher_name = teacher["name"]
                                total_courses = teacher["total_courses"]

                                report_lines.append(f"\n👨‍🏫 Teacher: {teacher_name} (ID: {teacher_id})")
                                report_lines.append(f"📚 Number of Courses: {total_courses}")

                                # שליפת הקורסים של המורה ומספר התלמידים בכל קורס
                                cursor.execute("""
                                    SELECT c.course_name, COUNT(sc.student_id) AS student_count
                                    FROM Courses c
                                    LEFT JOIN Student_Course sc ON c.course_id = sc.course_id
                                    WHERE c.teacher_id = %s
                                    GROUP BY c.course_id, c.course_name
                                """, (teacher_id,))

                                courses = cursor.fetchall()

                                if courses:
                                    report_lines.append("📘 Courses and Student Counts:")
                                    for course in courses:
                                        report_lines.append(
                                            f"   - {course['course_name']}: {course['student_count']} students")
                                else:
                                    report_lines.append("   ❌ No courses assigned to this teacher.")

                                # בדיקת מספר המשימות שהמורה קיבל (אם רלוונטי)
                                cursor.execute("""
                                    SELECT COUNT(*) AS total_tasks 
                                    FROM Tasks 
                                    WHERE reporter_id = %s
                                """, (teacher_id,))
                                total_tasks = cursor.fetchone()["total_tasks"]

                                report_lines.append(f"📌 Assigned Tasks: {total_tasks}")

                            report_lines.append("=========================================")
                            print("\n".join(report_lines))

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")

            elif rep_choice == 3:
                """
                מפיק דו"ח תשלומים וחובות של הורים, כולל סכום התשלום הכולל, חובות לא משולמים, ורשימת ההורים שחייבים כסף.
                """
                try:
                    with connect_database() as connection:
                        with connection.cursor(dictionary=True) as cursor:
                            print("\n📊 Generating Payment and Debts Report...\n")

                            # שליפת כל ההורים והתשלומים ששילמו
                            cursor.execute("""
                                SELECT p.id, p.name, p.payment AS total_paid
                                FROM Parents p
                            """)
                            parents = cursor.fetchall()

                            if not parents:
                                print("❌ No parents found in the system.")
                                continue

                            # שליפת חובות הורים – חישוב סכום כולל של קורסים שילדיהם רשומים אליהם
                            cursor.execute("""
                                SELECT sp.parent_id, SUM(1000) AS total_due
                                FROM Student_Parent sp
                                JOIN Student_Course sc ON sp.student_id = sc.student_id
                                WHERE sc.paid = 0  -- בדיקת קורסים שלא שולמו
                                GROUP BY sp.parent_id
                            """)
                            debts = {row["parent_id"]: row["total_due"] for row in cursor.fetchall()}

                            # חישוב סכומים כוללים
                            total_received = sum(parent["total_paid"] for parent in parents)
                            total_debt = sum(debts.values())

                            report_lines = ["📊 Payment and Debts Report", "========================================="]

                            for parent in parents:
                                parent_id = parent["id"]
                                parent_name = parent["name"]
                                total_paid = parent["total_paid"]
                                total_due = debts.get(parent_id, 0)

                                report_lines.append(f"\n👨‍👩‍👦 Parent: {parent_name} (ID: {parent_id})")
                                report_lines.append(f"💰 Total Paid: {total_paid}$")
                                report_lines.append(
                                    f"❗ Total Debt: {total_due}$" if total_due > 0 else "✅ No outstanding debt.")

                            # סיכום כללי
                            report_lines.append("=========================================")
                            report_lines.append(f"💵 Total Received: {total_received}$")
                            report_lines.append(f"❗ Total Outstanding Debt: {total_debt}$")
                            report_lines.append("=========================================")

                            print("\n".join(report_lines))

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")

            elif rep_choice == 4:
                """
                מפיק דו"ח ביצועי תלמידים הכולל ציונים, משימות ורשימת המתנה.
                """
                try:
                    with connect_database() as connection:
                        with connection.cursor(dictionary=True) as cursor:
                            print("\n📊 Generating Student Performance Report...\n")

                            # שליפת פרטי תלמידים, כולל שמות וגילאים
                            cursor.execute("""
                                SELECT id, name, age 
                                FROM Students
                            """)
                            students = cursor.fetchall()

                            if not students:
                                print("❌ No students found in the system.")
                                continue

                            report_lines = ["📊 Student Performance Report", "========================================="]

                            for student in students:
                                student_id = student["id"]
                                student_name = student["name"]
                                student_age = student["age"]

                                report_lines.append(
                                    f"\n🎓 Student: {student_name} (ID: {student_id}), Age: {student_age}")

                                # שליפת הקורסים שהתלמיד רשום אליהם
                                cursor.execute("""
                                    SELECT c.course_name, sc.grades, sc.assignments
                                    FROM Student_Course sc
                                    JOIN Courses c ON sc.course_id = c.course_id
                                    WHERE sc.student_id = %s
                                """, (student_id,))

                                courses = cursor.fetchall()

                                if not courses:
                                    report_lines.append("📌 Not enrolled in any courses.")
                                else:
                                    report_lines.append("\n📚 Courses & Performance:")
                                    for course in courses:
                                        course_name = course["course_name"]
                                        grade = course["grades"] if course[
                                                                        "grades"] is not None else "No grade recorded"
                                        assignments = course["assignments"] if course[
                                            "assignments"] else "No assignments recorded"

                                        report_lines.append(f"  📖 {course_name}")
                                        report_lines.append(f"     📊 Grade: {grade}")
                                        report_lines.append(f"     📝 Assignments: {assignments}")

                                    # חישוב ממוצע הציונים
                                    valid_grades = [c["grades"] for c in courses if c["grades"] is not None]
                                    if valid_grades:
                                        avg_grade = sum(valid_grades) / len(valid_grades)
                                        report_lines.append(f"     📈 Average Grade: {avg_grade:.2f}")

                                # שליפת רשימת המתנה לקורסים
                                cursor.execute("""
                                    SELECT c.course_name, w.date,
                                           (SELECT COUNT(*) FROM Waitlists w2 
                                            WHERE w2.course_id = w.course_id AND w2.date <= w.date) AS queue_position
                                    FROM Waitlists w
                                    JOIN Courses c ON w.course_id = c.course_id
                                    WHERE w.student_id = %s
                                    ORDER BY w.date ASC
                                """, (student_id,))

                                waitlists = cursor.fetchall()

                                if waitlists:
                                    report_lines.append("\n⏳ Waitlisted Courses:")
                                    for waitlist in waitlists:
                                        course_name = waitlist["course_name"]
                                        queue_position = waitlist["queue_position"]
                                        date_registered = waitlist["date"]
                                        report_lines.append(
                                            f"  📖 {course_name} (Position: {queue_position}, Registered: {date_registered})")

                            report_lines.append("=========================================")

                            print("\n".join(report_lines))

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")

            elif rep_choice == 5:
                """
                מפיק דו"ח תקלות ותחזוקה במערכת, כולל סטטוסים, עובדים אחראיים וניתוח כללי.
                """
                try:
                    with connect_database() as connection:
                        with connection.cursor(dictionary=True) as cursor:
                            print("\n🔧 Generating Maintenances Report...\n")

                            # 🔹 שליפת כל המשימות הקשורות לתחזוקה
                            cursor.execute("""
                                SELECT t.id, t.name, t.description, t.status, t.urgency, 
                                       gw.name AS worker_name
                                FROM Tasks t
                                LEFT JOIN Task_Worker tw ON t.id = tw.task_id
                                LEFT JOIN General_Workers gw ON tw.worker_id = gw.id
                                WHERE t.name LIKE 'Maintenance%'
                                ORDER BY FIELD(t.status, 'PENDING', 'IN_PROGRESS', 'COMPLETED'), 
                                         FIELD(t.urgency, 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW')
                            """)

                            tasks = cursor.fetchall()

                            if not tasks:
                                print("✅ No maintenance tasks found.")
                                continue

                            report_lines = ["🔧 Maintenances Report", "========================================="]

                            task_counts = {"PENDING": 0, "IN_PROGRESS": 0, "COMPLETED": 0}
                            urgency_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}

                            for task in tasks:
                                task_id = task["id"]
                                task_name = task["name"]
                                description = task["description"]
                                status = task["status"]
                                urgency = task["urgency"]
                                worker_name = task["worker_name"] if task["worker_name"] else "Unassigned"

                                task_counts[status] += 1
                                urgency_counts[urgency] += 1

                                report_lines.append(f"\n🛠️ Task: {task_name} (ID: {task_id})")
                                report_lines.append(f"   📌 Description: {description}")
                                report_lines.append(f"   📊 Status: {status}")
                                report_lines.append(f"   ⚠️ Urgency: {urgency}")
                                report_lines.append(f"   👷 Assigned Worker: {worker_name}")

                            # 🔹 שליפת מספר תקלות שחוזרות על עצמן (זיהוי כפילויות בשם התקלה)
                            cursor.execute("""
                                SELECT name, COUNT(*) AS count 
                                FROM Tasks 
                                WHERE name LIKE 'Maintenance%'
                                GROUP BY name
                                HAVING COUNT(*) > 1
                                ORDER BY count DESC
                            """)

                            recurring_issues = cursor.fetchall()

                            if recurring_issues:
                                report_lines.append("\n🔄 Recurring Maintenance Issues:")
                                for issue in recurring_issues:
                                    report_lines.append(f"   🔁 {issue['name']} - Reported {issue['count']} times")

                            # 🔹 סיכום כללי של סטטוסים ודחיפות
                            report_lines.append("\n📊 Maintenance Task Statistics:")
                            report_lines.append(f"   ⏳ Pending Tasks: {task_counts['PENDING']}")
                            report_lines.append(f"   🔄 In Progress Tasks: {task_counts['IN_PROGRESS']}")
                            report_lines.append(f"   ✅ Completed Tasks: {task_counts['COMPLETED']}\n")

                            report_lines.append("📊 Urgency Level Breakdown:")
                            for level, count in urgency_counts.items():
                                report_lines.append(f"   ⚠️ {level}: {count} Tasks")

                            report_lines.append("=========================================")

                            print("\n".join(report_lines))

                except mysql.connector.Error as e:
                    print(f"❌ Database error: {e}")


# ======================================================================================================================
# ---------------------------------------------------------------- Summary  --------------------------------------------
"""
בחלק זה נעסוק בפונקציות שיוצרות את הישויות השונות ע״י קובץ ה Excel,
נעסוק בפונקציות הדו״ח שונות, ובפונקצית שמירה אל תוך קובץ Excel חדש.
"""


# ======================================================================================================================
# ------------------------------------- Algorithm Analysis and Execution Department ------------------------------------

class Analysis:
    def __init__(self, manager: Manager):
        self.manager = manager  # שמירת אובייקט מסוג Manager

    def Create_Object(self) -> str:  # **מתודה ראשונה להפעלה**, לצורך יצירת האובייקטים במערכת מטבלת האקסל
        """
        פונקציה זו יוצרת אובייקטים בהתאם לגיליונות שבקובץ ה-Excel,
        כלומר בקובץ האקסל קיימים מספר גליונות (סטודנטים, מורים, קורסים, בקשות לרישום לקורסים),
        במתודה זו, נעבור על כל הגליונות וניצור אובייקטים ע״פ הכתוב בהם.
        """
        base_dir = os.path.dirname(__file__)  # תיקיית הקוד (Core)
        excel_file_path = os.path.join(base_dir, '..', 'Files', 'learning_center_project_data.xlsx')

        # קריאת הקובץ
        excel_data = pd.ExcelFile(excel_file_path, engine="openpyxl")

        sheet_names = excel_data.sheet_names
        sheet_dataframes = {}

        for sheet_name in sheet_names:
            sheet_df = excel_data.parse(sheet_name)
            sheet_dataframes[sheet_name] = sheet_df  # הגדרת המילון

        for sheet_name, df in sheet_dataframes.items():  # לולאה שעוברת על כל הגיליונות

            if sheet_name == "Students":  # אם הגיליון הוא סטודנט

                for _, row in df.iterrows():  # אז נעבור על כל הרשומות
                    # ניצור אובייקט מסוג רשימת הגיליון
                    student = Student(
                        name=row['Name'],
                        id=row['StudentID'],
                        age=row['Age'],
                        parent_email=row['ParentEmail'],
                        preferred_course=row['PreferredCourse']
                    )
                    self.manager.students[row['StudentID']] = student  # נשמור במילון הרשומות של המנהל לסוג זה

            elif sheet_name == "Teachers":  # אם הגיליון הוא מורים

                for _, row in df.iterrows():  # אז נעבור על כל הרשומות
                    # ניצור אובייקט מסוג רשימת הגיליון
                    teacher = Teacher(
                        name=row['Name'],
                        id=row['TeacherID'],
                        expertise=row['Expertise']
                    )
                    self.manager.teachers[row['TeacherID']] = teacher  # נשמור במילון הרשומות של המנהל לסוג זה

            elif sheet_name == "Courses":  # אם הגיליון הוא קורסים

                for _, row in df.iterrows():  # אז נעבור על כל הרשומות
                    # ניצור אובייקט מסוג רשימת הגיליון
                    course = Course(
                        course_name=row['CourseName'],
                        course_id=row['CourseID'],
                        teacher_id=row['TeacherID'],
                        capacity=row['Capacity'],
                        registered_students=row['RegisteredStudents'],
                    )
                    self.manager.courses[row['CourseID']] = course  # נשמור במילון הרשומות של המנהל לסוג זה

            elif sheet_name == "Waitlist":  # אם הגיליון הוא רשימת המתנה

                for _, row in df.iterrows():  # אז נעבור על כל הרשומות
                    # ניצור אובייקט מסוג רשימת הגיליון
                    request = Request(
                        course_id=row['CourseID'],
                        student_id=row['StudentID'],
                        request_date=row['RequestDate']
                    )
                    self.manager.requests.append(request)  # נשמור במילון הרשומות של המנהל לסוג זה

        return "\n🎉 Objects have been successfully created from the Excel data!"

    def Data_reading_function(self) -> str:  # **מתודה שניה להפעלה**, נפעיל אותה בסוף, מכיוון שעוברת על המערכים,
        # אז נירצה שהיא תעבור עליהם לאחר ביצוע הרשמת הסטודנטים
        """
        הפונקציה מחזירה את רשימת התלמידים שהצליחו להירשם, רשימת תלמידים שלא הצליחו להירשם וסיבת הדחייה שלהם,
        ובנוסף מחזירה אודות קורסים חדשים שנפתחו.
        """
        Successfully_enrolled_students = []  # סטודנטים שהצליחו להירשם בהצלחה
        Students_not_successfully_enrolled = []  # סטודנטים שלא שהצליחו להירשם בהצלחה
        New_courses = []  # מערך של בקשות לרישום לקורס שלא טופלו/שלא הצליחו לטפל

        for new_course in self.manager.popular_courses_opened:  # נעבור על המערך הייחודי של הקורסים החדשים
            New_courses.append(new_course)

        for course in self.manager.courses.values():
            for student_name in course.students:  # נעבור על כל שמות הסטודנטים שרשומים בקורס
                for student in self.manager.students.values():  # נאתר את אותם הסטודנטים, מאחר אנחנו רוצים את המחלקות שלהם
                    if student_name == student.name:  # אם שם הסטודנט הרשום דומה לשם סטודנט המחלקה
                        Successfully_enrolled_students.append(student)

        for request in list(self.manager.requests):  # נעבור על כל בקשות הרישום לקורסים שלא טופלו/שלא צלחו
            student = self.manager.students.get(request.student_id)  # משיכת הסטודנט לפי ID של בקשת רישום
            Students_not_successfully_enrolled.append(student)

        report = "\n============================= <Data Report> ======================================"
        report += "\n======================== Registration New Report ================================"

        report += "\n✏️👩‍🏫✅ --- Students who successfully registered for courses: ---\n"
        report += "-------------------------------------------------------------------\n"

        if Successfully_enrolled_students:
            for student in Successfully_enrolled_students:
                for course in self.manager.courses.values():
                    if student.name in course.students:  # אם שם הסטודנט מופיע ברשימת השמות הרשומים בקורס

                        report += (
                            f"🟢 **Student Name:** {student.name} (Student ID: {student.id}) | **Age Student**: {student.age} | "
                            f"**Parent Email:** {student.email} | "
                            f"**Enrolled in course :** {course.course_name} (Course ID: {course.course_id}) \n"
                        )

        else:
            report += "\n⚠️ No students found."

        report += "\n🕑🎒❌ --- Students who were not successfully enrolled in courses: ---\n"
        report += "-------------------------------------------------------------------------\n"

        if Students_not_successfully_enrolled:
            for student in Students_not_successfully_enrolled:
                for request in self.manager.requests:
                    if request.student_id == student.id:
                        course = self.manager.courses.get(
                            request.course_id)  # נשמור את הקורס שאליו רצה להירשם הסטודנט, לצורך הוצאת מידעים
                        # rejection_reason = student.register_for_course(course, self.manager.teachers.get(course.teacher_id))  # שמירת סיבת דחייה
                        rejection_reason = self.manager.take_request(request)
                        report += (
                            f"🔴 **Student Name:** {student.name} (Student ID: {student.id}) | **Age Student**: {student.age} | "
                            f"**Parent Email:** {student.email} | "
                            f"**Waiting for Course:** {course.course_name} (Course ID: {request.course_id}) |"
                            f"**Reason for rejection: {rejection_reason}**\n"
                        )

        else:
            report += "\n⚠️ No students found."

        report += "\n📖🏫 --- New courses opened: ---\n"
        report += "-----------------------------------\n"

        if New_courses:
            for new_course in New_courses:
                report += (f"🔵 **Course ID**: {new_course.course_id} | **Course Name**: {new_course.course_name} | "
                           f"**Number of registered**: {new_course.registered_students} | **Registration Limit**: {new_course.capacity} | "
                           f"**The course age is:** {new_course.course_age}\n")

            report += "\n============================= End of report ==================================="
        else:
            report += "\nNo new courses found."

        return report

    def Excel_registration_report(self) -> str:  # **מתודה שלישית להפעלה**, פונקציה תפעל לאחר יצירת האובייקטים במערכת,
        # פונקציה זו מבצעת גם הרשמה לקורסים, בגלל זה תפעל שניה
        """
        הפונקציה מחזירה דוח בקובץ אקסל חדש, האקסל יהיה בנוי כך :
        גיליון 1 - רשימת תלמידים ששובצו בהצלחה לקורסים
        גיליון 2 - רשימת תלמידים שלא הצליחו להירשם לקורס ( ללא התאמה וסיבת הדחייה )
        גיליון 3 - פרטים על הקורסים החדשים שנפתחו ( עקב עומסים ברשימות המתנה )
        """

        # ---------------------------------- Implementing Objects (Entities) in the System -----------------------------

        # נטמיע את הבקשות של הסטודנטים לרישום לקורסים, נעבור פר בקשה ונבדוק של מי הבקשה הזו (של איזה סטודנט)
        sorted_requests = sorted(self.manager.requests,
                                 key=lambda req: req.request_date)  # מיון מהבקשות הקודמות ועד לחדשות

        for request in sorted_requests:  # רשימת בקשות רישומים לקורסים, עוברים עליה מהבקשה המוקדמת ביותר ועד לחדשה ביותר
            student = self.manager.students.get(request.student_id)  # משיכת הסטודנט ע״פ ID נתון של בקשת רישום
            self.manager.add_student_to_waitlist(request, student)  # נוסיף לרשימת ההמתנה של הקורס עצמו

        # נטמיע את המורים המלמדים בקורסים עצמם
        for teacher_id, teacher in self.manager.teachers.items():  # עוברים על כל המורים במערכת
            for course_id, course in self.manager.courses.items():  # עוברים על כל הקורסים במערכת
                if teacher.expertise in course.course_name:  # נבדוק האם התמחותו של המורה מתאים לשם הקורס (אם נמצא בשם הקורס)
                    self.manager.assign_teacher_to_course(teacher_id, course_id)  # שיבוץ מורה לקורס ע״פ התמחותו

        print("\n🚀 Entities in the system have been successfully implemented and are ready for use! ✅\n")

        # -------------------------------- Starting Data Collection from the System After Implementation ---------------

        successfully_enrolled_students = []  # מערך לשמירת סטודנטים שהצליחו להירשם
        failed_enrollment_students = []  # מערך לשמירת סטודנטים שלא הצליחו להירשם
        new_courses_opened = []  # קורסים חדשים שנפתחו

        sorted_requests = sorted(self.manager.requests,
                                 key=lambda req: req.request_date)  # מיון מהבקשות הקודמות ועד לחדשות

        for request in sorted_requests:  # מעבר על הבקשות בסדר כרונולוגי

            failure_reason = self.manager.take_request(request)  # לוקח בקשה ומנסה לרשום במערכת

            student = self.manager.students.get(request.student_id)
            course = self.manager.courses.get(request.course_id)

            if not student:  # אם סטודנט לא נמצא
                failed_enrollment_students.append({
                    'Student ID': request.student_id,
                    'Name': "Unknown",
                    'Parent Email': "N/A",
                    'Course ID': request.course_id,
                    'Course Name': "Unknown",
                    'Reason for Failure': "Student not found"
                })
                continue

            if not course:  # אם קורס לא נמצא
                failed_enrollment_students.append({
                    'Student ID': student.id,
                    'Name': student.name,
                    'Parent Email': student.email,
                    'Course ID': request.course_id,
                    'Course Name': "Unknown",
                    'Reason for Failure': "Course not found"
                })
                continue

            teacher = self.manager.teachers.get(course.teacher_id)

            if not teacher:  # אם מורה לא נמצאה
                failed_enrollment_students.append({
                    'Student ID': student.id,
                    'Name': student.name,
                    'Parent Email': student.email,
                    'Course ID': course.course_id,
                    'Course Name': course.course_name,
                    'Reason for Failure': "No assigned teacher for this course"
                })
                continue

            # failure_reason = student.register_for_course(course, teacher)

            if "successfully" in failure_reason:  # אם כל הישויות המעורבות נמצאו

                successfully_enrolled_students.append({
                    'Student ID': student.id,
                    'Name': student.name,
                    'Parent Email': student.email,
                    'Course ID': course.course_id,
                    'Course Name': course.course_name
                })

                self.manager.requests.remove(request)  # הסרת הבקשה ממערכת הניהול
                course.remove_registration_request(request)  # הסרת הבקשה מהקורס
                student.remove_request(request, course)  # הסרת הבקשה מהסטודנט

            else:
                failed_enrollment_students.append({
                    'Student ID': student.id,
                    'Name': student.name,
                    'Parent Email': student.email,
                    'Course ID': course.course_id,
                    'Course Name': course.course_name,
                    'Reason for Failure': failure_reason
                })

        # בסיום כל תהליך הרישום
        self.manager.System_Recommendation()  # המלצות אוטומטיות על קורסים
        # self.manager.process_next_request()

        for new_course in self.manager.popular_courses_opened:
            teacher = self.manager.teachers.get(new_course.teacher_id)  # נשלוף את המורה מהמילון לפי מפתח מזהה של הקורס

            new_courses_opened.append({
                'Course ID': new_course.course_id,
                'Course Name': new_course.course_name,
                'Age Course': new_course.course_age,
                'Number of Registrations': new_course.registered_students,
                'Number of Requests': new_course.Requests.qsize(),
                'Capacity quantity': new_course.capacity,
                'Teacher Name': teacher.name,
                'Teacher Expertise': teacher.expertise,
                'Teacher ID': teacher.id
            })

        print("\n📊 Data collection from the system after implementation was successful! ✅\n")

        # נשמור את הדאטה שאספנו על הרישומים
        df_successfully_enrolled = pd.DataFrame(successfully_enrolled_students)
        df_failed_enrollment = pd.DataFrame(failed_enrollment_students)
        df_new_courses_opened = pd.DataFrame(new_courses_opened)

        # קביעת הנתיב לתיקיית Init שנמצאת ברמה אחת אחורה
        init_folder = os.path.join(os.path.dirname(__file__), '..', 'Init')

        # הפיכת הנתיב לקובץ מוחלט (כדי למנוע בעיות שקשורות לנתיב יחסי)
        init_folder = os.path.abspath(init_folder)

        # יצירת התיקייה אם היא לא קיימת
        os.makedirs(init_folder, exist_ok=True)

        # קביעת הנתיב לשמירת הקובץ
        file_path = os.path.join(init_folder, 'Registration_New_Report.xlsx')

        # יצירת קובץ Excel עם שלושה גליונות
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df_successfully_enrolled.to_excel(writer, sheet_name='Successfully Enrolled', index=True)
            df_failed_enrollment.to_excel(writer, sheet_name='Failed Enrollment', index=True)
            df_new_courses_opened.to_excel(writer, sheet_name='New Courses Opened', index=True)

        # החזרת הודעה עם מיקום הקובץ
        return (f"\n🎉 Excel report has been successfully generated!"
                f"\n🗂️ Location:"
                f"\n {file_path}")
