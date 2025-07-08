
# PhotoX 项目启动说明

## 自动启动脚本

本项目提供了多个自动启动脚本，方便快速启动开发环境。

### 1. 一键启动所有服务 (推荐)

#### Windows批处理版本
```bash
# 双击运行（英文版本，避免编码问题）
start_all.bat

# 或者使用中文版本（需要UTF-8编码支持）
start_all_中文.bat
```

#### PowerShell版本
```powershell
# 右键选择"使用PowerShell运行"
start_all_powershell.ps1
```

### 2. 分别启动服务

#### 启动前端服务
```bash
# 双击运行
start_frontend.bat
```

#### 启动后端服务
```bash
# 双击运行
start_backend.bat
```

## 手动启动步骤

如果自动脚本无法正常工作，可以按照以下步骤手动启动：

### 前端启动
```bash
# 1. 进入前端目录
cd photox_frontend

# 2. 设置PowerShell执行策略
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. 安装依赖（首次运行）
npm install

# 4. 启动开发服务器
npm run dev
```

### 后端启动
```bash
# 1. 进入后端目录
cd photox_backend

# 2. 设置PowerShell执行策略
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. 激活虚拟环境
venv\Scripts\Activate.ps1

# 4. 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 5. 启动Django服务器
python manage.py runserver
```

## 访问地址

- **前端地址**: http://localhost:5173
- **后端地址**: http://localhost:8000
- **Django管理后台**: http://localhost:8000/admin

## 注意事项

1. **首次运行**：确保已安装Node.js和Python环境
2. **虚拟环境**：后端需要激活Python虚拟环境
3. **数据库**：首次运行会自动执行数据库迁移
4. **端口占用**：如果端口被占用，请关闭占用端口的程序
5. **防火墙**：确保防火墙允许本地端口访问
6. **编码问题**：如果出现中文乱码，请使用英文版本的脚本（start_all.bat）

## 故障排除

### 前端问题
- 如果npm install失败，请检查网络连接
- 如果端口5173被占用，可以修改vite.config.ts中的端口配置

### 后端问题
- 如果虚拟环境激活失败，请检查venv目录是否存在
- 如果数据库迁移失败，请检查数据库配置
- 如果端口8000被占用，可以修改Django设置中的端口配置

### 编码问题
- 如果批处理文件显示中文乱码，请使用英文版本的脚本
- 或者确保Windows系统支持UTF-8编码
- 可以在PowerShell中运行：`chcp 65001` 设置UTF-8编码

## 开发环境要求

- Node.js 16+
- Python 3.8+
- npm 或 yarn
- Git

## 项目结构

```
photox_ltb-master2/
├── photox_frontend/     # 前端项目
├── photox_backend/      # 后端项目
├── start_all.bat        # 一键启动脚本
├── start_frontend.bat   # 前端启动脚本
├── start_backend.bat    # 后端启动脚本
└── README_启动说明.md   # 本说明文档
``` 