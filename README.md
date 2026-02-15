# 校园文创销售管理系统 · V2

全新的 Django + Vue 3 版本围绕“商品管理 / 在线销售 / 定制服务 / 数据分析 / 互动社区”五大板块重构，实现浅绿色 Apple 风交互体验、会话 + 令牌双保险以及远程 MySQL 存储。

```
├── Django/                    # 后端服务
│   ├── campus_store/
│   │   ├── accounts/          # 自定义用户、会话令牌、权限
│   │   ├── catalog/           # 分类、商品、库存同步
│   │   ├── commerce/          # 订单、支付意图、发货信息
│   │   ├── customization/     # 定制心愿 & 时间线
│   │   ├── analytics/         # 指标快照、概览接口
│   │   ├── community/         # 社区帖子 / 评论 / 点赞
│   │   ├── exceptions.py      # 统一 302 登录重定向
│   │   └── settings.py        # MySQL / REST / CORS 配置
│   └── manage.py
└── Front/
    ├── src/
    │   ├── api/               # axios 封装
    │   ├── layouts/           # AppShell 布局
    │   ├── store/             # Pinia 会话状态
    │   ├── router/            # 路由守卫 + 角色限制
    │   ├── components/        # Apple 风控件
    │   └── views/             # 登录/注册/仪表盘等页面
    └── package.json
```

## 后端

### 环境准备
```bash
cd Django
python -m venv venv
venv\Scripts\activate  # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### 数据库
- **默认连接**：远程 MySQL `47.108.151.60` / `yhl_0118` / `qiQi1314**00` / `yhl_0118`。
- **本地调试**：若暂时无法访问服务器，可在命令前添加 `DJANGO_USE_SQLITE=1` 使用 SQLite。
- 如需修改凭据，请设置环境变量 `MYSQL_HOST/USER/PASSWORD/DATABASE` 或在部署平台注入。

### 迁移 & 管理
```bash
# 生产使用远程 MySQL
python manage.py migrate

# 本地调试使用 SQLite
DJANGO_USE_SQLITE=1 python manage.py migrate

python manage.py createsuperuser  # 创建管理员
python manage.py runserver
```

### 核心能力
- 自定义 `accounts.User` + `SessionToken`，DRF 中间件遇到未登录/令牌过期时返回 `302 /login`。`SessionTokenAuthentication` 同时读取 Cookie 与 `X-SESSION-TOKEN` 头。
- `RolePermission` 统一控制管理员/商家/消费者访问入口；管理员拥有 `/api/admin/terminal/` 模拟终端 API（限制 15s，自动记录命令日志）。
- `catalog` 负责商品/库存；`commerce` 支持嵌套订单、支付意图、发货状态；`customization` 记录许愿、时间线互动与商家认领；`analytics` 汇总关键指标；`community` 提供帖子、评论、表态。
- REST Router 统一注册于 `/api/...`，详见 `campus_store/urls.py`。

## 前端

### 安装 & 命令
```bash
cd Front
npm install
npm run dev      # http://localhost:5173
npm run build    # 产出 dist/
```

将 `.env.development` 中的 `VITE_API_BASE` 指向后端（默认 `http://127.0.0.1:8000/api/`）。若后端部署在公网，直接填写公网地址即可。

### 体验亮点
- Pinia + Vue Router 构建认证流，未登录或令牌失效跳回 `/login`。
- AppShell 采用浅绿色玻璃拟态风格，Sidebar 根据角色动态展示模块。
- 页面覆盖：登录 / 注册 / 仪表盘 / 商品管理 / 在线销售 / 定制服务 / 数据分析 / 互动社区 / 管理员模拟终端。
- Axios 拦截器自动附带 `X-SESSION-TOKEN`，捕获 302 时自动跳转登录。

## 一键启动

1. **后端**  
   ```bash
   cd Django
   # 远程 MySQL
   python manage.py runserver 0.0.0.0:8000
   ```
2. **前端**  
   ```bash
   cd Front
   npm run dev
   ```

访问 `http://localhost:5173`，完成登录/注册后即可体验。管理员可通过 `python manage.py createsuperuser` 创建最高权限账号进入“模拟终端”。

## 测试
- 后端：`DJANGO_USE_SQLITE=1 python manage.py test`
- 前端：`npm run build`（Vite 默认进行类型/语法校验）

## 下一步建议
1. 使用 Celery + Redis 处理指标快照、库存告警、导出任务。
2. 引入短信/邮箱验证码，为管理员终端增加 MFA。
3. 将静态资源部署至 CDN，后端使用 Gunicorn + Daphne 托管 HTTP + WebSocket。
