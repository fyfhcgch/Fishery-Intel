from flask import Blueprint, render_template, jsonify, request, Response, send_file
from datetime import datetime, timedelta
import random
import csv
import io
import pandas as pd
from models import db, Pond, WaterQuality

data_bp = Blueprint('data', __name__)

@data_bp.route('/')
def data():
    """实时数据页面"""
    # 获取所有塘口
    ponds = Pond.query.all()
    
    # 获取选中的塘口ID，默认为第一个塘口
    selected_pond_id = request.args.get('pond_id', type=int)
    if not selected_pond_id and ponds:
        selected_pond_id = ponds[0].id
    
    return render_template('data.html', ponds=ponds, selected_pond_id=selected_pond_id)

@data_bp.route('/api/pond/<int:pond_id>')
def get_pond_data(pond_id):
    """获取塘口数据API"""
    # 获取塘口信息
    pond = Pond.query.get_or_404(pond_id)
    
    # 获取最新水质数据
    latest_water_quality = WaterQuality.query.filter_by(pond_id=pond_id).order_by(WaterQuality.timestamp.desc()).first()
    
    if not latest_water_quality:
        # 如果没有数据，返回模拟数据
        latest_water_quality = {
            'temperature': round(random.uniform(20, 30), 1),
            'dissolved_oxygen': round(random.uniform(4, 8), 1),
            'ph': round(random.uniform(6.5, 8.5), 1),
            'ammonia': round(random.uniform(0.1, 0.5), 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    else:
        latest_water_quality = {
            'temperature': latest_water_quality.temperature,
            'dissolved_oxygen': latest_water_quality.dissolved_oxygen,
            'ph': latest_water_quality.ph,
            'ammonia': latest_water_quality.ammonia,
            'timestamp': latest_water_quality.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    # 获取24小时历史数据
    now = datetime.now()
    history_data = []
    
    for i in range(24):
        time_point = now - timedelta(hours=i)
        water_quality = WaterQuality.query.filter_by(pond_id=pond_id).filter(
            WaterQuality.timestamp <= time_point,
            WaterQuality.timestamp > time_point - timedelta(hours=1)
        ).first()
        
        if water_quality:
            history_data.append({
                'timestamp': water_quality.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': water_quality.temperature,
                'dissolved_oxygen': water_quality.dissolved_oxygen,
                'ph': water_quality.ph,
                'ammonia': water_quality.ammonia
            })
        else:
            # 如果没有数据，生成模拟数据
            base_temp = 25 + random.uniform(-2, 2)
            base_do = 6.0 + random.uniform(-1.5, 1.5)
            base_ph = 7.5 + random.uniform(-0.5, 0.5)
            base_ammonia = 0.2 + random.uniform(-0.1, 0.2)
            
            # 模拟夜间溶解氧下降
            if time_point.hour >= 0 and time_point.hour <= 6:
                base_do -= random.uniform(0.5, 1.5)
            
            # 模拟午后温度升高
            if time_point.hour >= 12 and time_point.hour <= 15:
                base_temp += random.uniform(1, 3)
            
            history_data.append({
                'timestamp': time_point.strftime('%Y-%m-%d %H:%M:%S'),
                'temperature': round(base_temp, 1),
                'dissolved_oxygen': round(max(3.0, base_do), 1),
                'ph': round(max(6.5, min(8.5, base_ph)), 1),
                'ammonia': round(max(0, base_ammonia), 2)
            })
    
    # 反转历史数据，使时间从早到晚
    history_data.reverse()
    
    return jsonify({
        'pond': {
            'id': pond.id,
            'name': pond.name,
            'area': pond.area,
            'species': pond.species
        },
        'current': latest_water_quality,
        'history': history_data
    })

@data_bp.route('/api/ponds')
def get_ponds():
    """获取所有塘口API"""
    ponds = Pond.query.all()
    
    ponds_data = []
    for pond in ponds:
        # 获取最新水质数据
        latest_water_quality = WaterQuality.query.filter_by(pond_id=pond.id).order_by(WaterQuality.timestamp.desc()).first()
        
        if latest_water_quality:
            pond_data = {
                'id': pond.id,
                'name': pond.name,
                'area': pond.area,
                'species': pond.species,
                'temperature': latest_water_quality.temperature,
                'dissolved_oxygen': latest_water_quality.dissolved_oxygen,
                'ph': latest_water_quality.ph,
                'ammonia': latest_water_quality.ammonia,
                'timestamp': latest_water_quality.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            # 如果没有数据，返回模拟数据
            pond_data = {
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
        
        ponds_data.append(pond_data)
    
    return jsonify(ponds_data)

@data_bp.route('/api/water_quality/<int:pond_id>')
def get_water_quality_data(pond_id):
    """获取塘口水质趋势数据API"""
    # 获取请求参数
    days = request.args.get('days', 1, type=int)
    compare = request.args.get('compare', 0, type=int)  # 是否需要昨日对比数据
    
    # 获取塘口信息
    pond = Pond.query.get_or_404(pond_id)
    
    # 计算时间范围
    now = datetime.now()
    start_time = now - timedelta(days=days)
    
    # 获取当前数据
    current_data = []
    water_qualities = WaterQuality.query.filter_by(pond_id=pond_id).filter(
        WaterQuality.timestamp >= start_time
    ).order_by(WaterQuality.timestamp.asc()).all()
    
    if water_qualities:
        for wq in water_qualities:
            current_data.append({
                'timestamp': wq.timestamp.isoformat(),
                'temperature': wq.temperature,
                'turbidity': wq.turbidity,
                'conductivity': wq.conductivity,
                'water_level': wq.water_level,
                'dissolved_oxygen': wq.dissolved_oxygen,
                'ph': wq.ph,
                'cod': wq.cod,
                'ammonia': wq.ammonia,
                'heavy_metals': wq.heavy_metals,
                'residual_chlorine': wq.residual_chlorine,
                'total_phosphorus': wq.total_phosphorus,
                'total_nitrogen': wq.total_nitrogen,
                'coliform': wq.coliform,
                'algae': wq.algae,
                'biotoxicity': wq.biotoxicity
            })
    else:
        # 如果没有数据，生成模拟数据
        if days <= 7:
            # 7天及以内，按小时生成数据
            hours = days * 24
            for i in range(hours):
                time_point = now - timedelta(hours=hours-i)
                
                # 根据塘口类型模拟不同的基础数据
                if pond.species == "南美白对虾":
                    base_temp = 28 + random.uniform(-2, 2)
                    base_do = 6.5 + random.uniform(-1.0, 1.0)
                    base_ph = 8.0 + random.uniform(-0.3, 0.3)
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
                
                # 模拟投喂后氨氮升高
                if time_point.hour in [9, 10] or time_point.hour in [18, 19]:
                    base_ammonia += random.uniform(0.1, 0.3)
                
                # 偶尔模拟水质异常情况
                if random.random() < 0.02:
                    if random.random() < 0.5:
                        base_do -= random.uniform(1.5, 2.5)
                    else:
                        base_ph += random.uniform(0.8, 1.2)
                
                current_data.append({
                    'timestamp': time_point.isoformat(),
                    'temperature': round(base_temp, 1),
                    'turbidity': round(random.uniform(5, 25), 1),
                    'conductivity': round(random.uniform(300, 800), 0),
                    'water_level': round(random.uniform(1.5, 2.5), 2),
                    'dissolved_oxygen': round(max(3.0, base_do), 1),
                    'ph': round(max(6.5, min(9.0, base_ph)), 1),
                    'cod': round(random.uniform(10, 30), 1),
                    'ammonia': round(max(0, base_ammonia), 2),
                    'heavy_metals': round(random.uniform(0.01, 0.1), 3),
                    'residual_chlorine': round(random.uniform(0.1, 0.5), 2),
                    'total_phosphorus': round(random.uniform(0.1, 0.5), 2),
                    'total_nitrogen': round(random.uniform(0.5, 2.0), 2),
                    'coliform': round(random.uniform(100, 1000), 0),
                    'algae': round(random.uniform(1000, 10000), 0),
                    'biotoxicity': round(random.uniform(5, 20), 1)
                })
        else:
            # 超过7天，按天生成数据（每天取中午12点的数据）
            for i in range(days):
                time_point = now - timedelta(days=days-i)
                time_point = time_point.replace(hour=12, minute=0, second=0, microsecond=0)
                
                # 根据塘口类型模拟不同的基础数据
                if pond.species == "南美白对虾":
                    base_temp = 28 + random.uniform(-2, 2)
                    base_do = 6.5 + random.uniform(-1.0, 1.0)
                    base_ph = 8.0 + random.uniform(-0.3, 0.3)
                    base_ammonia = 0.15 + random.uniform(-0.05, 0.1)
                else:  # 草鱼
                    base_temp = 24 + random.uniform(-2, 2)
                    base_do = 7.0 + random.uniform(-1.0, 1.5)
                    base_ph = 7.5 + random.uniform(-0.5, 0.5)
                    base_ammonia = 0.2 + random.uniform(-0.1, 0.2)
                
                # 模拟一些天的水质异常情况
                if random.random() < 0.05:
                    if random.random() < 0.5:
                        base_do -= random.uniform(1.5, 2.5)
                    else:
                        base_ph += random.uniform(0.8, 1.2)
                
                current_data.append({
                    'timestamp': time_point.isoformat(),
                    'temperature': round(base_temp, 1),
                    'turbidity': round(random.uniform(5, 25), 1),
                    'conductivity': round(random.uniform(300, 800), 0),
                    'water_level': round(random.uniform(1.5, 2.5), 2),
                    'dissolved_oxygen': round(max(3.0, base_do), 1),
                    'ph': round(max(6.5, min(9.0, base_ph)), 1),
                    'cod': round(random.uniform(10, 30), 1),
                    'ammonia': round(max(0, base_ammonia), 2),
                    'heavy_metals': round(random.uniform(0.01, 0.1), 3),
                    'residual_chlorine': round(random.uniform(0.1, 0.5), 2),
                    'total_phosphorus': round(random.uniform(0.1, 0.5), 2),
                    'total_nitrogen': round(random.uniform(0.5, 2.0), 2),
                    'coliform': round(random.uniform(100, 1000), 0),
                    'algae': round(random.uniform(1000, 10000), 0),
                    'biotoxicity': round(random.uniform(5, 20), 1)
                })
    
    # 获取昨日数据（用于对比）
    yesterday_data = []
    if compare == 1:  # 只有在需要对比时才提供昨日数据
        yesterday_start = start_time - timedelta(days=1)
        yesterday_end = now - timedelta(days=1)
        
        yesterday_water_qualities = WaterQuality.query.filter_by(pond_id=pond_id).filter(
            WaterQuality.timestamp >= yesterday_start,
            WaterQuality.timestamp <= yesterday_end
        ).order_by(WaterQuality.timestamp.asc()).all()
        
        if yesterday_water_qualities:
            for wq in yesterday_water_qualities:
                yesterday_data.append({
                    'timestamp': wq.timestamp.isoformat(),
                    'temperature': wq.temperature,
                    'dissolved_oxygen': wq.dissolved_oxygen,
                    'ph': wq.ph,
                    'ammonia': wq.ammonia
                })
        else:
            # 生成模拟数据
            if days <= 7:
                # 7天及以内，按小时生成数据
                for i in range(days * 24):
                    time_point = yesterday_start + timedelta(hours=i)
                    
                    # 模拟昨日数据
                    base_temp = 25 + random.uniform(-2, 2)
                    base_do = 6.0 + random.uniform(-1.5, 1.5)
                    base_ph = 7.5 + random.uniform(-0.5, 0.5)
                    base_ammonia = 0.2 + random.uniform(-0.1, 0.2)
                    
                    if time_point.hour >= 0 and time_point.hour <= 6:
                        base_do -= random.uniform(0.8, 1.8)
                    
                    if time_point.hour >= 12 and time_point.hour <= 15:
                        base_temp += random.uniform(1, 3)
                    
                    yesterday_data.append({
                        'timestamp': time_point.isoformat(),
                        'temperature': round(base_temp, 1),
                        'dissolved_oxygen': round(max(3.0, base_do), 1),
                        'ph': round(max(6.5, min(9.0, base_ph)), 1),
                        'ammonia': round(max(0, base_ammonia), 2)
                    })
            else:
                # 超过7天，按天生成数据（每天取中午12点的数据）
                for i in range(days):
                    time_point = yesterday_start + timedelta(days=i)
                    time_point = time_point.replace(hour=12, minute=0, second=0, microsecond=0)
                    
                    # 模拟昨日数据
                    base_temp = 25 + random.uniform(-2, 2)
                    base_do = 6.0 + random.uniform(-1.5, 1.5)
                    base_ph = 7.5 + random.uniform(-0.5, 0.5)
                    base_ammonia = 0.2 + random.uniform(-0.1, 0.2)
                    
                    yesterday_data.append({
                        'timestamp': time_point.isoformat(),
                        'temperature': round(base_temp, 1),
                        'dissolved_oxygen': round(max(3.0, base_do), 1),
                        'ph': round(max(6.5, min(9.0, base_ph)), 1),
                        'ammonia': round(max(0, base_ammonia), 2)
                    })
    
    # 生成事件数据
    events = []
    if days <= 7:  # 只在查看7天及以内数据时提供事件
        # 模拟一些事件
        event_count = min(5, max(1, days // 2))
        for i in range(event_count):
            event_time = now - timedelta(hours=random.randint(1, days*24))
            event_type = random.choice(['warning', 'info', 'danger'])
            event_title = random.choice([
                '溶解氧偏低',
                'pH值异常',
                '氨氮升高',
                '水温变化',
                '投喂建议'
            ])
            
            events.append({
                'timestamp': event_time.isoformat(),
                'type': event_type,
                'title': event_title,
                'description': f'{pond.name}在{event_time.strftime("%m月%d日 %H:%M")}发生{event_title}，请及时处理。'
            })
    
    return jsonify({
        'pond': {
            'id': pond.id,
            'name': pond.name,
            'area': pond.area,
            'species': pond.species
        },
        'current_data': current_data,
        'yesterday_data': yesterday_data,
        'events': events
    })

@data_bp.route('/export')
def export_data():
    """导出水质数据API"""
    # 获取请求参数
    export_format = request.args.get('format', 'csv')
    days = request.args.get('days', 7, type=int)
    pond_id = request.args.get('pond_id', type=int)
    
    # 计算时间范围
    now = datetime.now()
    start_time = now - timedelta(days=days)
    
    # 查询数据
    if pond_id:
        # 导出特定塘口的数据
        pond = Pond.query.get_or_404(pond_id)
        water_qualities = WaterQuality.query.filter_by(pond_id=pond_id).filter(
            WaterQuality.timestamp >= start_time
        ).order_by(WaterQuality.timestamp.asc()).all()
        
        # 如果没有真实数据，生成模拟数据
        if not water_qualities:
            water_qualities = []
            if days <= 7:
                # 7天及以内，按小时生成数据
                hours = days * 24
                for i in range(hours):
                    time_point = now - timedelta(hours=hours-i)
                    
                    # 根据塘口类型模拟不同的基础数据
                    if pond.species == "南美白对虾":
                        base_temp = 28 + random.uniform(-2, 2)
                        base_do = 6.5 + random.uniform(-1.0, 1.0)
                        base_ph = 8.0 + random.uniform(-0.3, 0.3)
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
                    
                    # 模拟投喂后氨氮升高
                    if time_point.hour in [9, 10] or time_point.hour in [18, 19]:
                        base_ammonia += random.uniform(0.1, 0.3)
                    
                    # 创建模拟数据对象
                    wq = type('WaterQuality', (), {
                        'timestamp': time_point,
                        'temperature': round(base_temp, 1),
                        'turbidity': round(random.uniform(5, 25), 1),
                        'conductivity': round(random.uniform(300, 800), 0),
                        'water_level': round(random.uniform(1.5, 2.5), 2),
                        'dissolved_oxygen': round(max(3.0, base_do), 1),
                        'ph': round(max(6.5, min(9.0, base_ph)), 1),
                        'cod': round(random.uniform(10, 30), 1),
                        'ammonia': round(max(0, base_ammonia), 2),
                        'heavy_metals': round(random.uniform(0.01, 0.1), 3),
                        'residual_chlorine': round(random.uniform(0.1, 0.5), 2),
                        'total_phosphorus': round(random.uniform(0.1, 0.5), 2),
                        'total_nitrogen': round(random.uniform(0.5, 2.0), 2),
                        'coliform': round(random.uniform(100, 1000), 0),
                        'algae': round(random.uniform(1000, 10000), 0),
                        'biotoxicity': round(random.uniform(5, 20), 1)
                    })()
                    water_qualities.append(wq)
            else:
                # 超过7天，按天生成数据（每天取中午12点的数据）
                for i in range(days):
                    time_point = now - timedelta(days=days-i)
                    time_point = time_point.replace(hour=12, minute=0, second=0, microsecond=0)
                    
                    # 根据塘口类型模拟不同的基础数据
                    if pond.species == "南美白对虾":
                        base_temp = 28 + random.uniform(-2, 2)
                        base_do = 6.5 + random.uniform(-1.0, 1.0)
                        base_ph = 8.0 + random.uniform(-0.3, 0.3)
                        base_ammonia = 0.15 + random.uniform(-0.05, 0.1)
                    else:  # 草鱼
                        base_temp = 24 + random.uniform(-2, 2)
                        base_do = 7.0 + random.uniform(-1.0, 1.5)
                        base_ph = 7.5 + random.uniform(-0.5, 0.5)
                        base_ammonia = 0.2 + random.uniform(-0.1, 0.2)
                    
                    # 模拟一些天的水质异常情况
                    if random.random() < 0.05:
                        if random.random() < 0.5:
                            base_do -= random.uniform(1.5, 2.5)
                        else:
                            base_ph += random.uniform(0.8, 1.2)
                    
                    # 创建模拟数据对象
                    wq = type('WaterQuality', (), {
                        'timestamp': time_point,
                        'temperature': round(base_temp, 1),
                        'turbidity': round(random.uniform(5, 25), 1),
                        'conductivity': round(random.uniform(300, 800), 0),
                        'water_level': round(random.uniform(1.5, 2.5), 2),
                        'dissolved_oxygen': round(max(3.0, base_do), 1),
                        'ph': round(max(6.5, min(9.0, base_ph)), 1),
                        'cod': round(random.uniform(10, 30), 1),
                        'ammonia': round(max(0, base_ammonia), 2),
                        'heavy_metals': round(random.uniform(0.01, 0.1), 3),
                        'residual_chlorine': round(random.uniform(0.1, 0.5), 2),
                        'total_phosphorus': round(random.uniform(0.1, 0.5), 2),
                        'total_nitrogen': round(random.uniform(0.5, 2.0), 2),
                        'coliform': round(random.uniform(100, 1000), 0),
                        'algae': round(random.uniform(1000, 10000), 0),
                        'biotoxicity': round(random.uniform(5, 20), 1)
                    })()
                    water_qualities.append(wq)
        
        # 准备数据
        data = []
        for wq in water_qualities:
            data.append({
                '塘口名称': pond.name,
                '养殖品种': pond.species,
                '记录时间': wq.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                '水温(°C)': wq.temperature,
                '浊度(NTU)': wq.turbidity,
                '电导率(μS/cm)': wq.conductivity,
                '水位(m)': wq.water_level,
                '溶解氧(mg/L)': wq.dissolved_oxygen,
                'pH值': wq.ph,
                '化学需氧量(mg/L)': wq.cod,
                '氨氮(mg/L)': wq.ammonia,
                '重金属(mg/L)': wq.heavy_metals,
                '余氯(mg/L)': wq.residual_chlorine,
                '总磷(mg/L)': wq.total_phosphorus,
                '总氮(mg/L)': wq.total_nitrogen,
                '大肠杆菌群(CFU/L)': wq.coliform,
                '藻类密度(个/L)': wq.algae,
                '生物毒性(%)': wq.biotoxicity
            })
        
        filename = f"{pond.name}_水质数据_{start_time.strftime('%Y%m%d')}_{now.strftime('%Y%m%d')}"
    else:
        # 导出所有塘口的数据
        ponds = Pond.query.all()
        data = []
        
        for pond in ponds:
            pond_water_qualities = WaterQuality.query.filter_by(pond_id=pond.id).filter(
                WaterQuality.timestamp >= start_time
            ).order_by(WaterQuality.timestamp.asc()).all()
            
            # 如果没有真实数据，生成模拟数据
            if not pond_water_qualities:
                pond_water_qualities = []
                if days <= 7:
                    # 7天及以内，按小时生成数据
                    hours = days * 24
                    for i in range(hours):
                        time_point = now - timedelta(hours=hours-i)
                        
                        # 根据塘口类型模拟不同的基础数据
                        if pond.species == "南美白对虾":
                            base_temp = 28 + random.uniform(-2, 2)
                            base_do = 6.5 + random.uniform(-1.0, 1.0)
                            base_ph = 8.0 + random.uniform(-0.3, 0.3)
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
                        
                        # 模拟投喂后氨氮升高
                        if time_point.hour in [9, 10] or time_point.hour in [18, 19]:
                            base_ammonia += random.uniform(0.1, 0.3)
                        
                        # 创建模拟数据对象
                        wq = type('WaterQuality', (), {
                            'timestamp': time_point,
                            'temperature': round(base_temp, 1),
                            'turbidity': round(random.uniform(5, 25), 1),
                            'conductivity': round(random.uniform(300, 800), 0),
                            'water_level': round(random.uniform(1.5, 2.5), 2),
                            'dissolved_oxygen': round(max(3.0, base_do), 1),
                            'ph': round(max(6.5, min(9.0, base_ph)), 1),
                            'cod': round(random.uniform(10, 30), 1),
                            'ammonia': round(max(0, base_ammonia), 2),
                            'heavy_metals': round(random.uniform(0.01, 0.1), 3),
                            'residual_chlorine': round(random.uniform(0.1, 0.5), 2),
                            'total_phosphorus': round(random.uniform(0.1, 0.5), 2),
                            'total_nitrogen': round(random.uniform(0.5, 2.0), 2),
                            'coliform': round(random.uniform(100, 1000), 0),
                            'algae': round(random.uniform(1000, 10000), 0),
                            'biotoxicity': round(random.uniform(5, 20), 1)
                        })()
                        pond_water_qualities.append(wq)
                else:
                    # 超过7天，按天生成数据（每天取中午12点的数据）
                    for i in range(days):
                        time_point = now - timedelta(days=days-i)
                        time_point = time_point.replace(hour=12, minute=0, second=0, microsecond=0)
                        
                        # 根据塘口类型模拟不同的基础数据
                        if pond.species == "南美白对虾":
                            base_temp = 28 + random.uniform(-2, 2)
                            base_do = 6.5 + random.uniform(-1.0, 1.0)
                            base_ph = 8.0 + random.uniform(-0.3, 0.3)
                            base_ammonia = 0.15 + random.uniform(-0.05, 0.1)
                        else:  # 草鱼
                            base_temp = 24 + random.uniform(-2, 2)
                            base_do = 7.0 + random.uniform(-1.0, 1.5)
                            base_ph = 7.5 + random.uniform(-0.5, 0.5)
                            base_ammonia = 0.2 + random.uniform(-0.1, 0.2)
                        
                        # 模拟一些天的水质异常情况
                        if random.random() < 0.05:
                            if random.random() < 0.5:
                                base_do -= random.uniform(1.5, 2.5)
                            else:
                                base_ph += random.uniform(0.8, 1.2)
                        
                        # 创建模拟数据对象
                        wq = type('WaterQuality', (), {
                            'timestamp': time_point,
                            'temperature': round(base_temp, 1),
                            'turbidity': round(random.uniform(5, 25), 1),
                            'conductivity': round(random.uniform(300, 800), 0),
                            'water_level': round(random.uniform(1.5, 2.5), 2),
                            'dissolved_oxygen': round(max(3.0, base_do), 1),
                            'ph': round(max(6.5, min(9.0, base_ph)), 1),
                            'cod': round(random.uniform(10, 30), 1),
                            'ammonia': round(max(0, base_ammonia), 2),
                            'heavy_metals': round(random.uniform(0.01, 0.1), 3),
                            'residual_chlorine': round(random.uniform(0.1, 0.5), 2),
                            'total_phosphorus': round(random.uniform(0.1, 0.5), 2),
                            'total_nitrogen': round(random.uniform(0.5, 2.0), 2),
                            'coliform': round(random.uniform(100, 1000), 0),
                            'algae': round(random.uniform(1000, 10000), 0),
                            'biotoxicity': round(random.uniform(5, 20), 1)
                        })()
                        pond_water_qualities.append(wq)
            
            for wq in pond_water_qualities:
                data.append({
                    '塘口名称': pond.name,
                    '养殖品种': pond.species,
                    '记录时间': wq.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    '水温(°C)': wq.temperature,
                    '浊度(NTU)': wq.turbidity,
                    '电导率(μS/cm)': wq.conductivity,
                    '水位(m)': wq.water_level,
                    '溶解氧(mg/L)': wq.dissolved_oxygen,
                    'pH值': wq.ph,
                    '化学需氧量(mg/L)': wq.cod,
                    '氨氮(mg/L)': wq.ammonia,
                    '重金属(mg/L)': wq.heavy_metals,
                    '余氯(mg/L)': wq.residual_chlorine,
                    '总磷(mg/L)': wq.total_phosphorus,
                    '总氮(mg/L)': wq.total_nitrogen,
                    '大肠杆菌群(CFU/L)': wq.coliform,
                    '藻类密度(个/L)': wq.algae,
                    '生物毒性(%)': wq.biotoxicity
                })
        
        filename = f"所有塘口_水质数据_{start_time.strftime('%Y%m%d')}_{now.strftime('%Y%m%d')}"
    
    # 根据格式导出数据
    if export_format == 'csv':
        # 创建CSV文件
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
        writer.writeheader()
        writer.writerows(data)
        
        # 将StringIO转换为BytesIO以支持二进制下载
        csv_bytes = io.BytesIO()
        csv_bytes.write(output.getvalue().encode('utf-8-sig'))  # 使用utf-8-sig以支持Excel正确打开CSV
        csv_bytes.seek(0)
        
        # 创建响应
        return send_file(
            csv_bytes,
            as_attachment=True,
            download_name=f'{filename}.csv',
            mimetype='text/csv'
        )
    
    elif export_format == 'excel':
        # 创建Excel文件
        df = pd.DataFrame(data)
        
        # 创建内存中的Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='水质数据')
        
        output.seek(0)
        
        # 创建响应
        return send_file(
            output,
            as_attachment=True,
            download_name=f'{filename}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    elif export_format == 'json':
        # 创建JSON数据
        import json
        
        # 如果是单个塘口，添加塘口信息
        if pond_id:
            json_data = {
                'pond_info': {
                    'name': pond.name,
                    'species': pond.species,
                    'area': pond.area
                },
                'export_info': {
                    'time_range': f"{start_time.strftime('%Y-%m-%d')} 至 {now.strftime('%Y-%m-%d')}",
                    'total_records': len(data)
                },
                'water_quality_data': data
            }
        else:
            # 多个塘口的数据
            json_data = {
                'export_info': {
                    'time_range': f"{start_time.strftime('%Y-%m-%d')} 至 {now.strftime('%Y-%m-%d')}",
                    'total_records': len(data)
                },
                'water_quality_data': data
            }
        
        # 创建响应
        response = Response(
            json.dumps(json_data, ensure_ascii=False, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={filename}.json'}
        )
        return response
    
    else:
        return jsonify({'error': '不支持的导出格式'}), 400


@data_bp.route('/api/latest_water_quality')
def get_latest_water_quality():
    """获取最新水质数据API"""
    # 获取所有塘口
    ponds = Pond.query.all()
    latest_data = {}
    
    for pond in ponds:
        # 获取每个塘口的最新水质数据
        latest_record = WaterQuality.query.filter_by(pond_id=pond.id).order_by(WaterQuality.timestamp.desc()).first()
        if latest_record:
            latest_data[pond.id] = {
                'temperature': latest_record.temperature,
                'dissolved_oxygen': latest_record.dissolved_oxygen,
                'ph': latest_record.ph,
                'ammonia': latest_record.ammonia,
                'timestamp': latest_record.timestamp.isoformat()
            }
        else:
            # 如果没有数据，返回模拟数据
            latest_data[pond.id] = {
                'temperature': round(random.uniform(20, 30), 1),
                'dissolved_oxygen': round(random.uniform(4, 8), 1),
                'ph': round(random.uniform(6.5, 8.5), 1),
                'ammonia': round(random.uniform(0.1, 0.5), 2),
                'timestamp': datetime.now().isoformat()
            }
    
    return jsonify(latest_data)