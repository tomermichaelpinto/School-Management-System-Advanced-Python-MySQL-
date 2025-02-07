# ייבוא סיפריות עזר
from enum import Enum


class UrgencyLevel(Enum):
    """
    Enum לסוגי הדחיפות של דיווחים.
    """
    LOW = "Low urgency"         # דחיפות נמוכה
    MEDIUM = "Medium urgency"   # דחיפות בינונית
    HIGH = "High urgency"       # דחיפות גבוהה
    CRITICAL = "Critical urgency"

    def __str__(self):
        """
        מחזיר את ערך ה-Enum כמחרוזת.
        """
        return self.value
