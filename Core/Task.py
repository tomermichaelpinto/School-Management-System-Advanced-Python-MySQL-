# ייבוא סיפריות עזר
import mysql
import mysql.connector

from DataBase.conf_MySQL import connect_database
from Utils.task_status import TaskStatus
from Utils.UrgencyLevel import UrgencyLevel


class Task:
    # ---------------------------------------------------------------- Summary -----------------------------------------
    """
    מחלקה לייצוג משימה.
    """
    # -------------------------------------------------------------- Constructor ---------------------------------------
    def __init__(self, name: str, description: str, status: TaskStatus = TaskStatus.PENDING,
                 urgency: UrgencyLevel = UrgencyLevel.MEDIUM, reporter: str = None, reporter_id: int = None):
        if not name.strip():
            raise ValueError("Name cannot be empty.")
        if not description.strip():
            raise ValueError("Description cannot be empty.")
        if not isinstance(status, TaskStatus):
            raise ValueError("Status must be an instance of TaskStatus Enum.")
        if not isinstance(urgency, UrgencyLevel):
            raise ValueError("Urgency must be an instance of UrgencyLevel Enum.")

        self._name = name
        self._description = description
        self._status = status
        self._urgency = urgency
        self._reporter = reporter
        self._reporter_id = reporter_id

        self._id = self.get_next_task_id()  # Assign the current counter value to the object

    # -------------------------------------------------------- Setters & Getters ---------------------------------------
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        if not value.strip():
            raise ValueError("Description cannot be empty.")
        self._description = value

    @property
    def status(self) -> TaskStatus:
        return self._status

    @status.setter
    def status(self, value: TaskStatus):
        if not isinstance(value, TaskStatus):
            raise ValueError("Status must be an instance of TaskStatus Enum.")
        self._status = value

    @property
    def urgency(self) -> UrgencyLevel:
        return self._urgency

    @urgency.setter
    def urgency(self, value: UrgencyLevel):
        if not isinstance(value, UrgencyLevel):
            raise ValueError("Urgency must be an instance of UrgencyLevel Enum.")
        self._urgency = value

    @property
    def reporter(self) -> str:
        return self._reporter

    @reporter.setter
    def reporter(self, value: str):
        if value and not isinstance(value, str):
            raise ValueError("Reporter must be a valid string.")
        self._reporter = value

    @property
    def reporter_id(self) -> int:
        return self._reporter_id

    @reporter_id.setter
    def reporter_id(self, value: int):
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("Reporter ID must be a positive integer.")
        self._reporter_id = value

    @property
    def task_id(self) -> int:
        return self._id

    # ---------------------------------------------------- Basic Functions ---------------------------------------------
    @staticmethod
    def get_next_task_id() -> int:
        """
        שולף את ה-ID האחרון שנרשם בטבלת Tasks ומחזיר את ה-ID הבא שיהיה.
        """
        try:
            with connect_database() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT MAX(id) FROM Tasks;")
                    last_id = cursor.fetchone()[0]

                    if last_id is None:
                        return 1  # אם אין משימות בטבלה, מתחילים מ-1
                    return last_id + 1  # מגדילים את ה-ID האחרון ב-1

        except mysql.connector.Error as e:
            print(f"Error retrieving last Task ID: {e}")
            return 1  # במקרה של שגיאה, מתחילים מ-1

    def __str__(self):
        """
        מייצגת את פרטי המטלה במחרוזת קריאה.
        """
        return (f"Task Details:\n"
                f"Task ID: {self.task_id}\n"
                f"Name: {self.name}\n"
                f"Description: {self.description}\n"
                f"Status: {self.status.name}\n"
                f"Urgency: {self.urgency.name}\n"
                f"Reporter: {self.reporter}\n"
                f"Reporter ID: {self.reporter_id if self.reporter_id else 'N/A'}")

    def update_status(self, new_status: TaskStatus):
        """
        מעדכנת את הסטטוס של המשימה.
        """
        if not isinstance(new_status, TaskStatus):
            raise ValueError("New status must be an instance of TaskStatus Enum.")
        self.status = new_status

    def update_urgency(self, new_urgency: UrgencyLevel):
        """
        מעדכנת את הדחיפות של המשימה.
        """
        if not isinstance(new_urgency, UrgencyLevel):
            raise ValueError("New urgency must be an instance of UrgencyLevel Enum.")
        self.urgency = new_urgency

    def update_task(self, **kwargs):  # ביצוע עדכון על סמך פרמטרים שניתנו
        """
        מעדכנת את פרטי המשימה לפי המאפיינים שסופקו.
        :param kwargs: מילון של ערכים לעדכון.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Task has no attribute '{key}'.")