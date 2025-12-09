from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from datetime import datetime, timedelta
import random
from models import db, User, Pond, WaterQuality, FeedingRecord, Alert, FeedingDecision

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页"""
    # 获取所有塘口
    ponds = Pond.query.all()
    
    # 获取每个塘口的最新水质数据
    pond_data = []
    latest_water_quality = {}
    
    for pond in ponds:
        latest_wq = WaterQuality.query.filter_by(pond_id=pond.id).order_by(WaterQuality.timestamp.desc()).first()
        
        if latest_wq:
            pond_info = {
                'id': pond.id,
                'name': pond.name,
                'area': pond.area,
                'species': pond.species,
                'temperature': latest_wq.temperature,
                'dissolved_oxygen': latest_wq.dissolved_oxygen,
                'ph': latest_wq.ph,
                'ammonia': latest_wq.ammonia,
                'timestamp': latest_wq.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
            latest_water_quality[pond.id] = latest_wq
        else:
            # 如果没有数据，返回模拟数据
            pond_info = {
                'id': pond.id,
                'name': pond.name,
                'area': pond.area,
                'species': pond.species,
                'temperature': round(random.uniform(20, 30), 1),
                'dissolved_oxygen': round(random.uniform(4, 8), 1),
                'ph': round(random.uniform(6.5, 8.5), 1),
                'ammonia': round(random.uniform(0.1, 0.5), 2),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            # 创建模拟的水质对象
            class MockWaterQuality:
                def __init__(self, pond_id, temp, do, ph, ammonia, timestamp):
                    self.pond_id = pond_id
                    self.temperature = temp
                    self.dissolved_oxygen = do
                    self.ph = ph
                    self.ammonia = ammonia
                    self.timestamp = timestamp
            
            latest_water_quality[pond.id] = MockWaterQuality(
                pond.id,
                pond_info['temperature'],
                pond_info['dissolved_oxygen'],
                pond_info['ph'],
                pond_info['ammonia'],
                datetime.now()
            )
        
        pond_data.append(pond_info)
    
    # 获取活跃预警
    active_alerts = Alert.query.filter_by(status='active').all()
    
    # 获取今日投喂总量
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_feeding = db.session.query(db.func.sum(FeedingRecord.amount)).filter(
        FeedingRecord.time >= today_start
    ).scalar() or 0
    
    # 模拟天气数据
    weather = {
        'temperature': round(random.uniform(15, 30), 1),
        'condition': random.choice(['晴', '多云', '阴', '小雨']),
        'humidity': round(random.uniform(40, 80), 1),
        'wind': f"{random.randint(1, 5)}级",
        'forecast': random.choice([
            '适合投喂，水质稳定',
            '水温较高，建议增加溶氧',
            '天气多变，注意观察',
            '溶氧充足，可正常投喂'
        ])
    }
    
    return render_template('dashboard.html', ponds=pond_data, active_alerts=active_alerts, today_feeding=today_feeding, latest_water_quality=latest_water_quality, weather=weather)

@main_bp.route('/pond/<int:pond_id>')
def pond_detail(pond_id):
    """塘口详情页"""
    # 获取塘口信息
    pond = Pond.query.get_or_404(pond_id)
    
    # 获取最新水质数据
    latest_water_quality = WaterQuality.query.filter_by(pond_id=pond_id).order_by(WaterQuality.timestamp.desc()).first()
    
    # 获取最近的投喂记录（最近7天）
    now = datetime.now()
    feeding_history = []
    
    for i in range(7):
        day_start = now - timedelta(days=i, hours=now.hour, minutes=now.minute, seconds=now.second)
        day_end = day_start + timedelta(days=1)
        
        day_feedings = FeedingRecord.query.filter(
            FeedingRecord.pond_id == pond_id,
            FeedingRecord.time >= day_start,
            FeedingRecord.time < day_end
        ).all()
        
        day_total = sum(feeding.amount for feeding in day_feedings)
        
        feeding_history.append({
            'date': day_start.strftime('%Y-%m-%d'),
            'amount': day_total,
            'count': len(day_feedings)
        })
    
    # 反转历史数据，使时间从早到晚
    feeding_history.reverse()
    
    # 获取预警历史（最近10条）
    alert_history = Alert.query.filter_by(pond_id=pond_id).order_by(Alert.timestamp.desc()).limit(10).all()
    
    # 获取24小时水质数据
    water_quality_history = []
    for i in range(24):
        time_point = now - timedelta(hours=i)
        water_quality = WaterQuality.query.filter_by(pond_id=pond_id).filter(
            WaterQuality.timestamp <= time_point,
            WaterQuality.timestamp > time_point - timedelta(hours=1)
        ).first()
        
        if water_quality:
            water_quality_history.append({
                'timestamp': water_quality.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': water_quality.temperature,
                'dissolved_oxygen': water_quality.dissolved_oxygen,
                'ph': water_quality.ph,
                'ammonia': water_quality.ammonia,
                'turbidity': water_quality.turbidity or 0,
                'conductivity': water_quality.conductivity or 0,
                'water_level': water_quality.water_level or 0,
                'cod': water_quality.cod or 0
            })
        else:
            # 如果没有数据，生成模拟数据
            base_temp = 25 + random.uniform(-2, 2)
            base_do = 6.0 + random.uniform(-1.5, 1.5)
            base_ph = 7.5 + random.uniform(-0.5, 0.5)
            base_ammonia = 0.2 + random.uniform(-0.1, 0.2)
            base_turbidity = 5 + random.uniform(-2, 2)  # 浊度基准值
            base_conductivity = 500 + random.uniform(-100, 100)  # 电导率基准值
            base_water_level = 1.5 + random.uniform(-0.3, 0.3)  # 液位基准值
            base_cod = 15 + random.uniform(-5, 5)  # 化学需氧量基准值
            
            # 模拟夜间溶解氧下降
            if time_point.hour >= 0 and time_point.hour <= 6:
                base_do -= random.uniform(0.5, 1.5)
            
            # 模拟午后温度升高
            if time_point.hour >= 12 and time_point.hour <= 15:
                base_temp += random.uniform(1, 3)
            
            water_quality_history.append({
                'timestamp': time_point.strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': round(base_temp, 1),
                'dissolved_oxygen': round(max(3.0, base_do), 1),
                'ph': round(max(6.5, min(8.5, base_ph)), 1),
                'ammonia': round(max(0, base_ammonia), 2),
                'turbidity': round(max(0, base_turbidity), 1),
                'conductivity': round(max(0, base_conductivity), 0),
                'water_level': round(max(0, base_water_level), 2),
                'cod': round(max(0, base_cod), 1)
            })
    
    # 反转历史数据，使时间从早到晚
    water_quality_history.reverse()
    
    return render_template('pond_detail.html', 
                          pond=pond, 
                          latest_water_quality=latest_water_quality,
                          feeding_history=feeding_history,
                          alert_history=alert_history,
                          water_quality_history=water_quality_history)

@main_bp.route('/profile')
def profile():
    """用户资料页"""
    # 获取所有塘口
    ponds = Pond.query.all()
    
    # 计算养殖品种数量
    species_count = len(set(pond.species for pond in ponds))
    
    # 获取用户信息（这里使用模拟数据）
    user = {
        'username': '张渔农',
        'phone': '13800138000',
        'join_date': '2023-01-15',
        'farm_name': '渔智汇示范养殖场',
        'location': '浙江省杭州市',
        'pond_count': len(ponds),
        'total_area': db.session.query(db.func.sum(Pond.area)).scalar() or 0,
        'species_count': species_count
    }
    
    return render_template('profile.html', user=user, ponds=ponds)



@main_bp.route('/weekly_report')
def weekly_report():
    """周报页"""
    # 获取所有塘口
    ponds = Pond.query.all()
    
    # 获取最近4周的时间范围
    weeks = []
    for i in range(4):
        week_end = datetime.now().date() - timedelta(days=i*7)
        week_start = week_end - timedelta(days=6)
        weeks.append({
            'id': i+1,
            'start_date': week_start.strftime('%Y-%m-%d'),
            'end_date': week_end.strftime('%Y-%m-%d')
        })
    
    return render_template('weekly_report.html', ponds=ponds, weeks=weeks, selected_week_id=1)