import pandas as pd
import re


data = {
    "student_id": [
        101, 101, 101, 101, 101,
        102, 102, 102, 102,
        103, 103, 103, 103, 103,
        104, 104, 104, 104, 104
    ],
    "attendance_date": [
        "2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05",
        "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05",
        "2024-03-05", "2024-03-06", "2024-03-07", "2024-03-08", "2024-03-09",
        "2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05"
    ],
    "status": [
        "Absent", "Absent", "Absent", "Absent", "Present",
        "Absent", "Absent", "Absent", "Absent",
        "Absent", "Absent", "Absent", "Absent", "Absent",
        "Present", "Present", "Absent", "Present", "Present"
    ]
}
df = pd.DataFrame(data)
df["attendance_date"] = pd.to_datetime(df["attendance_date"])


students_data = {
    "student_id": [101, 102, 103, 104, 105],
    "student_name": ["Alice Johnson", "Bob Smith", "Charlie Brown", "David Lee", "Eva White"],
    "parent_email": ["alice_parent@example.com", "bob_parent@example.com", "invalid_email.com", "invalid_email.com", "eva_white@example.com"]
}
students_df = pd.DataFrame(students_data)


def long_absentees(df, min_days=3):
    df = df[df["status"] == "Absent"].copy()
    df["gap"] = df.groupby("student_id")["attendance_date"].diff().dt.days.ne(1).cumsum()
    result = df.groupby(["student_id", "gap"]).agg(
        absence_start_date=("attendance_date", "first"),
        absence_end_date=("attendance_date", "last"),
        total_absent_days=("attendance_date", "count")
    ).reset_index()
    return result[result["total_absent_days"] > min_days][["student_id", "absence_start_date", "absence_end_date", "total_absent_days"]]


def is_valid_email(email):
    pattern = r'^[A-Za-z_][A-Za-z0-9_]*@[a-zA-Z]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


long_absences = long_absentees(df, min_days=3)


final_df = long_absences.merge(students_df, on="student_id", how="left")


final_df["email"] = final_df["parent_email"].apply(lambda x: x if is_valid_email(x) else "")


final_df["msg"] = final_df.apply(
    lambda row: f"Dear Parent, your child {row['student_name']} was absent from {row['absence_start_date'].date()} to {row['absence_end_date'].date()} for {row['total_absent_days']} days. Please ensure their attendance improves."
    if row["email"] else "",
    axis=1
)


final_output = final_df[["student_id", "absence_start_date", "absence_end_date", "total_absent_days", "email", "msg"]]

print(final_output)
