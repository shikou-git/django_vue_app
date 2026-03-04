# 项目介绍

后台通用管理系统

技术栈：Django5.x + Vue3.x + And Design Vue4.x 前后端分离

# 后端

## 多环境配置（django-environ）

配置加载顺序
先读 .env（通用）
若设置了 DJANGO_ENV=dev|test|prod 且存在 .env.dev / .env.test / .env.prod，再读该文件（覆盖前面的同名变量）

```bash
# 默认（只读取.env）
python manage.py runserver

# 开发（.env + .env.dev）
set DJANGO_ENV=dev
python manage.py runserver

# 测试（.env + .env.test）
set DJANGO_ENV=test
python manage.py runserver

# 生产（.env + .env.prod，使用 gunicorn 生产级服务器）
set DJANGO_ENV=prod
gunicorn mysite.wsgi:application
```

PowerShell 中设为：`$env:DJANGO_ENV="dev"`；Linux/macOS：`export DJANGO_ENV=dev`。

## 数据库（MySQL 5.7）

默认使用 MySQL 5.7。在 `api/.env` 或 `api/.env.dev` 中配置：

- **方式一**：`DATABASE_URL=mysql://用户:密码@主机:3306/数据库名`
- **方式二**：不设 `DATABASE_URL` 时使用 `MYSQL_NAME`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_HOST`、`MYSQL_PORT`

首次使用需在 MySQL 中创建数据库（如 `CREATE DATABASE django_vue_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`），再执行迁移。

## 其他

```bash
# 安装依赖（含 mysqlclient）
pip install -r api/requirements.txt

# 导出顶层包
pipdeptree --freeze --warn silence | findstr /r "^[a-zA-Z]" > requirements.txt

# 迁移
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

# 前端

## 多环境配置（Vite 环境文件）

- **.env**：公共配置，所有命令都会加载
- **.env.dev / .env.test / .env.prod**：按 `--mode` 加载，覆盖同名变量
- **.env.dist**：变量说明模板，可提交；实际使用的 .env\* 勿提交

仅 **VITE\_** 前缀变量会注入到前端（如 `import.meta.env.VITE_API_BASE_URL`）。

| 命令                                   | 加载文件         | 说明         |
| -------------------------------------- | ---------------- | ------------ |
| `npm run dev`                          | .env + .env.dev  | 本地开发     |
| `npm run build` / `npm run build:prod` | .env + .env.prod | 生产构建     |
| `npm run build:test`                   | .env + .env.test | 测试环境构建 |
| `npm run build:dev`                    | .env + .env.dev  | 开发配置构建 |

首次使用：复制 `web/.env.dist` 为 `web/.env`，或复制对应 `.env.dev` / `.env.prod` 为 `.env` 后按需修改。

```bash
cd web
npm install
npm run dev
```
