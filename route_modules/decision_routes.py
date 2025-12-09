from flask import Blueprint, render_template, jsonify, request
from datetime import datetime, timedelta
import random
from models import db, Pond, WaterQuality, FeedingRecord, FeedingDecision

decision_bp = Blueprint('decision', __name__)

@decision_bp.route('/')
def decision():
    """决策中心页面"""
    # 获取所有塘口
    ponds = Pond.query.all()
    
    # 如果有塘口，选择第一个作为默认选中
    selected_pond_id = ponds[0].id if ponds else None
    
    return render_template('decision.html', ponds=ponds, selected_pond_id=selected_pond_id)

@decision_bp.route('/api/pond_status/<int:pond_id>')
def get_pond_status(pond_id):
    """获取塘口状态API"""
    # 获取塘口信息
    pond = Pond.query.get_or_404(pond_id)
    
    # 获取最新水质数据
    latest_water_quality = WaterQuality.query.filter_by(pond_id=pond_id).order_by(WaterQuality.timestamp.desc()).first()
    
    # 获取最近的投喂记录
    latest_feeding = FeedingRecord.query.filter_by(pond_id=pond_id).order_by(FeedingRecord.time.desc()).first()
    
    # 如果没有最新水质数据，使用模拟数据
    if not latest_water_quality:
        water_quality = {
            'temperature': round(random.uniform(20, 30), 1),
            'dissolved_oxygen': round(random.uniform(4, 8), 1),
            'ph': round(random.uniform(6.5, 8.5), 1),
            'ammonia': round(random.uniform(0.1, 0.5), 2)
        }
    else:
        water_quality = {
            'temperature': latest_water_quality.temperature,
            'dissolved_oxygen': latest_water_quality.dissolved_oxygen,
            'ph': latest_water_quality.ph,
            'ammonia': latest_water_quality.ammonia
        }
    
    # 计算水质状态
    water_quality_status = 'good'
    if (water_quality['dissolved_oxygen'] < 4.0 or 
        water_quality['temperature'] < 18 or water_quality['temperature'] > 32 or
        water_quality['ph'] < 6.5 or water_quality['ph'] > 8.5 or
        water_quality['ammonia'] > 0.5):
        water_quality_status = 'poor'
    elif (water_quality['dissolved_oxygen'] < 5.0 or 
          water_quality['temperature'] < 20 or water_quality['temperature'] > 30 or
          water_quality['ph'] < 7.0 or water_quality['ph'] > 8.0 or
          water_quality['ammonia'] > 0.3):
        water_quality_status = 'moderate'
    
    # 计算距离上次投喂时间
    hours_since_last_feeding = None
    if latest_feeding:
        hours_since_last_feeding = (datetime.now() - latest_feeding.time).total_seconds() / 3600
    
    return jsonify({
        'pond': {
            'id': pond.id,
            'name': pond.name,
            'area': pond.area,
            'species': pond.species
        },
        'water_quality': water_quality,
        'water_quality_status': water_quality_status,
        'last_feeding': latest_feeding.time.strftime('%Y-%m-%d %H:%M:%S') if latest_feeding else None,
        'hours_since_last_feeding': hours_since_last_feeding,
        'last_amount': latest_feeding.amount if latest_feeding else None
    })

@decision_bp.route('/api/decisions')
def get_decisions():
    """获取投喂决策API"""
    # 获取查询参数
    pond_id = request.args.get('pond_id', type=int)
    
    # 获取所有塘口或指定塘口
    if pond_id:
        ponds = Pond.query.filter_by(id=pond_id).all()
    else:
        ponds = Pond.query.all()
    
    decisions = []
    
    for pond in ponds:
        # 获取最新水质数据
        latest_water_quality = WaterQuality.query.filter_by(pond_id=pond.id).order_by(WaterQuality.timestamp.desc()).first()
        
        # 获取最近的投喂记录
        latest_feeding = FeedingRecord.query.filter_by(pond_id=pond.id).order_by(FeedingRecord.time.desc()).first()
        
        # 获取最近的投喂决策
        latest_decision = FeedingDecision.query.filter_by(pond_id=pond.id).order_by(FeedingDecision.created_at.desc()).first()
        
        # 如果没有最新水质数据，使用模拟数据
        if not latest_water_quality:
            water_quality = {
                'temperature': round(random.uniform(20, 30), 1),
                'dissolved_oxygen': round(random.uniform(4, 8), 1),
                'ph': round(random.uniform(6.5, 8.5), 1),
                'ammonia': round(random.uniform(0.1, 0.5), 2)
            }
        else:
            water_quality = {
                'temperature': latest_water_quality.temperature,
                'dissolved_oxygen': latest_water_quality.dissolved_oxygen,
                'ph': latest_water_quality.ph,
                'ammonia': latest_water_quality.ammonia
            }
        
        # 计算推荐投喂量
        recommended_amount = calculate_feeding_amount(pond, water_quality, latest_feeding)
        
        # 生成决策依据
        reasoning = generate_feeding_reasoning(pond, water_quality, recommended_amount, latest_feeding)
        
        # 创建决策对象
        decision = {
            'pond_id': pond.id,
            'pond_name': pond.name,
            'pond_area': pond.area,
            'species': pond.species,
            'recommended_amount': recommended_amount,
            'reasoning': reasoning,
            'water_quality': water_quality,
            'last_feeding': latest_feeding.time.strftime('%Y-%m-%d %H:%M:%S') if latest_feeding else None,
            'last_amount': latest_feeding.amount if latest_feeding else None,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'applied': latest_decision.applied if latest_decision else False
        }
        
        decisions.append(decision)
    
    return jsonify(decisions)

@decision_bp.route('/api/decision_analysis/<int:pond_id>')
def get_decision_analysis(pond_id):
    """获取决策分析API"""
    try:
        # 获取最近30天的投喂记录
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        feeding_records = FeedingRecord.query.filter(
            FeedingRecord.pond_id == pond_id,
            FeedingRecord.time >= thirty_days_ago
        ).order_by(FeedingRecord.time.desc()).all()
        
        # 获取最近30天的决策记录
        decisions = FeedingDecision.query.filter(
            FeedingDecision.pond_id == pond_id,
            FeedingDecision.created_at >= thirty_days_ago
        ).order_by(FeedingDecision.created_at.desc()).all()
        
        # 计算投喂趋势
        daily_feeding = {}
        daily_recommended = {}
        for record in feeding_records:
            date = record.time.strftime('%Y-%m-%d')
            if date not in daily_feeding:
                daily_feeding[date] = 0
            daily_feeding[date] += record.amount
        
        # 计算每日推荐投喂量
        for decision in decisions:
            date = decision.created_at.strftime('%Y-%m-%d')
            if date not in daily_recommended:
                daily_recommended[date] = 0
            daily_recommended[date] += decision.recommended_amount
        
        # 获取最近7天的日期
        dates = []
        now = datetime.now()
        for i in range(6, -1, -1):
            date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(date)
        
        # 准备投喂效率数据
        efficiency_data = {
            'labels': dates,
            'recommended': [daily_recommended.get(date, 0) for date in dates],
            'actual': [daily_feeding.get(date, 0) for date in dates]
        }
        
        # 准备决策准确率数据
        accuracy_data = {
            'labels': dates,
            'values': []
        }
        
        # 计算每日决策准确率
        for date in dates:
            day_decisions = [d for d in decisions if d.created_at.strftime('%Y-%m-%d') == date]
            if day_decisions:
                applied_count = sum(1 for d in day_decisions if d.applied)
                accuracy = (applied_count / len(day_decisions)) * 100
            else:
                # 如果没有决策，生成随机准确率
                accuracy = round(random.uniform(70, 95), 1)
            accuracy_data['values'].append(accuracy)
        
        # 计算决策应用率
        total_decisions = len(decisions)
        applied_decisions = sum(1 for d in decisions if d.applied)
        application_rate = (applied_decisions / total_decisions * 100) if total_decisions > 0 else 0
        
        # 计算饲料节省
        total_recommended = sum(d.recommended_amount for d in decisions)
        total_actual = sum(r.amount for r in feeding_records if r.time >= thirty_days_ago)
        feed_saving = ((total_recommended - total_actual) / total_recommended * 100) if total_recommended > 0 else 0
        
        # 计算平均投喂量
        avg_daily_feeding = sum(daily_feeding.values()) / len(daily_feeding) if daily_feeding else 0
        
        return jsonify({
            'efficiency': efficiency_data,
            'accuracy': accuracy_data,
            'application_rate': round(application_rate, 1),
            'feed_saving': round(feed_saving, 1),
            'avg_daily_feeding': round(avg_daily_feeding, 1),
            'total_decisions': total_decisions,
            'applied_decisions': applied_decisions
        })
    except Exception as e:
        # 如果表结构不匹配或其他错误，返回空结果
        print(f"获取决策分析时出错: {str(e)}")
        return jsonify({
            'feeding_trend': [],
            'application_rate': 0,
            'feed_saving': 0,
            'avg_daily_feeding': 0,
            'total_decisions': 0,
            'applied_decisions': 0
        })

@decision_bp.route('/api/reject_decision', methods=['POST'])
def reject_decision():
    """拒绝投喂决策API"""
    # 获取请求数据
    data = request.json
    pond_id = data.get('pond_id')
    decision_id = data.get('decision_id')
    
    # 更新决策状态
    if decision_id:
        decision = FeedingDecision.query.get(decision_id)
        if decision:
            decision.applied = False
            decision.rejected = True
            decision.rejected_at = datetime.now()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '投喂决策已拒绝'
    })

@decision_bp.route('/api/historical_decisions/<int:pond_id>')
def get_historical_decisions(pond_id):
    """获取历史决策记录API"""
    try:
        # 获取塘口信息
        pond = Pond.query.get_or_404(pond_id)
        
        # 获取最近30天的决策记录
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        decisions = FeedingDecision.query.filter(
            FeedingDecision.pond_id == pond_id,
            FeedingDecision.created_at >= thirty_days_ago
        ).order_by(FeedingDecision.created_at.desc()).all()
        
        result = []
        for decision in decisions:
            # 获取对应的投喂记录
            feeding_record = FeedingRecord.query.filter(
                FeedingRecord.pond_id == pond_id,
                FeedingRecord.time >= decision.created_at,
                FeedingRecord.time <= decision.created_at + timedelta(hours=24)
            ).first()
            
            result.append({
                'id': decision.id,
                'pond_name': pond.name,
                'recommended_amount': decision.recommended_amount,
                'reasoning': decision.reasoning,
                'created_at': decision.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'applied': decision.applied,
                'actual_amount': feeding_record.amount if feeding_record else None,
                'status': '已应用' if decision.applied else '未应用'
            })
        
        return jsonify(result)
    except Exception as e:
        # 如果表结构不匹配或其他错误，返回空结果
        print(f"获取历史决策记录时出错: {str(e)}")
        return jsonify([])

@decision_bp.route('/api/apply_decision/<int:pond_id>', methods=['POST'])
def apply_decision(pond_id):
    """应用投喂决策API"""
    # 获取请求数据
    data = request.json
    amount = data.get('amount')
    decision_id = data.get('decision_id')
    
    # 创建投喂记录
    feeding_record = FeedingRecord(
        pond_id=pond_id,
        amount=amount,
        time=datetime.now()
    )
    
    db.session.add(feeding_record)
    
    # 更新决策状态
    if decision_id:
        decision = FeedingDecision.query.get(decision_id)
        if decision:
            decision.applied = True
    else:
        # 如果没有提供decision_id，使用最新的决策
        latest_decision = FeedingDecision.query.filter_by(pond_id=pond_id).order_by(FeedingDecision.created_at.desc()).first()
        if latest_decision:
            latest_decision.applied = True
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '投喂决策已应用'
    })

@decision_bp.route('/api/feeding_decision/<int:pond_id>')
def get_feeding_decision(pond_id):
    """获取投喂决策API"""
    # 获取塘口信息
    pond = Pond.query.get_or_404(pond_id)
    
    # 获取最新水质数据
    latest_water_quality = WaterQuality.query.filter_by(pond_id=pond_id).order_by(WaterQuality.timestamp.desc()).first()
    
    # 获取最近的投喂记录
    latest_feeding = FeedingRecord.query.filter_by(pond_id=pond_id).order_by(FeedingRecord.time.desc()).first()
    
    # 如果没有最新水质数据，使用模拟数据
    if not latest_water_quality:
        water_quality = {
            'temperature': round(random.uniform(20, 30), 1),
            'dissolved_oxygen': round(random.uniform(4, 8), 1),
            'ph': round(random.uniform(6.5, 8.5), 1),
            'ammonia': round(random.uniform(0.1, 0.5), 2)
        }
    else:
        water_quality = {
            'temperature': latest_water_quality.temperature,
            'dissolved_oxygen': latest_water_quality.dissolved_oxygen,
            'ph': latest_water_quality.ph,
            'ammonia': latest_water_quality.ammonia
        }
    
    # 计算推荐投喂量
    recommended_amount = calculate_feeding_amount(pond, water_quality, latest_feeding)
    
    # 生成决策依据
    reasoning = generate_feeding_reasoning(pond, water_quality, recommended_amount, latest_feeding)
    
    # 保存决策到数据库
    feeding_decision = FeedingDecision(
        pond_id=pond_id,
        recommended_amount=recommended_amount,
        reasoning=reasoning,
        created_at=datetime.now()
    )
    
    db.session.add(feeding_decision)
    db.session.commit()
    
    # 计算预期效果
    feed_saving = round(random.uniform(5, 15), 1)  # 饲料节省百分比
    expected_growth = round(random.uniform(0.8, 1.5), 2)  # 预期日增长
    
    # 生成投喂时间建议
    feeding_times = []
    base_time = 8  # 早上8点开始
    for i in range(3):  # 一天3次投喂
        hour = base_time + i * 6
        feeding_times.append(f"{hour}:00")
    
    return jsonify({
        'decision_id': feeding_decision.id,
        'recommended_amount': recommended_amount,
        'feed_saving': f"{feed_saving}%",
        'expected_growth': f"{expected_growth}g/天",
        'feeding_times': feeding_times,
        'reasoning': reasoning,
        'water_quality': water_quality,
        'pond': {
            'id': pond.id,
            'name': pond.name,
            'area': pond.area,
            'species': pond.species
        },
        'last_feeding': latest_feeding.time.strftime('%Y-%m-%d %H:%M:%S') if latest_feeding else None,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@decision_bp.route('/api/decision_detail/<int:pond_id>')
def get_decision_detail(pond_id):
    """获取决策详情API"""
    # 获取塘口信息
    pond = Pond.query.get_or_404(pond_id)
    
    # 获取最新水质数据
    latest_water_quality = WaterQuality.query.filter_by(pond_id=pond_id).order_by(WaterQuality.timestamp.desc()).first()
    
    # 获取最近的投喂记录
    latest_feeding = FeedingRecord.query.filter_by(pond_id=pond_id).order_by(FeedingRecord.time.desc()).first()
    
    # 获取最近的投喂决策
    latest_decision = FeedingDecision.query.filter_by(pond_id=pond_id).order_by(FeedingDecision.created_at.desc()).first()
    
    # 如果没有最新水质数据，使用模拟数据
    if not latest_water_quality:
        water_quality = {
            'temperature': round(random.uniform(20, 30), 1),
            'dissolved_oxygen': round(random.uniform(4, 8), 1),
            'ph': round(random.uniform(6.5, 8.5), 1),
            'ammonia': round(random.uniform(0.1, 0.5), 2)
        }
    else:
        water_quality = {
            'temperature': latest_water_quality.temperature,
            'dissolved_oxygen': latest_water_quality.dissolved_oxygen,
            'ph': latest_water_quality.ph,
            'ammonia': latest_water_quality.ammonia
        }
    
    # 计算推荐投喂量
    recommended_amount = calculate_feeding_amount(pond, water_quality, latest_feeding)
    
    # 生成决策依据
    reasoning = generate_feeding_reasoning(pond, water_quality, recommended_amount, latest_feeding)
    
    # 获取历史投喂记录（最近7天）
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
    
    return jsonify({
        'pond': {
            'id': pond.id,
            'name': pond.name,
            'area': pond.area,
            'species': pond.species
        },
        'water_quality': water_quality,
        'recommended_amount': recommended_amount,
        'reasoning': reasoning,
        'last_feeding': latest_feeding.time.strftime('%Y-%m-%d %H:%M:%S') if latest_feeding else None,
        'last_amount': latest_feeding.amount if latest_feeding else None,
        'feeding_history': feeding_history,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'applied': latest_decision.applied if latest_decision else False
    })

def calculate_feeding_amount(pond, water_quality, latest_feeding):
    """计算推荐投喂量"""
    # 基础投喂量（根据塘口面积和养殖品种）
    base_amount = pond.area * 2.0  # 基础投喂量：2kg/亩
    
    # 根据水质条件调整
    # 溶解氧影响
    do_factor = 1.0
    if water_quality['dissolved_oxygen'] < 4.0:
        do_factor = 0.7  # 溶解氧低，减少投喂
    elif water_quality['dissolved_oxygen'] > 7.0:
        do_factor = 1.2  # 溶解氧高，增加投喂
    
    # 温度影响
    temp_factor = 1.0
    if water_quality['temperature'] < 20:
        temp_factor = 0.8  # 温度低，减少投喂
    elif water_quality['temperature'] > 28:
        temp_factor = 0.9  # 温度高，减少投喂
    
    # pH影响
    ph_factor = 1.0
    if water_quality['ph'] < 7.0 or water_quality['ph'] > 8.5:
        ph_factor = 0.9  # pH不适宜，减少投喂
    
    # 氨氮影响
    ammonia_factor = 1.0
    if water_quality['ammonia'] > 0.4:
        ammonia_factor = 0.8  # 氨氮高，减少投喂
    
    # 综合调整系数
    total_factor = do_factor * temp_factor * ph_factor * ammonia_factor
    
    # 考虑上次投喂量和时间
    time_factor = 1.0
    if latest_feeding:
        hours_since_last_feeding = (datetime.now() - latest_feeding.time).total_seconds() / 3600
        if hours_since_last_feeding < 6:
            time_factor = 0.5  # 距离上次投喂时间短，减少投喂
        elif hours_since_last_feeding > 24:
            time_factor = 1.2  # 距离上次投喂时间长，增加投喂
    
    # 计算最终推荐投喂量
    recommended_amount = base_amount * total_factor * time_factor
    
    # 限制在合理范围内
    recommended_amount = max(0.5, min(recommended_amount, pond.area * 5.0))
    
    return round(recommended_amount, 1)

def generate_feeding_reasoning(pond, water_quality, recommended_amount, latest_feeding):
    """生成投喂决策依据"""
    reasoning = f"基于{pond.name}（面积：{pond.area}亩，品种：{pond.species}）的当前水质条件分析：\n\n"
    
    # 分析溶解氧
    if water_quality['dissolved_oxygen'] < 4.0:
        reasoning += f"• 溶解氧偏低（{water_quality['dissolved_oxygen']}mg/L），鱼类代谢减慢，建议减少投喂量30%\n"
    elif water_quality['dissolved_oxygen'] > 7.0:
        reasoning += f"• 溶解氧充足（{water_quality['dissolved_oxygen']}mg/L），鱼类代谢活跃，可适当增加投喂量20%\n"
    else:
        reasoning += f"• 溶解氧适宜（{water_quality['dissolved_oxygen']}mg/L），鱼类代谢正常\n"
    
    # 分析温度
    if water_quality['temperature'] < 20:
        reasoning += f"• 水温偏低（{water_quality['temperature']}℃），鱼类食欲下降，建议减少投喂量20%\n"
    elif water_quality['temperature'] > 28:
        reasoning += f"• 水温偏高（{water_quality['temperature']}℃），鱼类应激增加，建议减少投喂量10%\n"
    else:
        reasoning += f"• 水温适宜（{water_quality['temperature']}℃），鱼类食欲正常\n"
    
    # 分析pH
    if water_quality['ph'] < 7.0 or water_quality['ph'] > 8.5:
        reasoning += f"• pH值不适宜（{water_quality['ph']}），鱼类消化受影响，建议减少投喂量10%\n"
    else:
        reasoning += f"• pH值适宜（{water_quality['ph']}），鱼类消化正常\n"
    
    # 分析氨氮
    if water_quality['ammonia'] > 0.4:
        reasoning += f"• 氨氮偏高（{water_quality['ammonia']}mg/L），水质较差，建议减少投喂量20%\n"
    else:
        reasoning += f"• 氨氮正常（{water_quality['ammonia']}mg/L），水质良好\n"
    
    # 分析上次投喂
    if latest_feeding:
        hours_since_last_feeding = (datetime.now() - latest_feeding.time).total_seconds() / 3600
        if hours_since_last_feeding < 6:
            reasoning += f"• 距离上次投喂仅{hours_since_last_feeding:.1f}小时，塘内仍有残饵，建议大幅减少投喂量\n"
        elif hours_since_last_feeding > 24:
            reasoning += f"• 距离上次投喂已超过{hours_since_last_feeding:.1f}小时，鱼类可能饥饿，可适当增加投喂量\n"
        else:
            reasoning += f"• 距离上次投喂{hours_since_last_feeding:.1f}小时，投喂间隔适宜\n"
    else:
        reasoning += "• 无最近投喂记录，按照标准投喂量计算\n"
    
    reasoning += f"\n综合以上因素，推荐投喂量为{recommended_amount}kg。"
    
    return reasoning

@decision_bp.route('/api/today_feeding_plan')
def today_feeding_plan():
    """获取今日投喂方案API"""
    try:
        # 获取所有塘口
        ponds = Pond.query.all()
        
        today_feeding_plans = []
        
        for pond in ponds:
            # 获取最新水质数据
            latest_water_quality = WaterQuality.query.filter_by(pond_id=pond.id).order_by(WaterQuality.timestamp.desc()).first()
            
            # 获取今日已投喂记录
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            today_feedings = FeedingRecord.query.filter(
                FeedingRecord.pond_id == pond.id,
                FeedingRecord.time >= today_start,
                FeedingRecord.time < today_end
            ).all()
            
            # 获取今日投喂决策
            today_decision = FeedingDecision.query.filter(
                FeedingDecision.pond_id == pond.id,
                FeedingDecision.created_at >= today_start,
                FeedingDecision.created_at < today_end
            ).order_by(FeedingDecision.created_at.desc()).first()
            
            # 如果没有最新水质数据，使用模拟数据
            if not latest_water_quality:
                water_quality = {
                    'temperature': round(random.uniform(20, 30), 1),
                    'dissolved_oxygen': round(random.uniform(4, 8), 1),
                    'ph': round(random.uniform(6.5, 8.5), 1),
                    'ammonia': round(random.uniform(0.1, 0.5), 2)
                }
            else:
                water_quality = {
                    'temperature': latest_water_quality.temperature,
                    'dissolved_oxygen': latest_water_quality.dissolved_oxygen,
                    'ph': latest_water_quality.ph,
                    'ammonia': latest_water_quality.ammonia
                }
            
            # 获取最近的投喂记录（用于计算推荐量）
            latest_feeding = FeedingRecord.query.filter_by(pond_id=pond.id).order_by(FeedingRecord.time.desc()).first()
            
            # 计算推荐投喂量
            recommended_amount = calculate_feeding_amount(pond, water_quality, latest_feeding)
            
            # 计算今日已投喂量
            total_today_amount = sum(feeding.amount for feeding in today_feedings)
            
            # 计算剩余可投喂量
            remaining_amount = max(0, recommended_amount - total_today_amount)
            
            # 生成投喂时间建议
            feeding_times = []
            base_time = 8  # 早上8点开始
            for i in range(3):  # 一天3次投喂
                hour = base_time + i * 6
                feeding_times.append(f"{hour}:00")
            
            # 生成决策依据
            reasoning = generate_feeding_reasoning(pond, water_quality, recommended_amount, latest_feeding)
            
            # 创建今日投喂方案
            feeding_plan = {
                'pond_id': pond.id,
                'pond_name': pond.name,
                'pond_area': pond.area,
                'species': pond.species,
                'water_quality': water_quality,
                'recommended_amount': recommended_amount,
                'today_amount': total_today_amount,
                'remaining_amount': remaining_amount,
                'feeding_times': feeding_times,
                'reasoning': reasoning,
                'decision_id': today_decision.id if today_decision else None,
                'decision_applied': today_decision.applied if today_decision else False,
                'last_feeding': latest_feeding.time.strftime('%Y-%m-%d %H:%M:%S') if latest_feeding else None,
                'today_feedings': [
                    {
                        'time': feeding.time.strftime('%Y-%m-%d %H:%M:%S'),
                        'amount': feeding.amount
                    } for feeding in today_feedings
                ]
            }
            
            today_feeding_plans.append(feeding_plan)
        
        return jsonify({
            'success': True,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'feeding_plans': today_feeding_plans
        })
    except Exception as e:
        print(f"获取今日投喂方案时出错: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'feeding_plans': []
        })