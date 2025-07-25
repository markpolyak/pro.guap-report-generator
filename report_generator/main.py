import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from .schemas import ReportRequest
from .generator import generate_report
from .limiter import apply_rate_limit
import tempfile

# 创建应用实例的函数
def create_app():
    app = FastAPI(
        title="Report Generator API",
        description="API для генерации шаблонов отчетов",
        version="1.0.0"
    )
    
    # 应用速率限制
    apply_rate_limit(app, enabled=os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true")
    
    @app.post("/generate-report/", summary="Генерация отчета")
    async def generate_report_endpoint(request: ReportRequest):
        try:
            # 生成DOCX文档
            doc = generate_report(request)
            
            # 保存临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                doc.save(tmp.name)
                tmp_path = tmp.name
            
            # 返回文件下载
            return FileResponse(
                tmp_path,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                filename="report.docx"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")
    
    return app

# 创建应用实例
app = create_app()  # 这行修复了 Pylance 错误