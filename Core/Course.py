# ייבוא סיפריות מחלקה
from Request import Request

# ייבוא סיפריות עזר
from queue import Queue
from typing import Set, Dict, Union, List


class Course:
    # ---------------------------------------------------------------- Summary -----------------------------------------
    """
    מחלקת קורס המייצגת קורס, כולל שם הקורס, מזהה הקורס, מזהה המורה, קיבולת הקורס,
    מספר הסטודנטים הרשומים, מורים, סטודנטים ורשימת המתנה.
    """

    # -------------------------------------------------------------- Constructor ---------------------------------------
    Age_Global = 10

    def __init__(self, course_name: str, course_id: int, teacher_id: int, capacity: int, registered_students: int,
                 course_age: int = Age_Global):
        """
        יוצר אובייקט קורס חדש עם שם, מזהה קורס, מזהה מורה, קיבולת הקורס ומספר הסטודנטים הרשומים.
        """

        self._course_name: str = course_name  # שם קורס
        self._course_id: int = course_id  # מס קורס
        self._teacher_id: int = teacher_id  # מס מורה שמלמדת את הקורס
        self._capacity: int = capacity  # קיבולת הסטודנטים שניתן לרשום
        self._course_age: int = course_age  # ייעוד גיל הקורס
        self._course_cost: float = 500  # עלות פתיחת הקורס - עלות קבועה

        # אם לא הוזן גיל, נעדכן את הגיל הגלובלי
        if course_age == Course.Age_Global:
            Course.Age_Global += 1  # גיל הגלובלי יגדל ב-1

        # Set & Dict
        self._requests: Queue[Request] = Queue()  # תלמידים שביקשו להירשם לקורס (נמצאים ברשימת המתנה)
        self._teachers: Set[str] = set()  # רשימת שמות המורים שמלמדים את הקורס
        self._students: Set[str] = set()  # רשימת שמות הסטודנטים שרשומים
        self._registered_students: int = registered_students  # מספר הסטודנטים הרשומים
        self._assignments: Dict[str, Union[str, List[str]]] = {}  # רשימת משימות לכל סטודנט חיפוש לפי שם סטונדט, שם סטודנט -> משימות
        self._Personal_schedules: Dict[str, Union[str, List[str]]] = {}  # לוח זמנים אישי בקורס, שם סטודנט -> לוח זמנים
        self._grades: Dict[str, Union[float, List[float]]] = {}  # רשימת ציונים לפי שמות הסטונים, שם סטודנט -> ציונים

    # -------------------------------------------------------- Setters & Getters ---------------------------------------
    @property
    def course_name(self) -> str:
        return self._course_name

    @course_name.setter
    def course_name(self, value: str):
        if not isinstance(value, str):
            raise ValueError("Course name must be a string.")
        self._course_name = value

    @property
    def course_id(self) -> int:
        return self._course_id

    @course_id.setter
    def course_id(self, value: int):
        if not isinstance(value, int):
            raise ValueError("Course ID must be an integer.")
        self._course_id = value

    @property
    def teacher_id(self) -> int:
        return self._teacher_id

    @teacher_id.setter
    def teacher_id(self, value: int):
        if not isinstance(value, int):
            raise ValueError("Teacher ID must be an integer.")
        self._teacher_id = value

    @property
    def capacity(self) -> int:
        return self._capacity

    @capacity.setter
    def capacity(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self._capacity = value

    @property
    def registered_students(self) -> int:
        return self._registered_students

    @registered_students.setter
    def registered_students(self, value: int):

        if not isinstance(value, int) or value < 0:
            raise ValueError("Registered students count must be a non-negative integer.")

        if value > self._capacity:
            raise ValueError("Registered students cannot exceed course capacity.")
        self._registered_students = value

    @property
    def teachers(self) -> Set[str]:
        return self._teachers

    @property
    def Requests(self) -> Queue:
        return self._requests

    @property
    def students(self) -> set[str]:
        return self._students

    @property
    def assignments(self) -> dict[str, str]:
        return self._assignments

    @property
    def personal_schedules(self) -> dict[str, str]:
        return self._Personal_schedules

    @property
    def course_cost(self) -> float:
        return self._course_cost

    @course_cost.setter
    def course_cost(self, cost: float):
        if cost < 0:
            raise ValueError("Course cost must be non-negative.")
        self._course_cost = cost

    @property
    def course_age(self) -> int:
        return self._course_age

    @course_age.setter
    def course_age(self, age: int):
        if not isinstance(age, int) or age <= 0:
            raise ValueError("Course age must be non-negative.")
        self._course_age = age

    @property
    def grades(self) -> Dict[str, float]:
        return self._grades

    # ---------------------------------------------------- Basic Functions ---------------------------------------------
    def __str__(self) -> str:
        """
        מציג את פרטי הקורס בצורה קריאה.
        """
        teachers_list = ', '.join([teacher for teacher in self._teachers])
        return (f"Course Name: {self._course_name}, ID: {self._course_id}, "
                f"Teacher ID: {self._teacher_id}, Capacity: {self._capacity}, "
                f"Registered Students: {self._registered_students}, Teachers: {teachers_list}")

    def __eq__(self, other) -> bool:
        """
        משווה בין שני אובייקטי קורסים. השוואה מתבצעת לפי מזהה הקורס (course_id).
        """
        if isinstance(other, Course):
            return self._course_id == other._course_id
        return False

    def __hash__(self) -> int:
        """
        מחזיר את ה-hash של אובייקט הקורס. ה-hash מבוסס על מזהה הקורס (course_id).
        """
        return hash(self._course_id)

    # ------------------------------------------------------ Insert and delete functions -------------------------------
    def add_assignment(self, student: str, assignment: str):
        """
        מוסיף משימה לסטודנט בקורס.
        """
        if not student or not assignment:
            print("Student name and assignment must be provided.")
            return

        self._assignments[student] = assignment
        print(f"Assignment '{assignment}' has been added for student {student}.")

    def add_schedule(self, schedule: str, student: str):
        """
        מוסיף לוח זמנים לסטודנט בקורס.
        """
        if not student or not schedule:
            print("Student name and schedule must be provided.")
            return

        self._Personal_schedules[student] = schedule
        print(f"Schedule '{schedule}' has been added for student {student}.")

    def remove_schedule(self, schedule: str, student: str):
        """
        מסירה את לוח הזמנים של הסטודנט מהקורס.
        """
        if student in self._Personal_schedules:
            # אם יש לוח זמנים עבור הסטודנט, נמחק אותו
            if self._Personal_schedules[student] == schedule:
                del self._Personal_schedules[student]  # הסרה של לוח הזמנים עבור הסטודנט
                print(f"Schedule '{schedule}' has been removed for student {student}.")
            else:
                print(f"Schedule '{schedule}' does not match the current schedule for student {student}.")
        else:
            print(f"Student {student} does not have a schedule in this course.")

    def remove_assignment(self, assignment: str):
        """
        מסירה את המשימה מכל הסטודנטים בקורס.
        """
        # מסירה את כל הסטודנטים שהוקצתה להם המשימה
        students_to_remove = [student_id for student_id, task in self._assignments.items() if task == assignment]
        for student_id in students_to_remove:
            self._assignments.pop(student_id, None)  # מסירה את המשימה עבור כל סטודנט
        print(f"Assignment '{assignment}' has been removed from all students in the course '{self._course_name}'.")

    def add_teacher(self, teacher: str):
        # המרת את שם המורה לאותיות קטנות
        teacher = teacher.lower()

        # בדיקה אם המורה נמצא כבר בקורס
        if any(existing_teacher == teacher for existing_teacher in self._teachers):
            print(f"Teacher {teacher} is already assigned to the course {self._course_name}.")
        else:
            self._teachers.add(teacher)
            print(f"Teacher {teacher} has been added to the course {self._course_name}.")

    def remove_teacher(self, teacher: str):
        # המרת את שם המורה לאותיות קטנות
        teacher = teacher.lower()

        # בדיקה אם המורה נמצא בקורס
        if teacher in self._teachers:
            self._teachers.discard(teacher)
            print(f"Teacher {teacher} has been removed from the course {self._course_name}.")
            print(f"Course {self._course_name} now has {len(self._teachers)} teachers.")
        else:
            print(f"Teacher {teacher} is not assigned to the course {self._course_name}.")

    def add_student(self, student: str):
        # המרת את שם התלמיד לאותיות קטנות
        student = student.lower()

        # בדיקה אם התלמיד כבר רשום בקורס
        if student in self.students:
            return f"Student {student} is already registered in the course {self.course_name}."
        else:
            # אם התלמיד לא רשום, נוסיף אותו לרשימה
            if self.registered_students < self._capacity:
                self.students.add(student)
                self.registered_students += 1  # עדכון מספר הסטודנטים הרשומים בקורס
                return (f"Student {student} has been registered in the course {self.course_name} "
                        f"Course {self._course_name} now has {self._registered_students} registered students.")
            else:
                return f"Cannot add student {student}. Course {self._course_name} is at full capacity."

    def remove_student(self, student: str):
        # המר את השם לאותיות קטנות
        student = student.lower()

        # בדיקה אם התלמיד רשום בקורס
        if student in self._students:
            self.students.discard(student)
            self.registered_students -= 1
            print(f"Student {student} has been removed from the course {self.course_name}.")
            print(f"Course {self.course_name} now has {self.registered_students} registered students.")
        else:
            print(f"Student {student} is not registered in the course {self.course_name}.")

    # ------------------------------------------------------ Advanced Functions ----------------------------------------
    def remove_registration_request(self, re: Request):  # מתודת עזר למחלקות האחרות
        """
        מסיר את הבקשה של תלמיד מהקורס אם הוא נמצא ברשימת הבקשות.
        אם התלמיד עבר לרשימת הסטודנטים, עדכון הסטטוס.
        """
        # בדוק אם התלמיד נמצא בתור
        if re in self.Requests.queue:
            self.Requests.queue.remove(re)
            return f"Student {re.student_id} has been removed from the waitlist for course {self.course_name}."

        else:
            return f"Student {re.student_id} was not found in the waitlist for course {self.course_name}."
