# 项目介绍

后台通用管理系统

技术栈：Django5.x + Vue3.x + And Design Vue4.x 前后端分离

# 后端

## 多环境配置（django-environ）

- **实际生效的是 `.env`**：Django 从 `api/.env` 读环境变量；**启动时可通过 `DJANGO_ENV` 指定环境**，见下。
- **`.env`、`.env.dev`、`.env.test`、`.env.prod` 不提交**；仓库里只放模板和示例（`.env.dist`、`.env.*.example`）。

### 启动时指定环境

**方式一：用环境变量指定（推荐）**

先按环境准备好对应文件（复制示例并改名）：`.env.dev`、`.env.test`、`.env.prod`（或只保留一份 `.env`）。启动时设置 `DJANGO_ENV`：

```bash
cd api
# 开发
set DJANGO_ENV=dev
python manage.py runserver

# 测试
set DJANGO_ENV=test
python manage.py runserver

# 生产（如 gunicorn）
set DJANGO_ENV=prod
gunicorn mysite.wsgi:application
```

PowerShell 中设为：`$env:DJANGO_ENV="dev"`；Linux/macOS：`export DJANGO_ENV=dev`。

**方式二：不指定**

不设 `DJANGO_ENV` 时只读 `api/.env`。复制对应示例为 `.env` 即可：

```bash
cd api
copy .env.dev.example .env
python manage.py runserver
```

## 其他

```bash
# 导出顶层包
pipdeptree --freeze --warn silence | findstr /r "^[a-zA-Z]" > requirements.txt

# 迁移
python manage.py makemigrations
python manage.py migrate
```

# 前端

```bash

```
