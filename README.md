# Resume Backend

这是一个基于 `FastAPI + PostgreSQL + Vue` 的在线简历系统 MVP。

当前已经具备：

- 简历的创建、查询、更新、删除
- Vue 前端表单编辑页面
- 基于 HTML 模板和浏览器打印能力生成 PDF
- PostgreSQL 持久化存储

## 本地启动

Windows 下可以直接双击/执行根目录脚本，一键构建 Vue 前端并启动 FastAPI：

```powershell
.\start.bat
```

如果你想手动分步启动，也可以执行：

```powershell
cd frontend
npm install
npm run build
cd ..\backend
..\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

启动前需要先构建 `frontend/dist`，`start.bat` 会自动执行 Vue 构建。

访问：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## 已接入的模板

模板文件已经复制到：

- `backend/app/html_templates/pro_resume/`

其中包括：

- HTML 模板 `resume.html.j2`
- 前端默认头像 `frontend/src/assets/default-avatar.jpg`
- 浏览器无头打印 PDF 流程

## 主要接口

- `GET /api/templates`
- `GET /api/resumes`
- `POST /api/resumes`
- `PUT /api/resumes/{resume_id}`
- `DELETE /api/resumes/{resume_id}`
- `POST /api/resumes/{resume_id}/render`
- `GET /api/resumes/{resume_id}/pdf`
