# ייבוא סיפריות עזר
import re
from abc import ABC, abstractmethod


class Person(ABC):
    # ---------------------------------------------------------------- Summary -----------------------------------------
    """
    מחלקת אב עבור אנשים, מכילה פרטי מידע בסיסיים כמו שם ומזהה.
    """

    # -------------------------------------------------------------- Constructor ---------------------------------------
    def __init__(self, name: str, id: int):
        self.__name = name  # משתמש ב-setter של שם
        self.__id = id  # משתמש ב-setter של מזהה

    # -------------------------------------------------------- Setters & Getters ---------------------------------------
    @property
    def name(self) -> str:
        return self.__name

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

        self.__name = val

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, val: int):
        """
        מאמתת ומגדירה את ה-ID.
        - חייב להיות מספר שלם חיובי.
        """
        if not isinstance(val, int) or val <= 0:
            raise ValueError("Invalid ID. ID must be a positive integer.")

        self.__id = val

    # ---------------------------------------------------- Basic Functions ---------------------------------------------
    @abstractmethod
    def __str__(self):
        """
        מתודה אבסטרקטית להדפסת פרטי האדם בצורה קריאה.
        כל מחלקה תורשת תצטרך לממש מתודה זו.
        """
        pass

    def __eq__(self, other):
        """
        משווה בין שני אובייקטי Person על פי המזהה (id).
        """
        if isinstance(other, Person):
            return self.__id == other.__id
        return False

    def __hash__(self):
        """
        מחזיר את ה-hash של האובייקט Person. ה-hash מבוסס על המזהה (id).
        """
        return hash(self.__id)
