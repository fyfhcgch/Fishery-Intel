from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from datetime import datetime, timedelta
import random
import json
from functools import wraps
import gzip
from io import BytesIO
from flask_babel import Babel, gettext as _, lazy_gettext

app = Flask(__name__)

# Release模式配置
app.config['SECRET_KEY'] = 'fish_smart_hub_2023'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fish_farm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = False
app.config['TESTING'] = False

# 本地化配置
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
app.config['BABEL_SUPPORTED_LOCALES'] = ['zh', 'en']
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

# 添加缓存和压缩配置
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 静态文件缓存1年
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'text/plain', 
    'application/javascript', 'application/json', 'application/xml'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_THRESHOLD'] = 100  # 大于100字节才压缩

# 语言选择函数
def get_locale():
    # 从session获取语言设置，如果没有则使用浏览器语言
    if 'language' in session:
        return session['language']
    
    # 从浏览器语言首选项获取
    browser_lang = request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])
    if browser_lang:
        return browser_lang
    
    # 默认使用中文
    return app.config['BABEL_DEFAULT_LOCALE']

# 初始化Babel (适配新版本)
babel = Babel(app)

# 注册localeselector (适配新版本Flask-Babel)
@babel.localeselector
def get_locale_wrapper():
    return get_locale()

# 将get_locale函数注册到模板上下文中
@app.context_processor
def inject_get_locale():
    return {'get_locale': get_locale}

# 添加语言切换路由
@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

# Release模式：简化缓存控制，移除复杂的压缩逻辑

# Release模式：简化静态文件缓存控制
@app.after_request
def add_cache_headers(response):
    # 静态资源缓存控制（1年）
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response

# 导入模型和db实例
from models import db, User, Pond, WaterQuality, FeedingRecord, Alert, FeedingDecision

# 初始化数据库
db.init_app(app)

# 导入路由
from routes import main_bp
from route_modules.data_routes import data_bp
from route_modules.decision_routes import decision_bp
from route_modules.alert_routes import alert_bp

app.register_blueprint(main_bp)
app.register_blueprint(data_bp, url_prefix='/data')
app.register_blueprint(decision_bp, url_prefix='/decision')
app.register_blueprint(alert_bp, url_prefix='/alert')

def create_demo_data():
    # 检查是否已有数据
    if User.query.first():
        return
    
    # 创建演示用户
    demo_user = User(username="张渔农", phone="13800138000")
    db.session.add(demo_user)
    db.session.commit()
    
    # 创建演示塘口
    ponds = [
        Pond(name="1号塘", area=5.2, species="南美白对虾", user_id=demo_user.id),
        Pond(name="2号塘", area=3.8, species="草鱼", user_id=demo_user.id),
        Pond(name="3号塘", area=4.5, species="南美白对虾", user_id=demo_user.id)
    ]
    
    for pond in ponds:
        db.session.add(pond)
    
    db.session.commit()
    
    # 创建演示水质数据
    now = datetime.now()
    for pond in ponds:
        # 为每个塘口创建一个月的详细数据
        for i in range(24 * 30):  # 一个月的数据
            time_point = now - timedelta(hours=i)
            
            # 根据塘口类型和一天中的时间模拟更真实的水质数据
            if pond.species == "南美白对虾":
                base_temp = 28 + random.uniform(-2, 2)  # 对虾喜欢较高温度
                base_do = 6.5 + random.uniform(-1.0, 1.0)
                base_ph = 8.0 + random.uniform(-0.3, 0.3)  # 对虾喜欢稍高pH
                base_ammonia = 0.15 + random.uniform(-0.05, 0.1)
            else:  # 草鱼
                base_temp = 24 + random.uniform(-2, 2)
                base_do = 7.0 + random.uniform(-1.0, 1.5)
                base_ph = 7.5 + random.uniform(-0.5, 0.5)
                base_ammonia = 0.2 + random.uniform(-0.1, 0.2)
            
            # 模拟夜间溶解氧下降
            if time_point.hour >= 0 and time_point.hour <= 6:
                base_do -= random.uniform(0.8, 1.8)
            
            # 模拟午后温度升高
            if time_point.hour >= 12 and time_point.hour <= 15:
                base_temp += random.uniform(1, 3)
            
            # 模拟投喂后氨氮升高（每天8点和17点投喂）
            if time_point.hour in [9, 10] or time_point.hour in [18, 19]:
                base_ammonia += random.uniform(0.1, 0.3)
            
            # 偶尔模拟水质异常情况
            if random.random() < 0.02:  # 2%概率出现异常
                if random.random() < 0.5:
                    base_do -= random.uniform(1.5, 2.5)  # 溶解氧异常低
                else:
                    base_ph += random.uniform(0.8, 1.2)  # pH异常高
            
            water_quality = WaterQuality(
                pond_id=pond.id,
                temperature=round(base_temp, 1),
                turbidity=round(random.uniform(5, 25), 1),  # 浊度(NTU)
                conductivity=round(random.uniform(300, 800), 0),  # 电导率(μS/cm)
                water_level=round(random.uniform(1.5, 2.5), 2),  # 液位(m)
                dissolved_oxygen=round(max(3.0, base_do), 1),  # 确保不低于3.0
                ph=round(max(6.5, min(9.0, base_ph)), 1),  # 确保在合理范围内
                cod=round(random.uniform(10, 30), 1),  # 化学需氧量(mg/L)
                ammonia=round(max(0, base_ammonia), 2),
                heavy_metals=round(random.uniform(0.01, 0.1), 3),  # 重金属(μg/L)
                residual_chlorine=round(random.uniform(0.1, 0.5), 2),  # 余氯(mg/L)
                total_phosphorus=round(random.uniform(0.1, 0.5), 2),  # 总磷(mg/L)
                total_nitrogen=round(random.uniform(0.5, 2.0), 2),  # 总氮(mg/L)
                coliform=round(random.uniform(100, 1000), 0),  # 总大肠菌群(个/L)
                algae=round(random.uniform(1000, 10000), 0),  # 藻类(个/mL)
                biotoxicity=round(random.uniform(5, 20), 1),  # 生物毒性(%)
                timestamp=time_point
            )
            db.session.add(water_quality)
    
    db.session.commit()
    
    # 创建演示投喂记录
    for pond in ponds:
        # 为每个塘口创建一个月的投喂记录
        for i in range(30):  # 一个月的记录
            feeding_date = now - timedelta(days=i)
            
            # 根据塘口类型和面积计算合理的投喂量
            if pond.species == "南美白对虾":
                # 对虾每天投喂两次
                morning_amount = pond.area * random.uniform(3.5, 4.5)  # 上午投喂量
                afternoon_amount = pond.area * random.uniform(2.5, 3.5)  # 下午投喂量
                
                # 上午投喂记录
                morning_feeding = FeedingRecord(
                    pond_id=pond.id,
                    amount=round(morning_amount, 1),
                    time=feeding_date.replace(hour=8, minute=0, second=0, microsecond=0),
                    notes="对虾配合饲料"
                )
                db.session.add(morning_feeding)
                
                # 下午投喂记录
                afternoon_feeding = FeedingRecord(
                    pond_id=pond.id,
                    amount=round(afternoon_amount, 1),
                    time=feeding_date.replace(hour=17, minute=0, second=0, microsecond=0),
                    notes="对虾配合饲料"
                )
                db.session.add(afternoon_feeding)
            else:  # 草鱼
                # 草鱼每天投喂一次
                daily_amount = pond.area * random.uniform(4.0, 6.0)
                
                daily_feeding = FeedingRecord(
                    pond_id=pond.id,
                    amount=round(daily_amount, 1),
                    time=feeding_date.replace(hour=9, minute=0, second=0, microsecond=0),
                    notes="草鱼配合饲料"
                )
                db.session.add(daily_feeding)
    
    db.session.commit()
    
    # 创建演示预警
    # 为每个塘口创建多种类型的预警记录
    for i, pond in enumerate(ponds):
        # 创建不同类型的预警
        alert_types = [
            {
                "level": "danger",
                "title": "溶解氧严重偏低",
                "message": f"{pond.name}溶解氧降至3.2mg/L，已低于安全阈值！请立即开启增氧机并减少投喂量。",
                "hours_ago": 2
            },
            {
                "level": "warning",
                "title": "pH值异常",
                "message": f"{pond.name}pH值({round(8.7 + i*0.1, 1)})偏高，可能影响鱼类消化吸收。建议使用水质调节剂。",
                "hours_ago": 6
            },
            {
                "level": "warning",
                "title": "氨氮浓度偏高",
                "message": f"{pond.name}氨氮浓度({round(0.45 + i*0.05, 2)}mg/L)偏高，建议减少投喂量并加强换水。",
                "hours_ago": 12
            },
            {
                "level": "info",
                "title": "水温变化较大",
                "message": f"{pond.name}水温在24小时内变化超过3℃，请注意鱼类应激反应。",
                "hours_ago": 18
            },
            {
                "level": "warning",
                "title": "浊度偏高",
                "message": f"{pond.name}浊度({round(22 + i*2, 1)}NTU)偏高，可能影响鱼类呼吸。建议检查过滤系统。",
                "hours_ago": 24
            }
        ]
        
        # 为每个塘口创建预警
        for alert_data in alert_types:
            alert = Alert(
                pond_id=pond.id,
                level=alert_data["level"],
                title=alert_data["title"],
                message=alert_data["message"],
                timestamp=now - timedelta(hours=alert_data["hours_ago"]),
                status="active" if alert_data["hours_ago"] < 12 else "resolved"  # 12小时内的预警为活跃状态
            )
            db.session.add(alert)
    
    # 添加一些已解决的预警记录
    for i, pond in enumerate(ponds[:2]):  # 只为前两个塘口添加已解决的预警
        resolved_alerts = [
            {
                "level": "warning",
                "title": "溶解氧偏低",
                "message": f"{pond.name}夜间溶解氧降至4.0mg/L，已开启增氧机处理。",
                "days_ago": 2
            },
            {
                "level": "info",
                "title": "投喂建议",
                "message": f"根据当前水质状况，建议{pond.name}今日投喂量减少10%。",
                "days_ago": 4
            }
        ]
        
        for alert_data in resolved_alerts:
            alert = Alert(
                pond_id=pond.id,
                level=alert_data["level"],
                title=alert_data["title"],
                message=alert_data["message"],
                timestamp=now - timedelta(days=alert_data["days_ago"]),
                status="resolved"
            )
            db.session.add(alert)
    
    db.session.commit()

# 创建数据库表和演示数据
with app.app_context():
    db.create_all()
    create_demo_data()

if __name__ == '__main__':
    # Release模式：关闭调试，使用生产环境配置
    app.run(debug=False, host='0.0.0.0', port=5000)