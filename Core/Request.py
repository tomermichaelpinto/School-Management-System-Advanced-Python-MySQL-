# ייבוא סיפריות עזר
from datetime import datetime


class Request:
    # ---------------------------------------------------------------- Summary -----------------------------------------
    """
    מחלקת ניהול בקשת רישום לקורס.
    """
    # הודעות שגיאה
    INVALID_STUDENT_MSG = "Student must be an integer representing a valid student ID."
    INVALID_COURSE_MSG = "Course ID must be an integer."
    INVALID_DATE_MSG = "Request date must be a datetime object."

    # משתנה סטטי למעקב אחרי מזהי הבקשות
    counter = 0

    # -------------------------------------------------------------- Constructor ---------------------------------------
    def __init__(self, course_id: int, student_id: int, request_date: datetime = None):
        """
        אתחול בקשת רישום לקורס עם מזהה ייחודי, מזהה קורס, מזהה סטודנט ותאריך הבקשה.
        """
        if not isinstance(course_id, int):
            raise ValueError(self.INVALID_COURSE_MSG)
        if not isinstance(student_id, int):
            raise ValueError(self.INVALID_STUDENT_MSG)
        if request_date is not None and not isinstance(request_date, datetime):
            raise ValueError(self.INVALID_DATE_MSG)

        # אם לא עבר תאריך, הגדר את ברירת המחדל
        self._request_date = request_date if request_date else datetime.now()

        # עדכון מזהה ייחודי
        self._waitlist_id = Request.counter
        Request.counter += 1

        # אתחול שאר המשתנים
        self._course_id = course_id
        self._student_id = student_id

    # -------------------------------------------------------- Setters & Getters ---------------------------------------
    @property
    def waitlist_id(self) -> int:
        """מחזיר את מזהה רשימת ההמתנה."""
        return self._waitlist_id

    @property
    def course_id(self) -> int:
        """מחזיר את מזהה הקורס."""
        return self._course_id

    @course_id.setter
    def course_id(self, value: int):
        if not isinstance(value, int):
            raise ValueError(self.INVALID_COURSE_MSG)
        self._course_id = value

    @property
    def student_id(self) -> int:
        """מחזיר את מזהה הסטודנט."""
        return self._student_id

    @student_id.setter
    def student_id(self, value: int):
        if not isinstance(value, int):
            raise ValueError(self.INVALID_STUDENT_MSG)
        self._student_id = value

    @property
    def request_date(self) -> str:
        """מחזיר את תאריך הבקשה בפורמט dd/mm/yyyy."""
        return self._request_date.strftime('%d/%m/%Y')  # מחזיר כ-string בפורמט הדחוי

    @request_date.setter
    def request_date(self, value: datetime):
        if isinstance(value, datetime):
            self._request_date = value  # שמירה כ- datetime
        elif isinstance(value, str):
            try:
                # המרת מחרוזת לתאריך
                self._request_date = datetime.strptime(value, '%d/%m/%Y')
            except ValueError:
                raise ValueError(self.INVALID_DATE_MSG)
        else:
            raise ValueError(self.INVALID_DATE_MSG)

    # ---------------------------------------------------- Basic Functions ---------------------------------------------
    # Base Functions
    def __str__(self) -> str:
        """
        מייצגת את פרטי הבקשה במחרוזת קריאה.
        """
        return (f"Registration Request Details:\n"
                f"Waitlist ID: {self._waitlist_id}\n"
                f"Course ID: {self._course_id}\n"
                f"Student ID: {self._student_id}\n"
                f"Request Date: {self._request_date}")

    def __eq__(self, other) -> bool:
        """
        השוואת שני אובייקטי בקשות.
        """
        if isinstance(other, Request):
            return self._course_id == other._course_id and self._student_id == other._student_id
        return False

    def __hash__(self) -> int:
        """
        חישוב ערך hash עבור אובייקט הבקשה.
        """
        return hash((self._waitlist_id, self._course_id, self._student_id))
