from pydantic import BaseModel, Field
from typing import List, Optional

class Organisation(BaseModel):
    founder: Optional[str] = "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ"
    name: Optional[str] = "федеральное государственное автономное образовательное учреждение высшего образования «САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ АЭРОКОСМИЧЕСКОГО ПРИБОРОСТРОЕНИЯ»"
    faculty: Optional[str] = None
    department: Optional[str] = None

class Student(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    group: Optional[str] = None
    identity_card: Optional[str] = Field(None, alias="identity_card")

class Teacher(BaseModel):
    name: str
    surname: str
    patronymic: Optional[str] = None
    status: str

class Report(BaseModel):
    subject_name: str
    task_name: str
    task_type: str
    teacher: Teacher
    report_structure: Optional[List[str]] = None

class ReportRequest(BaseModel):
    organisation: Organisation
    student: Student
    report: Report