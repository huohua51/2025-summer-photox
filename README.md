<<<<<<< HEAD
# PhotoX - 智能图片管理平台

PhotoX 是一个基于 AI 技术的智能图片管理平台，提供图片上传、智能分类、AI 分析、社区分享等功能。

## 项目概述

PhotoX 结合了现代 Web 技术和人工智能，为用户提供全面的图片管理解决方案。项目采用前后端分离架构，支持图片的智能分类、标签生成、风格分析等 AI 功能。

## 技术栈

### 后端 (Django)
- **框架**: Django 4.1.7 + Django REST Framework
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT Token 认证
- **存储**: 七牛云对象存储
- **AI功能**: 
  - 图像分类与标签生成
  - 颜色提取与分析
  - 智能推荐算法
- **API文档**: drf-yasg (Swagger)

### 前端 (Vue.js)
- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **UI组件**: 自定义组件库
- **样式**: CSS3 + 响应式设计

## 主要功能

### 用户系统
- 用户注册、登录、个人资料管理
- 多角色权限控制
- 用户关注与社交功能

### 图片管理
- 图片上传（支持批量上传）
- 智能分类与标签生成
- 图片编辑与AI处理
- 相册创建与管理
- 公开/私密设置

### AI智能功能
- **自动分类**: 基于深度学习的图片内容识别
- **标签生成**: AI自动生成描述性标签
- **颜色分析**: 提取图片主色调
- **风格分析**: 分析图片艺术风格和情感色彩
- **智能推荐**: 基于用户行为的个性化推荐

### 社区功能
- 图片点赞、评论、收藏
- 用户动态与关注系统
- 内容分享与发现

### 管理后台
- 用户管理与内容审核
- 数据统计与分析
- 系统配置与维护

## 项目结构

```
photox_ltb-master/
├── photox_backend/          # Django 后端
│   ├── image_repo_backend/  # 项目配置
│   ├── users/              # 用户模块
│   ├── images/             # 图片模块
│   ├── albums/             # 相册模块
│   ├── community/          # 社区功能
│   ├── tags/               # 标签管理
│   └── templates/          # 模板文件
├── photox_frontend/         # Vue.js 前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── api/            # API接口
│   │   ├── router/         # 路由配置
│   │   └── stores/         # 状态管理
│   └── public/             # 静态资源
└── Photox_Docs/            # 项目文档
```

## 快速开始

### 后端启动

1. 创建虚拟环境并安装依赖：
```bash
cd photox_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. 数据库迁移：
```bash
python manage.py migrate
```

3. 创建超级用户：
```bash
python manage.py createsuperuser
```

4. 启动开发服务器：
```bash
python manage.py runserver
```

### 前端启动

1. 安装依赖：
```bash
cd photox_frontend
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

## API文档

后端启动后访问：
- Swagger UI: http://127.0.0.1:8000/swagger/
- ReDoc: http://127.0.0.1:8000/redoc/
- 管理后台: http://127.0.0.1:8000/admin/

## 贡献者

- huohua51 - 项目架构与后端开发
- 18335986800@163.com - 前端开发与UI设计
- 1101219195@qq.com - AI功能与算法优化

## 开发规范

### Git提交规范
- feat: 新功能
- fix: 修复问题
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建工具或辅助工具的变动

### 代码规范
- 后端遵循 Django 最佳实践
- 前端遵循 Vue.js 官方风格指南
- 使用 ESLint 和 Prettier 进行代码格式化

## 部署

### Docker 部署
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 传统部署
详见 `deploy.sh` 脚本配置

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 更新日志

### v1.0.0 (2025-01-XX)
- 完成基础功能开发
- 实现AI智能分类与推荐
- 上线用户管理与社区功能

---

**PhotoX** - 让图片管理更智能、更简单！ 
=======
# 2025-summer-photox
2025暑期实训
>>>>>>> a6605e7d222b223c9b579215a5e09d115640ce86
