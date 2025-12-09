# 智能渔业监控系统 (Fishery Intelligence Hub)

智能渔业监控系统是一个基于Web的水产养殖监控平台，旨在帮助养殖户实时监测水质参数、管理投喂计划、接收预警通知并做出科学决策。

## 功能特性

### 🌊 实时水质监控
- 温度、溶解氧、pH值、氨氮等多项水质参数实时监测
- 数据可视化仪表板展示关键指标
- 24小时水质趋势图表分析

### ⚠️ 智能预警系统
- 异常水质参数自动检测与预警
- 多级别预警通知（信息、警告、危险）
- 历史预警记录与处理状态跟踪

### 📊 数据分析与报告
- 历史数据分析与趋势预测
- 周报生成与导出功能
- 投喂决策辅助建议

### 🎯 投喂管理
- 投喂记录跟踪与管理
- 基于水质和鱼类生长的智能投喂建议
- 投喂计划制定与执行跟踪

### 📱 响应式设计
- 支持PC、平板、手机等多种设备访问
- 移动端优化的触控交互体验
- 自适应布局适配不同屏幕尺寸

## 技术架构

### 前端技术
- HTML5 + CSS3 + JavaScript
- Bootstrap 5 响应式框架
- Chart.js 数据可视化库
- jQuery 简化DOM操作

### 后端技术
- Python Flask Web框架
- SQLite 数据库
- SQLAlchemy ORM
- Flask-Babel 国际化支持

### 部署环境
- Nginx 反向代理服务器
- Systemd 服务管理
- Alibaba Cloud Linux 3

## 快速开始

### 本地开发环境搭建

1. 克隆项目代码
```bash
git clone https://github.com/fyfhcgch/Fishery-Intel.git
cd Fishery-Intel
```

2. 安装依赖
```bash
pip install flask flask-sqlalchemy flask-babel
```

3. 运行应用
```bash
python app.py
```

4. 访问应用
在浏览器中打开 http://localhost:5000

### 生产环境部署

1. 服务器环境准备
```bash
# 更新系统包
yum update -y

# 安装Python 3和pip
yum install -y python3 python3-pip

# 安装C++编译器和开发工具
yum install -y gcc gcc-c++ python3-devel

# 安装兼容版本的Flask-Babel
pip3 install Flask-Babel==2.0.0
```

2. 配置Nginx反向代理
```bash
# 安装Nginx
yum install -y nginx

# 创建Nginx配置文件
cat > /etc/nginx/conf.d/fish_smart_hub.conf << 'EOF'
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件直接由Nginx处理
    location /static {
        alias /var/www/fish_smart_hub/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
```

3. 配置Systemd服务
```bash
cat > /etc/systemd/system/fish-smart-hub.service << 'EOF'
[Unit]
Description=Fish Smart Hub Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/fish_smart_hub
Environment=PATH=/usr/local/bin
ExecStart=/usr/bin/python3 /var/www/fish_smart_hub/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

4. 启动服务
```bash
systemctl daemon-reload
systemctl enable fish-smart-hub
systemctl start fish-smart-hub
systemctl enable nginx
systemctl start nginx
```

## 项目结构

```
Fishery-Intel/
├── app.py                 # 应用入口文件
├── models.py              # 数据库模型定义
├── routes.py              # 主要路由定义
├── route_modules/         # 模块化路由
│   ├── data_routes.py     # 数据相关API
│   ├── alert_routes.py    # 预警相关API
│   └── decision_routes.py # 决策相关API
├── static/                # 静态资源文件
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   └── vendor/            # 第三方库
├── templates/             # HTML模板文件
└── translations/          # 国际化翻译文件
```

## 数据库设计

### 主要实体
- **User**: 用户信息
- **Pond**: 塘口信息
- **WaterQuality**: 水质数据
- **FeedingRecord**: 投喂记录
- **Alert**: 预警信息
- **FeedingDecision**: 投喂决策

## 国际化支持

系统支持中英文切换，默认语言为中文。用户可以在界面中切换语言，系统会记住用户的语言偏好。

## 开发指南

### 添加新的水质参数
1. 在`models.py`中的`WaterQuality`模型添加新字段
2. 在`templates/`中的相应页面添加数据显示
3. 在`route_modules/data_routes.py`中更新API接口

### 添加新的预警类型
1. 在`models.py`中的`Alert`模型确认字段支持
2. 在业务逻辑中添加预警触发条件
3. 在前端页面中添加预警显示

## 贡献指南

欢迎提交Issue和Pull Request来改进系统功能。

## 许可证

本项目采用MIT许可证，详情请见[LICENSE](LICENSE)文件。

## 联系方式

如有任何问题，请联系项目维护者。