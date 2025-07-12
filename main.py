import json
import sys
import os
from datetime import datetime
from docxtpl import DocxTemplate


def load_data_from_json(json_file_path='2.txt'):

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 构建教师全名
        teacher = data['report']['teacher']
        teacher_full_name = f"{teacher['surname']} {teacher['name']} {teacher['patronymic']}"

        # 构建学生全名
        student = data['student']
        student_full_name = f"{student['surname']} {student['name']} {student['patronymic']}"

        # 获取当前日期
        current_date = datetime.now().strftime('%Y/%m/%d')

        # 映射数据到data_docx格式
        data_docx = {
            'position': data['report']['teacher']['status'],
            'time': current_date,  # 当前时间
            't_name': teacher_full_name,  # 教师全名
            'title': data['report']['task_name'],  # 任务标题
            'subject': data['report']['subject_name'],  # 学科名称
            'class': data['student']['group'],  # 班级/组
            'st_name': student_full_name,  # 学生全名
        }

        return data_docx

    except FileNotFoundError:
        raise FileNotFoundError(f"找不到JSON文件: {json_file_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"JSON格式错误: {e}")
    except KeyError as e:
        raise KeyError(f"JSON中缺少必要字段: {e}")


def generate_document(template_path='./模板.docx', output_path='result.docx', json_file_path='2.txt'):

    try:
        # 检查模板文件是否存在
        if not os.path.exists(template_path):
            print(f"错误: 找不到模板文件 {template_path}")
            return False

        # 读取模板文档
        doc = DocxTemplate(template_path)

        # 从JSON文件加载数据
        data_docx = load_data_from_json(json_file_path)

        # 使用数据填充模板
        doc.render(data_docx)

        # 保存生成的文档
        doc.save(output_path)

        print(f"文档生成成功: {output_path}")
        print("使用的数据:")
        for key, value in data_docx.items():
            print(f"  {key}: {value}")

        return True

    except Exception as e:
        print(f"生成文档时发生错误: {e}")
        return False


def main():
    """
    主函数，处理命令行参数
    """
    # 默认参数
    template_path = './模板.docx'
    output_path = 'result.docx'
    json_file_path = '2.txt'

    # 处理命令行参数
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
    if len(sys.argv) > 2:
        template_path = sys.argv[2]
    if len(sys.argv) > 3:
        output_path = sys.argv[3]

    # 显示使用的参数
    print("文档生成器")
    print(f"JSON数据文件: {json_file_path}")
    print(f"模板文件: {template_path}")
    print(f"输出文件: {output_path}")
    print("-" * 50)

    # 生成文档
    success = generate_document(template_path, output_path, json_file_path)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


# 当作为独立应用程序运行时执行main函数
if __name__ == "__main__":
    main()