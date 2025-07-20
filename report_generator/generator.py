from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .schemas import ReportRequest

# 默认机构信息
DEFAULT_ORGANISATION = {
    "founder": "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ",
    "name": "федеральное государственное автономное образовательное учреждение высшего образования «САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ АЭРОКОСМИЧЕСКОГО ПРИБОРОСТРОЕНИЯ»"
}

def generate_report(data: ReportRequest) -> Document:
    doc = Document()
    
    # 设置默认字体
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(14)
    
    # 添加标题
    title = doc.add_paragraph()
    title_run = title.add_run("ОТЧЕТ")
    title_run.bold = True
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 添加机构信息
    org = data.organisation or {}
    founder = org.founder or DEFAULT_ORGANISATION["founder"]
    name = org.name or DEFAULT_ORGANISATION["name"]
    
    doc.add_paragraph(f"Учредитель: {founder}")
    doc.add_paragraph(f"Учебное заведение: {name}")
    
    if org.faculty:
        doc.add_paragraph(f"Институт: {org.faculty}")
    if org.department:
        doc.add_paragraph(f"Кафедра: {org.department}")
    
    # 添加学生信息
    student = data.student
    student_info = f"{student.surname} {student.name}"
    if student.patronymic:
        student_info += f" {student.patronymic}"
    doc.add_paragraph(f"Студент: {student_info}")
    
    if student.group:
        doc.add_paragraph(f"Группа: {student.group}")
    if student.identity_card:
        doc.add_paragraph(f"Номер студенческого билета: {student.identity_card}")
    
    # 添加报告信息
    report = data.report
    doc.add_paragraph(f"Дисциплина: {report.subject_name}")
    doc.add_paragraph(f"Тип работы: {report.task_type}")
    doc.add_paragraph(f"Название работы: {report.task_name}")
    
    teacher = report.teacher
    teacher_info = f"{teacher.surname} {teacher.name[0]}."
    if teacher.patronymic:
        teacher_info += f"{teacher.patronymic[0]}."
    doc.add_paragraph(f"Преподаватель: {teacher_info} ({teacher.status})")
    if teacher.status:
        doc.add_paragraph(f"Статус: {teacher.status}")
        
    # 添加报告结构
    if report.report_structure:
        doc.add_paragraph("\nСтруктура отчета:")
        for section in report.report_structure:
            doc.add_paragraph(section, style='ListBullet')
    
    return doc