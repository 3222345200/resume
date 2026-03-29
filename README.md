# Resume Backend

这是一个基于 `FastAPI + PostgreSQL + HTML` 的在线简历系统 MVP。

当前已经具备：

- 简历的创建、查询、更新、删除
- 前端表单编辑页面
- 基于 HTML 模板和浏览器打印能力生成 PDF
- PostgreSQL 持久化存储

## 本地启动

```powershell
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

访问：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## 已接入的模板

模板文件已经复制到：

- `app/html_templates/pro_resume/`

其中包括：

- HTML 模板 `resume.html.j2`
- 前端默认头像 `frontend/default-avatar.jpg`
- 浏览器无头打印 PDF 流程

## 主要接口

- `GET /api/templates`
- `GET /api/resumes`
- `POST /api/resumes`
- `PUT /api/resumes/{resume_id}`
- `DELETE /api/resumes/{resume_id}`
- `POST /api/resumes/{resume_id}/render`
- `GET /api/resumes/{resume_id}/pdf`
