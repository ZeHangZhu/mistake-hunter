## 项目初始化步骤

### 1. 进入项目目录
```powershell
cd A:\错题猎手\src
```

### 2. 激活虚拟环境（如果可以）
如果项目有 `.venv` 目录，运行：
```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. 安装依赖
检查是否有 `requirements.txt`，如果有运行：
```powershell
pip install -r requirements.txt
```

### 4. 运行数据库迁移
```powershell
python manage.py migrate
```

### 5. 创建超级用户（可选，用于管理后台）
```powershell
python manage.py createsuperuser
```
按照提示输入用户名、邮箱和密码。

### 6. 启动开发服务器
```powershell
python manage.py runserver
```

### 7. 在浏览器中访问
打开浏览器访问：`http://127.0.0.1:8000/`  


## 快速开始使用

1. **注册账号**：访问登录页面，点击"注册"创建账号
2. **创建学科**：登录后点击"学科管理"，添加第一个学科（如：数学）
3. **添加错题**：点击"错题本" → "添加错题"开始使用
