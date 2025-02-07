# ייבוא סיפריות מחלקה
import mysql
import mysql.connector

from Core.Person import Person
from Core.Task import Task

# ייבוא סיפריות עזר
from abc import ABC
from typing import List

from System_Menu import current_user
from Utils import task_status, UrgencyLevel
from Utils.task_status import TaskStatus
import re

from conf_MySQL import connect_database


class General_Worker(Person, ABC):
    # ---------------------------------------------------------------- Summary -----------------------------------------
    """
    מחלקת עובד כללי היורשת מ- Person.
    """

    # -------------------------------------------------------------- Constructor ---------------------------------------
    def __init__(self, name: str, id: int, salary: float = 2000):
        super().__init__(name, id)

        self._name = name
        self._id = id
        self._salary = salary
        self._tasks: List[Task] = []  # משימות שמקבל מהמנהל
        self._personal_reports: List[Task] = []  # דיווחים שדיווח

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
    def salary(self) -> float:
        return self._salary

    @salary.setter
    def salary(self, val: float):
        if not isinstance(val, (int, float)) or val <= 0:
            raise ValueError("Salary must be a non-negative number.")
        self._salary = val

    @property
    def tasks(self) -> List[Task]:
        """
        מחזירה את רשימת המשימות של העובד.
        """
        return self._tasks

    @tasks.setter
    def tasks(self, val: List[Task]):
        if not isinstance(val, list) or not all(isinstance(task, Task) for task in val):
            raise ValueError("Tasks must be a list of Task instances.")
        self._tasks = val

    @property
    def personal_reports(self) -> list[Task]:
        return self._personal_reports

    @personal_reports.setter
    def personal_reports(self, val: List[str]):
        if not isinstance(val, list) or not all(isinstance(report, str) for report in val):
            raise ValueError("Personal reports must be a list of strings.")
        self._personal_reports = val

    # ---------------------------------------------------- Basic Functions ---------------------------------------------
    def __str__(self) -> str:
        """
        מציגה את פרטי העובד הכללי בצורה קריאה.
        """
        tasks_details = '\n'.join(f"- {task}" for task in self._tasks) if self._tasks else "No tasks assigned"
        return (
            f"General Worker Details:\n"
            f"Name: {self._name}\n"
            f"ID: {self._id}\n"
            f"Tasks:\n{tasks_details}"
        )

    def __eq__(self, other) -> bool:
        """
        משווה בין שני אובייקטי General_Worker על פי המזהה (id).
        """
        if isinstance(other, General_Worker):
            return self._id == other.id
        return False

    def __hash__(self) -> int:
        """
        מחזיר את ה-hash של האובייקט General_Worker. ה-hash מבוסס על המזהה (id).
        """
        return hash(self._id)

    # ------------------------------------------------------ Advanced Functions ----------------------------------------
    def add_task(self, task: Task):
        """
        מוסיפה משימה חדשה לעובד הכללי.
        """
        if not isinstance(task, Task):
            raise ValueError("Task must be an instance of the Task class.")
        if task in self._tasks:
            raise ValueError("Task with this ID already exists.")
        self._tasks.append(task)

    def update_task_status(self, task: Task, update_status: task_status):
        """
        מעדכנת את הסטטוס של משימה קיימת.
        """
        if task not in self._tasks:
            raise ValueError("Task not found.")

        for T in self._tasks:
            if T == task:
                T.status = update_status  # עדכון הסטטוס של המשימה שנמצאה

                """
                מעדכן את הסטטוס של משימה קיימת במסד הנתונים.
                :param task_id: מזהה המשימה (ID) שצריך לעדכן.
                :param new_status: הסטטוס החדש (PENDING, IN_PROGRESS, COMPLETED).
                """
                try:
                    with connect_database() as connection:
                        with connection.cursor() as cursor:
                            # בדיקה אם המשימה קיימת
                            cursor.execute("SELECT id FROM Tasks WHERE id = %s", (T.task_id,))
                            task = cursor.fetchone()

                            if not task:
                                print("Task not found in database.")
                                return

                            # עדכון הסטטוס של המשימה
                            cursor.execute("""
                                UPDATE Tasks 
                                SET status = %s 
                                WHERE id = %s
                            """, (T.status, T.task_id))

                            connection.commit()
                            print(f"Task ID '{T.task_id}' status updated successfully to {T.status}.")

                except mysql.connector.Error as e:
                    print(f"An error occurred while updating task status: {e}")

                print(f"The status of the task {task.name} has been successfully updated to {update_status}")
                return  # יציאה לאחר העדכון

        # אם הגענו לנקודה זו, המשמעות היא שהמשימה לא נמצאה
        raise ValueError("Task with the given name was not found.")

    def update_task_priority(self, task: Task, update_urgency: UrgencyLevel):
        """
        מעדכנת את רמת הדחיפות של משימה קיימת.
        """
        if task not in self._tasks:
            raise ValueError("Task not found.")

        if not isinstance(update_urgency, UrgencyLevel.UrgencyLevel):
            raise ValueError("Priority must be an instance of urgency level Enum.")

        for T in self._tasks:
            if T == task:
                T.urgency = update_urgency  # ביצוע עדכון רמת הדחיפות
                print(
                    f"The urgency level of the task '{task.name}' has been successfully updated to '{update_urgency}'.")
                return

    def display_tasks(self):
        """
        מציגה את כל המשימות של העובד עם הסטטוס שלהן.
        """
        if not self._tasks:
            return "No tasks assigned."

        task_details = f"General Worker: {self._name}, ID: {self._id}:\n"
        for task in self._tasks:
            task_details += f"Task name: {task.name},Task description: {task.description},Task status: {task.status}\n"
            task_details += f"Task urgency level: {task.urgency}"

        task_details += f"The number of tasks are: {len(self.tasks)}"
        return "\n".join(task_details)

    def Problem_Reports(self, name: str, description: str, status: TaskStatus = None, urgency: UrgencyLevel = None,
                        additional_info: str = None):
        """
        דיווחי בעיות אחזקה.

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
                description=f"{description}\nAdditional Info: {additional_info if additional_info else 'None'}",
                status=status if status else TaskStatus.PENDING,  # אם לא נמסר סטטוס, ברירת המחדל היא PENDING
                urgency=urgency if urgency else UrgencyLevel.UrgencyLevel.MEDIUM,
                # אם לא נמסרה דחיפות, ברירת המחדל היא Medium
                reporter=self.name,
                reporter_id=self.id
            )

            # הוספת הדיווח לרשימת הדיווחים האישיים
            self.personal_reports.append(task)
            print("The report was successfully sent to the manager.")

            # הוספת המשימה למסד הנתונים
            with connect_database() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO Tasks (id, name, description, status, urgency, reporter_id)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        task.task_id, task.name, task.description, task.status.name, task.urgency.name,
                        task.reporter_id))
                    connection.commit()
                    print("The problem report was successfully added to the database.")

        except mysql.connector.Error as e:
            print(f"An error occurred while submitting the problem report to the database: {e}")

        except Exception as e:
            print(f"Failed to send the report: {str(e)}")

    def filter_tasks(self, status: task_status, urgency: UrgencyLevel) -> List[Task]:
        filtered_tasks = self._tasks
        if status:
            filtered_tasks = [task for task in filtered_tasks if task.status == status]
        if urgency:
            filtered_tasks = [task for task in filtered_tasks if task.urgency == urgency]
        return filtered_tasks


# ======================================================================================================================
# ------------------------------------------------------------- General_Worker_Menu ---------------------------------------
class General_Worker_Menu:
    def __init__(self, general_worker: General_Worker):
        self.general_worker = general_worker  # מאתחל את אובייקט עובד כללי

    def display_menu(self):
        """
        מציג את התפריט האפשרויות לעובד כללי
        """
        while True:
            try:
                print("\n============= 🛠️ General Worker Menu 🛠️ ==============")
                print("1. Update Task Status 🔄")
                print("2. Report a Maintenance Issue ⚠️")
                print("3. Exit General Worker Menu 🔙")
                print("======================================================")
                choice = input("Please enter your choice (1-3): ").strip()

                # בדיקת חוקיות הקלט
                if not choice.isdigit() or not (1 <= int(choice) <= 3):
                    print("❌ Invalid choice. Please enter a number between 1 and 3.")
                    continue

                choice = int(choice)

                # טיפול בבחירות המשתמש
                if choice == 1:
                    self.update_task_status()
                elif choice == 2:
                    self.report_maintenance_issue()
                elif choice == 3:
                    print("🔙 Exiting General Worker Menu...")
                    break

            except Exception as e:
                print(f"❌ An unexpected error occurred: {e}")

    @staticmethod
    def update_task_status():
        """
        מתודה לעובד כללי לעדכון סטטוס של משימת תחזוקה.
        """

        try:
            worker_id = current_user["id"]
            worker_name = current_user["name"]

            with connect_database() as connection:
                with connection.cursor() as cursor:
                    # 🔹 הצגת רשימת המשימות של העובד
                    cursor.execute("""
                        SELECT t.id, t.name, t.status 
                        FROM Tasks t
                        JOIN Task_Worker tw ON t.id = tw.task_id
                        WHERE tw.worker_id = %s
                    """, (worker_id,))

                    tasks = cursor.fetchall()

                    if not tasks:
                        print(f"✅ No tasks assigned to Worker '{worker_name}' (ID: {worker_id}).")
                        return

                    print(f"\n📌 Assigned Tasks for '{worker_name}' (ID: {worker_id}):")
                    for task in tasks:
                        print(f"  - Task ID: {task[0]}, Name: {task[1]}, Status: {task[2]}")

                    # 🔹 קלט מזהה משימה ובדיקת תקינות
                    while True:
                        try:
                            task_id = int(input("\nEnter Task ID to update: ").strip())
                            if task_id <= 0:
                                print("❌ Task ID must be a positive integer.")
                                continue

                            # בדיקה שהמשימה משויכת לעובד
                            cursor.execute("""
                                SELECT name, status FROM Tasks 
                                WHERE id = %s AND id IN 
                                (SELECT task_id FROM Task_Worker WHERE worker_id = %s)
                            """, (task_id, worker_id))
                            task = cursor.fetchone()

                            if not task:
                                print(f"❌ Task with ID {task_id} is not assigned to Worker '{worker_name}'.")
                                return

                            task_name, current_status = task
                            print(f"🔎 Task '{task_name}' (ID: {task_id}) found. Current Status: {current_status}")
                            break

                        except ValueError:
                            print("❌ Invalid input! Please enter a valid integer for Task ID.")

                    # 🔹 תפריט לבחירת סטטוס חדש
                    print("\nChoose new status:")
                    print("1. Pending")
                    print("2. In Progress")
                    print("3. Completed")

                    status_map = {"1": "PENDING", "2": "IN_PROGRESS", "3": "COMPLETED"}
                    while True:
                        status_choice = input("Choose status (1-3): ").strip()
                        new_status = status_map.get(status_choice)

                        if new_status:
                            break
                        print("❌ Invalid status choice. Please enter a number between 1-3.")

                    # 🔹 עדכון סטטוס המשימה במסד הנתונים
                    cursor.execute("""
                        UPDATE Tasks 
                        SET status = %s 
                        WHERE id = %s
                    """, (new_status, task_id))
                    connection.commit()

                    print(f"✅ Task '{task_name}' (ID: {task_id}) status updated to {new_status} by '{worker_name}'.")

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")

    @staticmethod
    def report_maintenance_issue():
        """
        פונקציה לדיווח על בעיית תחזוקה.
        התקלה תירשם כמשימה (Task) בטבלת 'Tasks' עם סטטוס 'PENDING'.
        """
        try:
            # קלט שם המשימה/תיאור הבעיה בקצרה
            while True:
                task_name = input("Enter Task Name (e.g., 'Leaking Pipe'): ").strip()
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

            # קלט תיאור מפורט של הבעיה
            while True:
                issue_description = input("Enter Issue Description: ").strip()
                if not issue_description:
                    print("❌ Issue description cannot be empty. Please enter a valid description.")
                else:
                    break

            with connect_database() as connection:
                with connection.cursor() as cursor:
                    # בדיקה אם המדווח קיים במערכת
                    cursor.execute("SELECT name FROM Passwords_Users WHERE id = %s", (reporter_id,))
                    reporter_record = cursor.fetchone()

                    if not reporter_record:
                        print(f"❌ No user found with ID {reporter_id}. Please check and try again.")
                        return

                    reporter_name = reporter_record[0]

                    # בדיקה אם כבר קיימת תקלה פתוחה שדווחה על ידי המשתמש
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
                    print(f"✅ Issue '{task_name}' reported successfully by {reporter_name} (ID: {reporter_id}).")

        except mysql.connector.Error as e:
            print(f"❌ Database error: {e}")

