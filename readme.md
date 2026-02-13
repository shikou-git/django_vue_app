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

## 其他

```bash
# 导出顶层包
pipdeptree --freeze --warn silence | findstr /r "^[a-zA-Z]" > requirements.txt

# 迁移
python manage.py makemigrations
python manage.py migrate
```

# 前端

## 多环境配置（Vite 环境文件）

- **.env**：公共配置，所有命令都会加载
- **.env.dev / .env.test / .env.prod**：按 `--mode` 加载，覆盖同名变量
- **.env.dist**：变量说明模板，可提交；实际使用的 .env* 勿提交

仅 **VITE_** 前缀变量会注入到前端（如 `import.meta.env.VITE_API_BASE_URL`）。

| 命令 | 加载文件 | 说明 |
|------|----------|------|
| `npm run dev` | .env + .env.dev | 本地开发 |
| `npm run build` / `npm run build:prod` | .env + .env.prod | 生产构建 |
| `npm run build:test` | .env + .env.test | 测试环境构建 |
| `npm run build:dev` | .env + .env.dev | 开发配置构建 |

首次使用：复制 `web/.env.dist` 为 `web/.env`，或复制对应 `.env.dev` / `.env.prod` 为 `.env` 后按需修改。

```bash
cd web
npm install
npm run dev
```
