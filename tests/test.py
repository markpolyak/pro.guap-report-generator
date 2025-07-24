import pytest
import main
import json
import os
import tempfile
from datetime import datetime
import sys

# 测试数据
test_data = {
    "organisation": {
        "founder": "МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ",
        "name": "федеральное государственное автономное образовательное учреждение высшего образования «САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ АЭРОКОСМИЧЕСКОГО ПРИБОРОСТРОЕНИЯ»",
        "faculty": "ИНСТИТУТ НЕПРЕРЫВНОГО И ДИСТАНЦИОННОГО ОБРАЗОВАНИЯ",
        "department": "КАФЕДРА информационных технологий и программной инженерии"
    },
    "student": {
        "name": "Иван",
        "surname": "Иванов", 
        "patronymic": "Иванович",
        "group": "4931"
    },
    "report": {
        "subject_name": "Операционные системы",
        "task_name": "ЛР1. Знакомство с командным интерпретатором bash",
        "task_type": "Лабораторная работа",
        "teacher": {
            "name": "Юлия",
            "surname": "Антохина",
            "patronymic": "Анатольевна", 
            "status": "Ректор, д.т.н., проф."
        },
        "report_structure": [
            "Цель", "Задание", "Результат выполнения", "Выводы"
        ]
    }
}

@pytest.fixture
def setup_test_files():
    """创建临时测试文件"""
    # 创建临时目录
    tmp_dir = tempfile.mkdtemp()
    json_path = os.path.join(tmp_dir, 'test.json')
    
    # 创建测试JSON文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False)
    
    # 创建空模板文件
    template_path = os.path.join(tmp_dir, 'template.docx')
    open(template_path, 'a').close()
    
    yield {
        "json_path": json_path,
        "template_path": template_path,
        "output_path": os.path.join(tmp_dir, 'output.docx'),
        "tmp_dir": tmp_dir
    }
    
    # 清理临时文件
    for f in [json_path, template_path]:
        if os.path.exists(f):
            os.remove(f)
    os.rmdir(tmp_dir)

def test_task_title(setup_test_files):
    """测试任务标题是否正确加载"""
    data_docx = main.load_data_from_json(setup_test_files["json_path"])
    assert data_docx['title'] == "ЛР1. Знакомство с командным интерпретатором bash"

def test_teacher_status(setup_test_files):
    """测试教师状态是否正确"""
    data_docx = main.load_data_from_json(setup_test_files["json_path"])
    assert data_docx['position'] == "Ректор, д.т.н., проф."

def test_teacher_name(setup_test_files):
    """测试教师姓名是否正确"""
    data_docx = main.load_data_from_json(setup_test_files["json_path"])
    assert data_docx['t_name'] == "Антохина Юлия Анатольевна"

def test_subject_data(setup_test_files):
    """测试学科数据是否正确"""
    data_docx = main.load_data_from_json(setup_test_files["json_path"])
    assert data_docx['subject'] == "Операционные системы"

def test_student_group(setup_test_files):
    """测试学生组别是否正确"""
    data_docx = main.load_data_from_json(setup_test_files["json_path"])
    assert data_docx['class'] == "4931"

def test_student_name(setup_test_files):
    """测试学生姓名是否正确"""
    data_docx = main.load_data_from_json(setup_test_files["json_path"])
    assert data_docx['st_name'] == "Иванов Иван Иванович"

def test_time_format(setup_test_files):
    """测试时间格式是否正确"""
    data_docx = main.load_data_from_json(setup_test_files["json_path"])
    time_parts = data_docx['time'].split('/')
    assert len(time_parts) == 3
    datetime.strptime(data_docx['time'], '%Y/%m/%d')

def test_missing_file():
    """测试JSON文件不存在的错误处理"""
    with pytest.raises(FileNotFoundError):
        main.load_data_from_json('nonexistent.json')

def test_missing_fields():
    """测试缺少必要字段的处理"""
    # 创建临时的不完整JSON文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump({"student": {"name": "Test"}}, f, ensure_ascii=False)
        temp_file = f.name
    
    try:
        with pytest.raises(KeyError):
            main.load_data_from_json(temp_file)
    finally:
        os.unlink(temp_file)

def test_document_generation(setup_test_files):
    """测试文档生成功能"""
    result = main.generate_document(
        template_path=setup_test_files["template_path"],
        output_path=setup_test_files["output_path"],
        json_file_path=setup_test_files["json_path"]
    )
    assert result is True
    assert os.path.exists(setup_test_files["output_path"])

def test_missing_template(setup_test_files):
    """测试模板文件不存在的处理"""
    result = main.generate_document(
        template_path="nonexistent_template.docx",
        output_path=setup_test_files["output_path"],
        json_file_path=setup_test_files["json_path"]
    )
    assert result is False
