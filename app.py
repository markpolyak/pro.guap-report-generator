from flask import Flask, request, send_file, jsonify, make_response
from werkzeug.utils import secure_filename
from flask_cors import CORS  # 添加这行导入
import os
import tempfile
import logging
import traceback
import shutil
from main import generate_document

app = Flask(__name__)
CORS(app)  # 启用 CORS 支持

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/generate', methods=['POST'])
def generate_report():
    logger.info("Получен запрос на сборку")
    
    try:
        # 检查是否提供了JSON文件
        if 'json' not in request.files:
            logger.error("Файл JSON отсутствует в запросе")
            return jsonify({"error": "Отсутствует файл JSON"}), 400
        
        json_file = request.files['json']
        template_file = request.files.get('template', None)
        
        logger.info(f"Получить JSON-файл: {json_file.filename}")
        if template_file:
            logger.info(f"Получить файл шаблона: {template_file.filename}")
        
        # 创建临时目录
        tmp_dir = tempfile.mkdtemp()
        logger.info(f"Создать временный каталог: {tmp_dir}")
        
        try:
            # 保存JSON文件
            json_path = os.path.join(tmp_dir, 'data.json')
            json_file.save(json_path)
            logger.info(f"Файлы JSON сохраняются в: {json_path}")
            
            # 处理模板文件
            template_path = None
            if template_file:
                template_path = os.path.join(tmp_dir, 'template.docx')
                template_file.save(template_path)
                logger.info(f"Сохраните файл шаблона в: {template_path}")
            else:
                logger.info("Файл шаблона не предоставлен, используется шаблон по умолчанию.")
                # 使用默认模板路径
                template_path = './шаблон.docx'
            
            # 设置输出路径
            output_path = os.path.join(tmp_dir, 'result.docx')
            logger.info(f"Выходной путь: {output_path}")
            
            # 调用生成函数
            logger.info("Начало документирования...")
            success = generate_document(
                template_path=template_path,
                output_path=output_path,
                json_file_path=json_path
            )
            
            if not success:
                logger.error("Не удалось создать документ")
                return jsonify({"error": "Не удалось создать документ"}), 500
            
            logger.info("Документ создан успешно")
            
            # 读取文件内容到内存
            with open(output_path, 'rb') as f:
                file_data = f.read()
            
            # 创建响应对象
            response = make_response(file_data)
            response.headers.set('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response.headers.set('Content-Disposition', 'attachment', filename='generated_report.docx')
            
            return response
            
        finally:
            # 清理临时目录
            try:
                shutil.rmtree(tmp_dir, ignore_errors=True)
                logger.info(f"Временные каталоги очищены: {tmp_dir}")
            except Exception as e:
                logger.error(f"Не удалось очистить временный каталог: {str(e)}")
    
    except Exception as e:
        logger.error(f"Произошла ошибка во время процесса сборки: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Внутренняя ошибка сервера",
            "details": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)