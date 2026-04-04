# 前端 Vue 重构建议

这个项目当前前端是 `login.html + login.js + editor.html + editor.js + styles.css` 的原生静态实现，后端由 FastAPI 直接返回 HTML 并挂载 `/assets` 静态资源。

## 现状判断

- 旧版原生前端已下线，当前主前端在 `frontend/`，后续维护和新功能都建议直接在 Vue 工程内演进。
- 登录/注册页和编辑页都依赖同一份大 CSS，样式复用度高，但组件边界不清晰。
- 后端 API 已经比较稳定，适合先保持接口不变，只重构前端渲染层。

## 推荐迁移路线

### 第一阶段：Vue 接管页面壳和状态

- 引入 `Vue 3 + Vite + Vue Router + Pinia`
- 新建 `src/pages/LoginPage.vue`、`src/pages/EditorPage.vue`
- 把登录态、简历列表、模板列表、当前编辑简历抽到 `stores/auth.ts` 和 `stores/resume.ts`
- 把 API 请求封装到 `src/api/*.ts`

### 第二阶段：拆编辑页组件

- `ResumeSidebar.vue`：用户信息、简历列表、新建简历、退出登录、侧边栏收起/展开
- `ResumeMetaForm.vue`：标题、模板选择、版式设置
- `ResumeSectionNav.vue`：左侧模块导航、拖拽排序、新增自定义模块
- `ResumeBasicsSection.vue`：基础信息 + 头像上传裁剪参数
- `ResumeRepeatSection.vue`：教育/经历/项目/作品集/科研/奖项通用列表编辑
- `ResumeCustomSection.vue`：自定义模块
- `ResumePreviewPane.vue`：PDF/HTML 预览
- `ConfirmDialog.vue`、`ToastMessage.vue`、`MonthPicker.vue`、`RichTextEditor.vue` 作为通用组件

### 第三阶段：样式响应式体系化

- 用 4 档断点统一管理：
- `>= 1440px` 桌面大屏：编辑区 + 预览区双栏
- `1024px ~ 1439px` 小桌面/横屏平板：双栏但缩小预览区最小宽度
- `768px ~ 1023px` 平板：编辑区单栏，预览区下移，侧边栏默认抽屉收起
- `< 768px` 手机：模块导航横向滚动，表单单列，操作按钮满宽，PDF 预览高度按 `svh` 计算

## 和 FastAPI 的集成方式

- 开发环境：Vite dev server 代理 `/api` 到 FastAPI
- 生产环境：`npm run build` 后把 `dist/` 挂到 FastAPI 静态目录，`/login`、`/register`、`/editor` 统一返回 `index.html`

## 建议先不要一次性全量重写的原因

- `editor.js` 里有大量现成业务细节，包括富文本净化、月份选择器、模块排序、头像裁剪、PDF 缓存签名，这些逻辑一次性改写很容易引入回归。
- 更稳妥的做法是先按组件边界迁移一个页面，再逐块搬运功能，同时保留接口契约和原有数据结构。

如果你希望我下一步直接开始落 Vue 版本，我建议先从“登录/注册页 + 编辑页外壳 + Pinia 状态层”这一层开工，先把工程骨架搭起来，再把编辑模块逐个迁进去。
