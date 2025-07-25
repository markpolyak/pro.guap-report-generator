from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from .schemas import ReportRequest

def generate_report(data: ReportRequest) -> Document:
    doc = Document()
    
    # ======================== 第一部分：机构信息 ========================
    # 设置整体页面边距
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
    
    # 设置全局字体
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(10.5)  # 五号字体
    # 设置中文字体支持
    font.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    
    # 1. 学校缩写 - 居中，小四，加粗
    university_abbr = doc.add_paragraph("ГУАП")
    university_abbr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    university_abbr.runs[0].font.size = Pt(12)  # 小四
    university_abbr.runs[0].bold = True
    
    # 2. 教育部名称 - 居中，五号，单倍行距
    ministry = doc.add_paragraph("МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ")
    ministry.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ministry.runs[0].font.size = Pt(10.5)  # 五号
    ministry.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    
    # 3. 机构类型 - 居中，13pt，单倍行距
    org_type = doc.add_paragraph("федеральное государственное автономное образовательное учреждение высшего образования")
    org_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    org_type.runs[0].font.size = Pt(13)
    org_type.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    
    # 4. 学校全名 - 居中，小四，单倍行距
    org_name = doc.add_paragraph("«САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ АЭРОКОСМИЧЕСКОГО ПРИБОРОСТРОЕНИЯ»")
    org_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    org_name.runs[0].font.size = Pt(12)  # 小四
    org_name.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    
    # 5. 添加下划线（在机构信息下方）
    underline_paragraph = doc.add_paragraph()
    underline_run = underline_paragraph.add_run()
    underline_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 创建下划线边框
    bottom_border = OxmlElement('w:bottom')
    bottom_border.set(qn('w:val'), 'single')
    bottom_border.set(qn('w:sz'), '8')
    bottom_border.set(qn('w:space'), '1')
    bottom_border.set(qn('w:color'), 'auto')
    
    pPr = underline_paragraph._element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    pBdr.append(bottom_border)
    pPr.append(pBdr)
    
    # 6. 系信息 - 居中，五号
    if data.organisation.department:
        # 提取部门编号
        dept_number = ''.join(filter(str.isdigit, data.organisation.department))
        if not dept_number:
            dept_number = "43"  # 默认值
        
        dept_paragraph = doc.add_paragraph(f"КАФЕДРА № {dept_number}")
        dept_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        dept_paragraph.runs[0].font.size = Pt(10.5)  # 五号
    
    # 添加空行
    doc.add_paragraph()
    
    # ======================== 第二部分：报告标题 ========================
    # 7. 报告标题 - 左对齐，五号
    title_paragraph = doc.add_paragraph("ОТЧЕТ")
    title_paragraph.runs[0].font.size = Pt(10.5)  # 五号
    
    # 8. 保护状态 - 左对齐，五号
    status_paragraph = doc.add_paragraph("ЗАЩИЩЕН С ОЦЕНКОЙ")
    status_paragraph.runs[0].font.size = Pt(10.5)  # 五号
    
    # 9. 教师标题 - 左对齐，五号
    teacher_title = doc.add_paragraph("ПРЕПОДАВАТЕЛЬ")
    teacher_title.runs[0].font.size = Pt(10.5)  # 五号
    
    # 10. 教师信息表格（三部分均匀分布）
    teacher_table = doc.add_table(rows=1, cols=3)
    teacher_table.autofit = False
    teacher_table.style = 'Table Grid'  # 添加表格边框
    
    # 设置列宽
    widths = [Inches(2.5), Inches(1.5), Inches(2.5)]
    for i, width in enumerate(widths):
        teacher_table.columns[i].width = width
    
    # 填充内容
    teacher = data.report.teacher
    teacher_table.cell(0, 0).text = "должность, уч. степень, звание"
    teacher_table.cell(0, 1).text = "подпись, дата"
    teacher_table.cell(0, 2).text = "инициалы, фамилия"
    
    # 设置单元格格式
    for cell in teacher_table.row_cells(0):
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.font.size = Pt(10)  # 10号字体
    
    # 添加空行
    doc.add_paragraph()
    
    # ======================== 第三部分：工作信息 ========================
    # 11. 报告类型 - 居中，四号
    # 根据任务类型选择正确的报告名称
    task_type = data.report.task_type.lower()
    report_type_name = ""
    if "лабораторн" in task_type:
        report_type_name = "ЛАБОРАТОРНОЙ"
    elif "курсов" in task_type:
        report_type_name = "КУРСОВОЙ"
    elif "диплом" in task_type:
        report_type_name = "ДИПЛОМНОЙ"
    else:
        report_type_name = task_type.upper()
    
    report_type = doc.add_paragraph(f"ОТЧЕТ О {report_type_name} РАБОТЕ №")
    report_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    report_type.runs[0].font.size = Pt(14)  # 四号
    
    # 12. 任务名称 - 居中，四号
    task_name = doc.add_paragraph(f"«{data.report.task_name}»")
    task_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    task_name.runs[0].font.size = Pt(14)  # 四号
    
    # 13. 课程名称 - 居中，四号
    subject_name = doc.add_paragraph(f"по курсу: {data.report.subject_name}")
    subject_name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subject_name.runs[0].font.size = Pt(14)  # 四号
    
    # 14. 选题号 - 居中，小四
    variant = doc.add_paragraph("ВАРИАНТ №")
    variant.alignment = WD_ALIGN_PARAGRAPH.CENTER
    variant.runs[0].font.size = Pt(12)  # 小四
    
    # 添加空行
    doc.add_paragraph("\n")
    
    # ======================== 第四部分：学生信息 ========================
    # 15. 学生标题 - 左对齐，五号
    student_title = doc.add_paragraph("РАБОТУ ВЫПОЛНИЛ")
    student_title.runs[0].font.size = Pt(10.5)  # 五号
    
    # 16. 学生信息表格（四部分均匀分布）
    student_table = doc.add_table(rows=1, cols=4)
    student_table.autofit = False
    student_table.style = 'Table Grid'  # 添加表格边框
    
    # 设置列宽
    widths = [Inches(1.5), Inches(1.0), Inches(1.5), Inches(2.0)]
    for i, width in enumerate(widths):
        student_table.columns[i].width = width
    
    # 填充内容
    student = data.student
    # 格式化学生姓名
    student_initials = f"{student.surname} {student.name[0]}."
    if student.patronymic:
        student_initials += f"{student.patronymic[0]}."
    
    student_table.cell(0, 0).text = "СТУДЕНТ гр. №"
    student_table.cell(0, 1).text = student.group if student.group else ""
    student_table.cell(0, 2).text = "подпись, дата"
    student_table.cell(0, 3).text = student_initials
    
    # 设置单元格格式
    # 第一列：小四
    for paragraph in student_table.cell(0, 0).paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(12)  # 小四
    
    # 其他列：10号字体
    for col in [1, 2, 3]:
        for paragraph in student_table.cell(0, col).paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(10)
    
    # 居中所有单元格内容
    for cell in student_table.row_cells(0):
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 添加空行
    doc.add_paragraph("\n" * 2)
    
    # ======================== 第五部分：页脚 ========================
    # 17. 位置和日期 - 居中，五号
    footer = doc.add_paragraph("Санкт-Петербург 2025")
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.runs[0].font.size = Pt(10.5)  # 五号
    
    # 添加分页符
    doc.add_page_break()
    
    # ======================== 第六部分：报告结构 ========================
    if data.report.report_structure:
        # 添加标题
        structure_title = doc.add_paragraph("Структура отчета:")
        structure_title.runs[0].font.bold = True
        structure_title.runs[0].font.size = Pt(12)
        
        # 添加报告结构列表
        for section in data.report.report_structure:
            p = doc.add_paragraph(section, style='ListBullet')
            p.runs[0].font.size = Pt(12)
            # 设置列表格式
            p.paragraph_format.left_indent = Inches(0.5)
    
    return doc