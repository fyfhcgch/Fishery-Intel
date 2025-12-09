from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建一个SQLAlchemy实例，将在app.py中初始化
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    ponds = db.relationship('Pond', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Pond(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    area = db.Column(db.Float, nullable=False)  # 塑口面积（亩）
    species = db.Column(db.String(50), nullable=False)  # 养殖品种
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    water_qualities = db.relationship('WaterQuality', backref='pond', lazy=True)
    feeding_records = db.relationship('FeedingRecord', backref='pond', lazy=True)
    alerts = db.relationship('Alert', backref='pond', lazy=True)
    feeding_decisions = db.relationship('FeedingDecision', backref='pond', lazy=True)
    
    def __repr__(self):
        return f'<Pond {self.name}>'

class WaterQuality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('pond.id'), nullable=False, index=True)
    temperature = db.Column(db.Float, nullable=False)  # 温度（℃）
    turbidity = db.Column(db.Float, nullable=True)  # 浊度（NTU）
    conductivity = db.Column(db.Float, nullable=True)  # 电导率（μS/cm）
    water_level = db.Column(db.Float, nullable=True)  # 液位（m）
    ph = db.Column(db.Float, nullable=False)  # pH值
    dissolved_oxygen = db.Column(db.Float, nullable=False)  # 溶解氧（mg/L）
    cod = db.Column(db.Float, nullable=True)  # 化学需氧量（mg/L）
    ammonia = db.Column(db.Float, nullable=False)  # 氨氮（mg/L）
    heavy_metals = db.Column(db.Float, nullable=True)  # 重金属（μg/L）
    residual_chlorine = db.Column(db.Float, nullable=True)  # 余氯（mg/L）
    total_phosphorus = db.Column(db.Float, nullable=True)  # 总磷TP（mg/L）
    total_nitrogen = db.Column(db.Float, nullable=True)  # 总氮TN（mg/L）
    coliform = db.Column(db.Float, nullable=True)  # 总大肠菌群（个/L）
    algae = db.Column(db.Float, nullable=True)  # 藻类（个/mL）
    biotoxicity = db.Column(db.Float, nullable=True)  # 生物毒性（%）
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<WaterQuality {self.pond_id} at {self.timestamp}>'

class FeedingRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('pond.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)  # 投喂量（kg）
    time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<FeedingRecord {self.pond_id}: {self.amount}kg at {self.time}>'

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('pond.id'), nullable=False, index=True)
    level = db.Column(db.String(20), nullable=False)  # info, warning, danger
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    status = db.Column(db.String(20), default='active')  # active, resolved
    
    def __repr__(self):
        return f'<Alert {self.level}: {self.title}>'

class FeedingDecision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('pond.id'), nullable=False, index=True)
    recommended_amount = db.Column(db.Float, nullable=False)  # 推荐投喂量（kg）
    reasoning = db.Column(db.Text, nullable=False)  # 决策依据
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    applied = db.Column(db.Boolean, default=False)  # 是否已应用
    # rejected = db.Column(db.Boolean, default=False)  # 是否已拒绝
    # rejected_at = db.Column(db.DateTime, nullable=True)  # 拒绝时间
    
    def __repr__(self):
        return f'<FeedingDecision {self.pond_id}: {self.recommended_amount}kg>'