# ייבוא סיפריות מחלקה
from Core.Manager import Manager, Analysis

# ייבוא של סיפריות עזר
import pandas as pd

# -------------------------------------------------- Summary  ----------------------------------------------------------
"""
בחלק זה נריץ את האלגוריתם של דרישת קבצי האקסל,
נייבא לכאן את כל הסיפריות מחלקה וסיפריות העזר לצורך הרצה,
נוציא הדפסות ונבצע ניתוחים שונים.
"""

# -------------------------------------------------- Function calls ----------------------------------------------------

Manager_Runner = Manager('Arik', 208110254, 32000)  # יצירת מופע של מחלקת Manager
analysis = Analysis(Manager_Runner)  # יצירת מופע של Analysis עם אובייקט Manager

print(analysis.Create_Object())

for i, (course_id, course) in enumerate(Manager_Runner.courses.items(), start=1):
    print(f"{i}. Course ID: {course_id}, Course Name: {course.course_name}")
print("============================================================================")

for i, (student_id, student) in enumerate(Manager_Runner.students.items(), start=1):
    print(f"{i}. Student ID: {student_id}, Name: {student.name}")
print("============================================================================")

for i, request in enumerate(Manager_Runner.requests, start=1):
    print(f"{i}. Request: {request}")
print("============================================================================")

for i, (teacher_id, teacher) in enumerate(Manager_Runner.teachers.items(), start=1):
    print(f"{i}. Teacher ID: {teacher_id}, Name: {teacher.name}")
print("============================================================================")

print(analysis.Excel_registration_report())

print(analysis.Data_reading_function())

print()
print(Manager_Runner)

# ---------------------------------------------------------------- Challenge questions ---------------------------------
"""
שאלות אתגר :
---------------

1. כיצד ניתן לייעל את האלגוריתם כך שיעבוד ביעילות גם עם 10 אלף רשומות?

-> תשובה :
   - שימוש בקבצי CSV במקום Excel: קבצי CSV מהירים יותר לעיבוד מכיוון שהם טקסטואלים ופשוטים.
   - קריאה חלקית של הקובץ: במקום לקרוא את כל הנתונים לזיכרון בבת אחת, ניתן להשתמש בפרמטרים כמו `chunksize` ב-pandas כדי לקרוא את הנתונים במנות קטנות.
     לדוגמה:
     ```python
     for chunk in pd.read_csv('data.csv', chunksize=1000):
         process_chunk(chunk)
     ```
   - שימוש במבני נתונים יעילים יותר: לדוגמה, אחסון נתוני מורים וקורסים במבני נתונים מהירים כמו `dict` או `set` עם גישה מהירה.
   - טיפול ברקע: אפשר להשתמש בריבוי תהליכים (`multiprocessing`) או שימוש בביצוע מקבילי (`concurrent.futures`) כדי לעבד את הרשומות במקביל.

2. מה קורה אם אין מורים זמינים? הצע פתרון יצירתי לבעיה.

-> תשובה :
   - פתיחת קורס מקוון: אם אין מורים זמינים, ניתן להציע לתלמידים קורסים מקוונים מוקלטים או בלמידה עצמית.
   - חלוקת עומסים: ניתן לבדוק אם יש מורים שמלמדים קורסים אחרים ולהציע להם ללמד קורס נוסף בשעות נוספות או בחלוקת השעות עם מורים אחרים.
   - שימוש במדריכים חיצוניים: גיוס מדריכים זמניים או מומחים מבחוץ (freelancers).
   - התאמת כיתות: שילוב תלמידים מקורסים דומים לכיתה אחת כדי למזער את הדרישה למורים.
   - דחיית הקורס: אם כל הפתרונות נכשלים, ניתן לעדכן את התלמידים ולדחות את הקורס לזמן שבו יהיו מורים זמינים.
"""


# ----------------------------------------------------------------------------------------------------------------------
def excel_to_csv(excel_file_path, csv_file_path):
    """
    הפונקציה excel_to_csv מקבלת את נתיב קובץ ה-Excel ואת נתיב הקובץ עבור קבצי ה-CSV.
    היא פותחת את קובץ ה-Excel בעזרת pandas.ExcelFile ומעבדת כל גיליון בקובץ.
    כל גיליון מומר לקובץ CSV נפרד עם שם גיליון כחלק מהשם הסופי של הקובץ (למשל, learning_center_project_data_Students.csv).
    הקובץ נשמר בפורמט CSV עם פרמטר index=False כדי שלא יתווסף עמודת אינדקס לקובץ.
    :param excel_file_path:
    :param csv_file_path:
    :return
    """
    excel_data = pd.ExcelFile(excel_file_path, engine="openpyxl")

    # מעבר על כל הגיליונות והמרתם לקובצי CSV
    for sheet_name in excel_data.sheet_names:
        df = excel_data.parse(sheet_name)
        sheet_csv_path = f"{csv_file_path}_{sheet_name}.csv"  # שם הקובץ יצוין לפי שם הגיליון
        df.to_csv(sheet_csv_path, index=False)  # המרת הגיליון לקובץ CSV
        print(f"Converted {sheet_name} to {sheet_csv_path}")


"""
# דוגמה לשימוש:
excel_file = 'learning_center_project_data.xlsx'  # הקובץ שאתה רוצה להמיר
csv_file_prefix = 'learning_center_project_data'  # שם קובץ בסיסי להמרה

excel_to_csv(excel_file, csv_file_prefix)
"""

# ======================================================================================================================
# ---------------------------------------------------------------- Challenge questions ---------------------------------
"""
שאלות אתגר :
---------------

1. כיצד ניתן לייעל את האלגוריתם כך שיעבוד ביעילות גם עם 10 אלף רשומות?

-> תשובה :
   - שימוש בקבצי CSV במקום Excel: קבצי CSV מהירים יותר לעיבוד מכיוון שהם טקסטואלים ופשוטים.
   - קריאה חלקית של הקובץ: במקום לקרוא את כל הנתונים לזיכרון בבת אחת, ניתן להשתמש בפרמטרים כמו `chunksize` ב-pandas כדי לקרוא את הנתונים במנות קטנות.
     לדוגמה:
     ```python
     for chunk in pd.read_csv('data.csv', chunksize=1000):
         process_chunk(chunk)
     ```
   - שימוש במבני נתונים יעילים יותר: לדוגמה, אחסון נתוני מורים וקורסים במבני נתונים מהירים כמו `dict` או `set` עם גישה מהירה.
   - טיפול ברקע: אפשר להשתמש בריבוי תהליכים (`multiprocessing`) או שימוש בביצוע מקבילי (`concurrent.futures`) כדי לעבד את הרשומות במקביל.

2. מה קורה אם אין מורים זמינים? הצע פתרון יצירתי לבעיה.

-> תשובה :
   - פתיחת קורס מקוון: אם אין מורים זמינים, ניתן להציע לתלמידים קורסים מקוונים מוקלטים או בלמידה עצמית.
   - חלוקת עומסים: ניתן לבדוק אם יש מורים שמלמדים קורסים אחרים ולהציע להם ללמד קורס נוסף בשעות נוספות או בחלוקת השעות עם מורים אחרים.
   - שימוש במדריכים חיצוניים: גיוס מדריכים זמניים או מומחים מבחוץ (freelancers).
   - התאמת כיתות: שילוב תלמידים מקורסים דומים לכיתה אחת כדי למזער את הדרישה למורים.
   - דחיית הקורס: אם כל הפתרונות נכשלים, ניתן לעדכן את התלמידים ולדחות את הקורס לזמן שבו יהיו מורים זמינים.
"""

# ======================================================================================================================
# ----------------------------------------------------------------------------------------------------------------------

# def excel_to_csv(excel_file_path, csv_file_path):
#     """
#     הפונקציה excel_to_csv מקבלת את נתיב קובץ ה-Excel ואת נתיב הקובץ עבור קבצי ה-CSV.
#     היא פותחת את קובץ ה-Excel בעזרת pandas.ExcelFile ומעבדת כל גיליון בקובץ.
#     כל גיליון מומר לקובץ CSV נפרד עם שם גיליון כחלק מהשם הסופי של הקובץ (למשל, learning_center_project_data_Students.csv).
#     הקובץ נשמר בפורמט CSV עם פרמטר index=False כדי שלא יתווסף עמודת אינדקס לקובץ.
#     :param excel_file_path:
#     :param csv_file_path:
#     :return
#     """
#     excel_data = pd.ExcelFile(excel_file_path, engine="openpyxl")
#
#     # מעבר על כל הגיליונות והמרתם לקובצי CSV
#     for sheet_name in excel_data.sheet_names:
#         df = excel_data.parse(sheet_name)
#         sheet_csv_path = f"{csv_file_path}_{sheet_name}.csv"  # שם הקובץ יצוין לפי שם הגיליון
#         df.to_csv(sheet_csv_path, index=False)  # המרת הגיליון לקובץ CSV
#         print(f"Converted {sheet_name} to {sheet_csv_path}")


"""
# דוגמה לשימוש:
excel_file = 'learning_center_project_data.xlsx'  # הקובץ שאתה רוצה להמיר
csv_file_prefix = 'learning_center_project_data'  # שם קובץ בסיסי להמרה

excel_to_csv(excel_file, csv_file_prefix)
"""
