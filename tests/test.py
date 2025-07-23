import pytest
import main
import json
import os
import tempfile
from datetime import datetime
from docxtpl import DocxTemplate
from docx import Document
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

def test_1():
    """测试任务标题是否正确加载"""
    try:
        data_docx = main.load_data_from_json('2.txt')
        if 'title' not in data_docx or not data_docx['title']:
            assert False, "Проверьте заголовок"
        if data_docx['title'] != "ЛР1. Знакомство с командным интерпретатором bash":
            assert False, "Проверьте заголовок"
    except Exception:
        assert False, "Проверьте заголовок"

def test_2():
    """测试教师状态是否正确"""
    try:
        data_docx = main.load_data_from_json('2.txt')
        if 'position' not in data_docx or not data_docx['position']:
            assert False, "Статус преподавателя"
        if data_docx['position'] != "Ректор, д.т.н., проф.":
            assert False, "Статус преподавателя"
    except Exception:
        assert False, "Статус преподавателя"

def test_3():
    """测试教师姓名是否正确"""
    try:
        data_docx = main.load_data_from_json('2.txt')
        if 't_name' not in data_docx or not data_docx['t_name']:
            assert False, "ФИО преподавателя"
        expected_name = "Антохина Юлия Анатольевна"
        if data_docx['t_name'] != expected_name:
            assert False, "ФИО преподавателя"
    except Exception:
        assert False, "ФИО преподавателя"

def test_4():
    """测试学科数据是否正确"""
    try:
        data_docx = main.load_data_from_json('2.txt')
        if 'subject' not in data_docx or not data_docx['subject']:
            assert False, "Данные о предмете"
        if data_docx['subject'] != "Операционные системы":
            assert False, "Данные о предмете"
    except Exception:
        assert False, "Данные о предмете"

def test_5():
    """测试学生组别是否正确"""
    try:
        data_docx = main.load_data_from_json('2.txt')
        if 'class' not in data_docx or not data_docx['class']:
            assert False, "Группа студента"
        if data_docx['class'] != "4931":
            assert False, "Группа студента"
    except Exception:
        assert False, "Группа студента"

def test_6():
    """测试学生姓名是否正确"""
    try:
        data_docx = main.load_data_from_json('2.txt')
        if 'st_name' not in data_docx or not data_docx['st_name']:
            assert False, "ФИО студента"
        expected_name = "Иванов Иван Иванович"
        if data_docx['st_name'] != expected_name:
            assert False, "ФИО студента"
    except Exception:
        assert False, "ФИО студента"

def test_7():
    """测试时间格式是否正确"""
    try:
        data_docx = main.load_data_from_json('2.txt')
        if 'time' not in data_docx or not data_docx['time']:
            assert False, "Формат времени"
        # 检查时间格式是否为 YYYY/MM/DD
        time_parts = data_docx['time'].split('/')
        if len(time_parts) != 3:
            assert False, "Формат времени"
        # 检查是否为有效日期
        try:
            datetime.strptime(data_docx['time'], '%Y/%m/%d')
        except ValueError:
            assert False, "Формат времени"
    except Exception:
        assert False, "Формат времени"

def test_8():
    """测试JSON文件不存在的错误处理"""
    try:
        main.load_data_from_json('nonexistent.json')
        assert False, "Обработка ошибок файла"
    except FileNotFoundError:
        # 这是期望的行为
        pass
    except Exception:
        assert False, "Обработка ошибок файла"


def test_9():
    """测试缺少必要字段的处理"""
    # 创建临时的不完整JSON文件
    incomplete_data = {"student": {"name": "Test"}}  # 缺少必要字段
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(incomplete_data, f, ensure_ascii=False)
        temp_file = f.name
    
    try:
        main.load_data_from_json(temp_file)
        assert False, "Обработка отсутствующих полей"
    except KeyError:
        # 这是期望的行为
        pass
    except Exception:
        assert False, "Обработка отсутствующих полей"
    finally:
        os.unlink(temp_file)

def test_10():
    """测试文档生成功能"""
    if not os.path.exists('./шаблон.docx'):
        pytest.skip("模板文件不存在，跳过文档生成测试")
    
    try:
        # 测试文档生成
        result = main.generate_document('./шаблон.docx', 'test_result.docx', '2.txt')
        if not result:
            assert False, "Генерация документа"
        
        # 检查输出文件是否存在
        if not os.path.exists('test_result.docx'):
            assert False, "Генерация документа"
            
        # 清理测试文件
        if os.path.exists('test_result.docx'):
            os.remove('test_result.docx')
            
    except Exception:
        assert False, "Генерация документа"

def test_11():
    """测试模板文件不存在的处理"""
    try:
        result = main.generate_document('nonexistent_template.docx', 'test_output.docx', '2.txt')
        if result:  # 应该返回False
            assert False, "Обработка отсутствующего шаблона"
    except Exception:
        assert False, "Обработка отсутствующего шаблона"

if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])
