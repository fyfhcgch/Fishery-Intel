from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
import random
from models import db, Alert, Pond, WaterQuality

alert_bp = Blueprint('alert', __name__, url_prefix='/alert')

@alert_bp.route('/')
def alerts():
    """预警与通知页面"""
    # 获取所有塘口信息
    ponds = Pond.query.all()
    
    # 获取最近4周的时间范围用于周报选择
    weeks = []
    for i in range(4):
        week_end = datetime.now().date() - timedelta(days=i*7)
        week_start = week_end - timedelta(days=6)
        weeks.append({
            'id': i+1,
            'start_date': week_start.strftime('%Y-%m-%d'),
            'end_date': week_end.strftime('%Y-%m-%d')
        })
    
    return render_template('alerts.html', ponds=ponds, weeks=weeks, selected_week_id=1)

def generate_active_alerts():
    """生成活跃预警数据 - 共享函数，确保统计API和活跃预警API使用相同数据"""
    # 检查session中是否已有预警数据
    if 'active_alerts' in session and session['active_alerts']:
        print(f"DEBUG: Using cached alerts from session, count: {len(session['active_alerts'])}")
        return session['active_alerts']
    
    # 模拟获取活跃预警数据
    active_alerts = []
    
    # 获取所有塘口
    ponds = Pond.query.all()
    print(f"DEBUG: Found {len(ponds)} ponds")
    
    # 为每个塘口生成可能的预警
    has_generated_alert = False
    for pond in ponds:
        # 随机决定是否有预警，但确保至少有一个预警用于测试
        should_generate_alert = random.random() < 0.8 or not has_generated_alert
        if should_generate_alert:
            has_generated_alert = True
            alert_types = ['dissolved_oxygen', 'temperature', 'ph', 'ammonia', 'turbidity', 'conductivity', 'water_level', 'cod', 'heavy_metals', 'residual_chlorine', 'total_phosphorus', 'total_nitrogen', 'coliform', 'algae', 'biotoxicity']
            alert_type = random.choice(alert_types)
            
            # 根据预警类型设置内容
            if alert_type == 'dissolved_oxygen':
                title = '溶解氧过低'
                message = f'{pond.name}溶解氧值为{random.uniform(2.0, 3.4):.1f}mg/L，低于安全阈值'
                level = 'danger' if random.random() < 0.5 else 'warning'
            elif alert_type == 'temperature':
                title = '水温异常'
                message = f'{pond.name}水温为{random.uniform(15, 18):.1f}°C，超出适宜范围'
                level = 'warning'
            elif alert_type == 'ph':
                title = 'pH值异常'
                message = f'{pond.name}pH值为{random.uniform(6.0, 6.5):.1f}，超出适宜范围'
                level = 'warning'
            elif alert_type == 'ammonia':
                title = '氨氮过高'
                message = f'{pond.name}氨氮浓度为{random.uniform(0.4, 0.8):.1f}mg/L，超过安全阈值'
                level = 'danger' if random.random() < 0.6 else 'warning'
            elif alert_type == 'turbidity':
                title = '浊度异常'
                message = f'{pond.name}浊度为{random.uniform(25, 40):.1f}NTU，超出正常范围'
                level = 'warning'
            elif alert_type == 'conductivity':
                title = '电导率异常'
                message = f'{pond.name}电导率为{random.uniform(800, 1200):.0f}μS/cm，超出正常范围'
                level = 'warning'
            elif alert_type == 'water_level':
                title = '液位异常'
                message = f'{pond.name}液位为{random.uniform(0.8, 1.2):.2f}m，低于安全水位'
                level = 'danger'
            elif alert_type == 'cod':
                title = '化学需氧量过高'
                message = f'{pond.name}化学需氧量为{random.uniform(30, 50):.1f}mg/L，超过安全阈值'
                level = 'danger' if random.random() < 0.7 else 'warning'
            elif alert_type == 'heavy_metals':
                title = '重金属含量异常'
                message = f'{pond.name}重金属含量为{random.uniform(0.1, 0.2):.3f}μg/L，超过安全阈值'
                level = 'danger'
            elif alert_type == 'residual_chlorine':
                title = '余氯含量异常'
                message = f'{pond.name}余氯含量为{random.uniform(0.5, 0.8):.2f}mg/L，超出正常范围'
                level = 'warning'
            elif alert_type == 'total_phosphorus':
                title = '总磷含量过高'
                message = f'{pond.name}总磷含量为{random.uniform(0.5, 1.0):.2f}mg/L，超过安全阈值'
                level = 'warning'
            elif alert_type == 'total_nitrogen':
                title = '总氮含量过高'
                message = f'{pond.name}总氮含量为{random.uniform(2.0, 3.0):.2f}mg/L，超过安全阈值'
                level = 'warning'
            elif alert_type == 'coliform':
                title = '总大肠菌群超标'
                message = f'{pond.name}总大肠菌群数为{random.uniform(1000, 2000):.0f}个/L，超过安全标准'
                level = 'danger' if random.random() < 0.6 else 'warning'
            elif alert_type == 'algae':
                title = '藻类密度过高'
                message = f'{pond.name}藻类密度为{random.uniform(10000, 20000):.0f}个/mL，可能引发水华'
                level = 'warning'
            else:  # biotoxicity
                title = '生物毒性异常'
                message = f'{pond.name}生物毒性为{random.uniform(20, 30):.1f}%，超过安全阈值'
                level = 'danger'
            
            alert = {
                'id': random.randint(1000, 9999),
                'pond_id': pond.id,
                'pond_name': pond.name,
                'type': alert_type,
                'title': title,
                'message': message,
                'level': level,
                'status': 'active',  # 添加状态字段，默认为active
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(5, 60))).strftime('%Y-%m-%d %H:%M:%S'),
                'value': random.uniform(2.0, 8.0),
                'threshold': random.uniform(3.0, 5.0)
            }
            
            active_alerts.append(alert)
    
    # 将数据存储到session中
    session['active_alerts'] = active_alerts
    print(f"DEBUG: Generated {len(active_alerts)} active alerts")
    
    return active_alerts

@alert_bp.route('/api/active_alerts')
def get_active_alerts():
    """获取活跃预警API"""
    active_alerts = generate_active_alerts()
    print(f"DEBUG: Returning {len(active_alerts)} alerts from get_active_alerts")
    for alert in active_alerts:
        print(f"DEBUG: Alert ID: {alert['id']}, Status: {alert['status']}")
    return jsonify(active_alerts)

@alert_bp.route('/api/refresh_alerts')
def refresh_alerts():
    """刷新预警数据API - 清除缓存并重新生成数据"""
    if 'active_alerts' in session:
        session.pop('active_alerts')
    active_alerts = generate_active_alerts()
    session['active_alerts'] = active_alerts
    return jsonify(active_alerts)

@alert_bp.route('/api/alert_history')
def get_alert_history():
    """获取预警历史API"""
    # 获取查询参数
    level = request.args.get('level', '')
    status = request.args.get('status', '')
    pond = request.args.get('pond', '')
    
    # 模拟预警历史数据
    alert_history = []
    
    # 获取所有塘口
    ponds = Pond.query.all()
    
    # 生成历史预警
    for i in range(50):  # 生成50条历史记录
        pond = random.choice(ponds) if ponds else Pond.query.first()
        alert_types = ['dissolved_oxygen', 'temperature', 'ph', 'ammonia', 'turbidity', 'conductivity', 'water_level', 'cod', 'heavy_metals', 'residual_chlorine', 'total_phosphorus', 'total_nitrogen', 'coliform', 'algae', 'biotoxicity']
        alert_type = random.choice(alert_types)
        
        # 根据预警类型设置内容
        if alert_type == 'dissolved_oxygen':
            title = '溶解氧过低'
            message = f'{pond.name}溶解氧值过低'
        elif alert_type == 'temperature':
            title = '水温异常'
            message = f'{pond.name}水温异常'
        elif alert_type == 'ph':
            title = 'pH值异常'
            message = f'{pond.name}pH值异常'
        else:  # ammonia
            title = '氨氮过高'
            message = f'{pond.name}氨氮浓度过高'
        
        # 随机生成预警级别
        levels = ['danger', 'warning', 'info']
        alert_level = random.choice(levels)
        
        # 随机生成状态
        alert_status = random.choice(['resolved', 'acknowledged', 'ignored'])
        
        # 生成时间戳（过去30天内）
        timestamp = datetime.now() - timedelta(days=random.randint(0, 30), 
                                              hours=random.randint(0, 23),
                                              minutes=random.randint(0, 59))
        
        alert = {
            'id': i + 1,
            'pond_id': pond.id,
            'pond_name': pond.name,
            'type': alert_type,
            'title': title,
            'message': message,
            'level': alert_level,
            'status': alert_status,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'resolved_at': (timestamp + timedelta(hours=random.randint(1, 24))).strftime('%Y-%m-%d %H:%M:%S') if alert_status == 'resolved' else None
        }
        
        alert_history.append(alert)
    
    # 按时间戳倒序排序
    alert_history.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # 应用过滤器
    if level and level != 'all':
        alert_history = [alert for alert in alert_history if alert['level'] == level]
    
    if status and status != 'all':
        alert_history = [alert for alert in alert_history if alert['status'] == status]
    
    if pond and pond != 'all':
        alert_history = [alert for alert in alert_history if str(alert['pond_id']) == pond]
    
    return jsonify(alert_history)

@alert_bp.route('/api/alert_detail/<int:alert_id>')
def get_alert_detail(alert_id):
    """获取预警详情API"""
    # 模拟预警详情数据
    alert = {
        'id': alert_id,
        'pond_id': random.randint(1, 3),
        'pond_name': f'塘口{alert_id % 3 + 1}号',
        'type': 'dissolved_oxygen',
        'title': '溶解氧过低',
        'message': '塘口溶解氧值低于安全阈值，可能导致鱼类缺氧',
        'level': 'danger',
        'status': 'active',
        'timestamp': (datetime.now() - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S'),
        'value': 2.8,
        'threshold': 3.5,
        'unit': 'mg/L',
        'trend': 'decreasing',
        'suggestion': '立即开启增氧设备，提高水体溶解氧含量',
        'chart_data': {}
    }
    
    # 生成历史数据（过去24小时）
    history = []
    labels = []
    values = []
    
    for i in range(24):
        timestamp = datetime.now() - timedelta(hours=23-i)
        value = 3.5 + random.uniform(-0.5, 0.5)
        
        # 最后几个值呈下降趋势
        if i >= 20:
            value = 3.5 - (i - 19) * 0.1 + random.uniform(-0.1, 0.1)
        
        labels.append(timestamp.strftime('%H:%M'))
        values.append(round(value, 2))
        history.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'value': round(value, 2)
        })
    
    # 设置图表数据
    alert['chart_data'] = {
        'labels': labels,
        'data': values,
        'datasetLabel': '溶解氧 (mg/L)',
        'threshold': 3.5,
        'borderColor': '#007bff',
        'backgroundColor': 'rgba(0, 123, 255, 0.1)'
    }
    
    alert['history'] = history
    
    # 生成相关数据
    alert['related_data'] = {
        'temperature': {
            'current': random.uniform(18, 25),
            'unit': '°C',
            'status': 'normal'
        },
        'ph': {
            'current': random.uniform(7.0, 8.0),
            'unit': '',
            'status': 'normal'
        },
        'ammonia': {
            'current': random.uniform(0.1, 0.3),
            'unit': 'mg/L',
            'status': 'normal'
        }
    }
    
    # 生成建议措施
    alert['recommendations'] = [
        '立即开启增氧设备，提高水体溶解氧含量',
        '检查增氧设备运行状态，确保正常工作',
        '减少投喂量，降低鱼类耗氧量',
        '考虑换水，改善水体环境'
    ]
    
    return jsonify(alert)

@alert_bp.route('/api/mark_resolved/<int:alert_id>', methods=['POST'])
def mark_alert_resolved(alert_id):
    """标记预警为已解决"""
    # 直接从session获取活跃预警数据，不调用generate_active_alerts
    print(f"DEBUG: Session before: {session}")
    if 'active_alerts' not in session:
        session['active_alerts'] = generate_active_alerts()
    
    active_alerts = session['active_alerts']
    print(f"DEBUG: Active alerts from session: {len(active_alerts)}")
    
    # 查找并更新指定ID的预警状态
    found_alert = False
    for alert in active_alerts:
        if alert['id'] == alert_id:
            alert['status'] = 'resolved'
            found_alert = True
            print(f"DEBUG: Found and marked alert {alert_id} as resolved")
            break
    
    if not found_alert:
        print(f"DEBUG: Alert {alert_id} not found in active alerts")
    
    # 更新session中的数据
    session['active_alerts'] = active_alerts
    print(f"DEBUG: Updated session with {len(active_alerts)} alerts")
    print(f"DEBUG: Session after: {session}")
    
    return jsonify({
        'success': True,
        'message': '预警已标记为已解决'
    })

@alert_bp.route('/api/mark_all_resolved', methods=['POST'])
def mark_all_alerts_resolved():
    """标记所有预警为已解决"""
    # 直接从session获取活跃预警数据，不调用generate_active_alerts
    if 'active_alerts' not in session:
        session['active_alerts'] = generate_active_alerts()
    
    active_alerts = session['active_alerts']
    
    # 将所有预警状态更新为'resolved'
    for alert in active_alerts:
        alert['status'] = 'resolved'
    
    # 更新session中的数据
    session['active_alerts'] = active_alerts
    
    return jsonify({
        'success': True,
        'message': '所有预警已标记为已解决'
    })

@alert_bp.route('/api/update_threshold', methods=['POST'])
def update_threshold():
    """更新预警阈值"""
    param_type = request.json.get('type')
    value = request.json.get('value')
    
    # 在实际应用中，这里会更新数据库中的阈值设置
    # 这里只是模拟返回成功响应
    return jsonify({
        'success': True,
        'message': f'{param_type}阈值已更新为{value}'
    })

@alert_bp.route('/api/update_notification_settings', methods=['POST'])
def update_notification_settings():
    """更新通知设置"""
    settings = request.json
    
    # 在实际应用中，这里会更新数据库中的通知设置
    # 这里只是模拟返回成功响应
    return jsonify({
        'success': True,
        'message': '通知设置已更新'
    })

@alert_bp.route('/api/statistics')
def get_alert_statistics():
    """获取预警统计API"""
    # 从session获取活跃预警数据，确保统计与实际显示数据一致
    if 'active_alerts' not in session:
        session['active_alerts'] = generate_active_alerts()
    
    active_alerts = session['active_alerts']
    
    # 计算统计数据
    active_count = len([alert for alert in active_alerts if alert['status'] != 'resolved'])
    warning_count = sum(1 for alert in active_alerts if alert['level'] == 'warning' and alert['status'] != 'resolved')
    info_count = sum(1 for alert in active_alerts if alert['level'] == 'info' and alert['status'] != 'resolved')
    
    # 统计各类型预警数量（排除已解决的）
    alert_type_counts = {}
    for alert in active_alerts:
        if alert['status'] != 'resolved':
            alert_type = alert['type']
            if alert_type not in alert_type_counts:
                alert_type_counts[alert_type] = 0
            alert_type_counts[alert_type] += 1
    
    # 确保所有预警类型都有计数（即使是0）
    all_alert_types = ['dissolved_oxygen', 'temperature', 'ph', 'ammonia', 'turbidity', 'conductivity', 
                      'water_level', 'cod', 'heavy_metals', 'residual_chlorine', 'total_phosphorus', 
                      'total_nitrogen', 'coliform', 'algae', 'biotoxicity']
    
    alert_types = {alert_type: alert_type_counts.get(alert_type, 0) for alert_type in all_alert_types}
    
    # 模拟已解决今日数量和周趋势
    stats = {
        'active': active_count,
        'warning': warning_count,
        'info': info_count,
        'resolved_today': random.randint(3, 8),
        'weekly_trend': [random.randint(0, 10) for _ in range(7)],
        'alert_types': alert_types
    }
    
    return jsonify(stats)


@alert_bp.route('/check_alerts', methods=['POST'])
def check_alerts():
    """检查新预警API"""
    # 在实际应用中，这里应该查询数据库获取自上次检查以来的新预警
    # 目前我们使用session来模拟新预警的产生
    
    # 获取当前活跃预警
    current_alerts = generate_active_alerts()
    
    # 检查session中是否存储了上次的预警ID
    last_alert_ids = session.get('last_alert_ids', set())
    
    # 找出新的预警（不在上次预警ID集合中的）
    new_alerts = []
    current_alert_ids = set()
    
    for alert in current_alerts:
        current_alert_ids.add(alert['id'])
        if alert['id'] not in last_alert_ids:
            new_alerts.append(alert)
    
    # 更新session中的预警ID集合
    session['last_alert_ids'] = current_alert_ids
    
    return jsonify({
        'success': True,
        'new_alerts': new_alerts
    })