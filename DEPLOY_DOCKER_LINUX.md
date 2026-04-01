# Alibaba Linux Docker 部署流程

这个项目已经整理成可以直接在 `Alibaba Linux` 上用 `Docker Compose` 部署的结构。

现在仓库里已经有这些文件：

- `Dockerfile`
- `docker-compose.yml`
- `deploy/nginx/default.conf`
- `deploy.sh`
- `.env.docker.example`

最终部署后的访问关系是：

- `80 -> nginx -> app:8000`
- `9000 -> minio api`
- `9001 -> minio console`

也就是说：

- 网站入口：`http://你的服务器IP/`
- 接口文档：`http://你的服务器IP/docs`
- MinIO 控制台：`http://你的服务器IP:9001`

## 一、服务器准备

建议最低配置：

- 2 vCPU
- 4 GB 内存
- 20 GB 磁盘

安全组 / 防火墙开放端口：

- `80`
- `9000`
- `9001`
- 如果后续要上 HTTPS，再放行 `443`

## 二、Alibaba Linux 安装 Docker

下面按 `Alibaba Cloud Linux 3` 写。

```bash
sudo rm -f /etc/yum.repos.d/docker*.repo
sudo wget -O /etc/yum.repos.d/docker-ce.repo http://mirrors.cloud.aliyuncs.com/docker-ce/linux/centos/docker-ce.repo
sudo sed -i 's|https://mirrors.aliyun.com|http://mirrors.cloud.aliyuncs.com|g' /etc/yum.repos.d/docker-ce.repo
sudo dnf -y install dnf-plugin-releasever-adapter --repo alinux3-plus
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin git
sudo systemctl enable docker
sudo systemctl start docker
docker --version
docker compose version
git --version
```

如果 `dnf` 不可用，先确认系统版本：

```bash
cat /etc/os-release
```

## 三、最短可执行流程

如果你要的是“拉代码后改一下配置就跑”，直接按这个顺序：

```bash
cd /opt
git clone <你的仓库地址> resume
cd /opt/resume
cp .env.docker.example .env.docker
vi .env.docker
sh deploy.sh
```

启动完成后检查：

```bash
docker compose --env-file .env.docker ps
curl http://127.0.0.1/api/health
```

## 四、`.env.docker` 要改什么

只要重点改这几组。

### 1. PostgreSQL

```env
POSTGRES_DB=resume_app
POSTGRES_USER=resume_user
POSTGRES_PASSWORD=你的数据库强密码
DATABASE_URL=postgresql+psycopg://resume_user:你的数据库强密码@postgres:5432/resume_app
```

要求：

- `DATABASE_URL` 必须和上面三项保持一致
- 主机名要写 `postgres`，不要写 `127.0.0.1`

### 2. 应用登录密钥

```env
AUTH_SECRET_KEY=一个至少32位的随机字符串
```

建议生成：

```bash
openssl rand -hex 32
```

### 3. MinIO

```env
MINIO_ROOT_USER=resumeadmin
MINIO_ROOT_PASSWORD=你的MinIO强密码
MINIO_ENDPOINT=minio:9000
MINIO_PUBLIC_ENDPOINT=你的服务器公网IP:9000
MINIO_ACCESS_KEY=resumeadmin
MINIO_SECRET_KEY=你的MinIO强密码
MINIO_BUCKET=resume-pdfs
MINIO_SECURE=false
```

这里最关键的是：

- `MINIO_ENDPOINT=minio:9000` 是容器内部访问地址
- `MINIO_PUBLIC_ENDPOINT=公网IP:9000` 是浏览器访问预签名链接的地址
- `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` 目前建议直接和 `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` 保持一致

### 4. 邮件验证码

如果你要启用邮箱验证码，再配置：

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=你的SMTP账号
SMTP_PASSWORD=你的SMTP密码
SMTP_FROM_EMAIL=no-reply@example.com
SMTP_FROM_NAME=OfferPilot
SMTP_USE_SSL=false
SMTP_USE_STARTTLS=true
```

如果暂时不用邮件功能，可以先不改，但注册发送验证码时会失败。

## 五、账号密码怎么规划

建议你直接按这套命名走，最省心：

### PostgreSQL

- 数据库名：`resume_app`
- 用户名：`resume_user`
- 密码：你自己生成一个强密码

### MinIO

- 管理员账号：`resumeadmin`
- 管理员密码：你自己生成一个强密码
- Bucket：`resume-pdfs`

### 应用密钥

- `AUTH_SECRET_KEY`：随机 32 字节以上

## 六、Bucket 需要手动创建吗

这个项目启动时会自动执行：

- 数据库建表
- MinIO Bucket 检查
- 如果 Bucket 不存在就自动创建

所以通常不需要你手工创建。

你只需要保证：

- `minio` 容器正常启动
- `.env.docker` 里 `MINIO_BUCKET=resume-pdfs`

启动后你可以到 MinIO Console 验证：

- `http://你的服务器IP:9001`
- 用户名：`MINIO_ROOT_USER`
- 密码：`MINIO_ROOT_PASSWORD`

## 七、为什么反向代理只代理应用，不代理 MinIO

当前这套方案里：

- `Nginx` 只负责网站入口和接口反代
- `MinIO` 直接开放 `9000/9001`

这是为了让 `MINIO_PUBLIC_ENDPOINT` 更简单稳定。

因为你的代码会给浏览器返回 MinIO 预签名 URL，如果再额外做复杂路径代理，后面更容易出错。

## 八、启动和排错命令

启动：

```bash
sh deploy.sh
```

它等价于：

```bash
docker compose --env-file .env.docker up -d --build
```

查看状态：

```bash
docker compose --env-file .env.docker ps
```

看应用日志：

```bash
docker compose --env-file .env.docker logs -f app
```

看 Nginx 日志：

```bash
docker compose --env-file .env.docker logs -f nginx
```

看数据库日志：

```bash
docker compose --env-file .env.docker logs -f postgres
```

看 MinIO 日志：

```bash
docker compose --env-file .env.docker logs -f minio
```

## 九、更新部署

以后更新代码就执行：

```bash
cd /opt/resume
git pull
docker compose --env-file .env.docker down
docker compose --env-file .env.docker up -d --build
```

如果只重建应用和 Nginx：

```bash
docker compose --env-file .env.docker up -d --build app nginx
```

## 十、上线后验证

健康检查：

```bash
curl http://127.0.0.1/api/health
```

页面检查：

- `http://你的服务器IP/`
- `http://你的服务器IP/login`
- `http://你的服务器IP/docs`

MinIO 检查：

- `http://你的服务器IP:9001`

## 十一、常见坑

### 1. 页面能打开，但 PDF 生成失败

这个功能依赖 Chromium。当前 `Dockerfile` 里已经装了 `chromium`，正常不需要你再处理。

### 2. PDF 下载链接打不开

通常是 `MINIO_PUBLIC_ENDPOINT` 配错了。

错误例子：

```env
MINIO_PUBLIC_ENDPOINT=minio:9000
```

这只是容器内部地址，浏览器打不开。

正确例子：

```env
MINIO_PUBLIC_ENDPOINT=47.xx.xx.xx:9000
```

### 3. 数据库连不上

检查：

- `DATABASE_URL` 用户名密码是否和 `POSTGRES_USER` / `POSTGRES_PASSWORD` 一致
- 主机名是否写成了 `postgres`
- 启动命令是否用了 `--env-file .env.docker`

### 4. 邮件发不出去

检查：

- SMTP 服务是否真的开通
- 端口是 `465` 还是 `587`
- `SMTP_USE_SSL` / `SMTP_USE_STARTTLS` 是否符合邮件服务商要求

## 十二、一套可以直接改的示例

```env
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false

POSTGRES_DB=resume_app
POSTGRES_USER=resume_user
POSTGRES_PASSWORD=ResumeDb_2026_StrongPass
DATABASE_URL=postgresql+psycopg://resume_user:ResumeDb_2026_StrongPass@postgres:5432/resume_app

AUTH_SECRET_KEY=4e46fd7f1d0f3fbdce4ec7b0b9049df7a40656fdf9bb41cc6a96bdb77308f00a

MINIO_ROOT_USER=resumeadmin
MINIO_ROOT_PASSWORD=ResumeMinio_2026_StrongPass
MINIO_ENDPOINT=minio:9000
MINIO_PUBLIC_ENDPOINT=203.0.113.10:9000
MINIO_ACCESS_KEY=resumeadmin
MINIO_SECRET_KEY=ResumeMinio_2026_StrongPass
MINIO_BUCKET=resume-pdfs
MINIO_SECURE=false
```

## 参考资料

- Alibaba Cloud ECS 安装和使用 Docker：
  https://www.alibabacloud.com/help/en/ecs/use-cases/install-and-use-docker
- Alibaba Cloud ECS 安装和使用 Docker：
  https://www.alibabacloud.com/help/en/ecs/user-guide/install-and-use-docker
