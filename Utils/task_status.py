# ייבוא סיפריות עזר
from enum import Enum


class TaskStatus(Enum):
    """
    Enum לסטטוס של משימה.
    """
    PENDING = "Pending"          # בהמתנה
    IN_PROGRESS = "In Progress"  # בביצוע
    COMPLETED = "Completed"      # הושלם
