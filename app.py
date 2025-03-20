from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coupons.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Coupon Model
class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)  # "Percentage", "Fixed", "Free Delivery"
    discount_value = db.Column(db.Integer, nullable=False)
    min_order_value = db.Column(db.Integer, nullable=False, default=0)
    expiry_date = db.Column(db.Date, nullable=False)
    max_uses = db.Column(db.Integer, default=1)
    used_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(10), default="Active")

with app.app_context():
    db.create_all()

# Fetch Active Coupons
@app.route('/coupons', methods=['GET'])
def get_coupons():
    active_coupons = Coupon.query.filter(Coupon.status == "Active").all()
    return jsonify([{
        "code": c.code,
        "discount_type": c.discount_type,
        "discount_value": c.discount_value,
        "min_order_value": c.min_order_value,
        "expiry_date": c.expiry_date.strftime('%Y-%m-%d'),
        "max_uses": c.max_uses,
        "used_count": c.used_count
    } for c in active_coupons])

# Validate Coupon Code
@app.route('/validate-coupon', methods=['POST'])
def validate_coupon():
    data = request.json
    coupon = Coupon.query.filter_by(code=data['code']).first()

    if not coupon:
        return jsonify({"success": False, "message": "Invalid coupon code"})

    if coupon.status != "Active":
        return jsonify({"success": False, "message": "Coupon is expired or inactive"})

    if coupon.used_count >= coupon.max_uses:
        return jsonify({"success": False, "message": "Coupon usage limit reached"})

    return jsonify({"success": True, "message": "Coupon is valid", "discount": coupon.discount_value})

if __name__ == '__main__':
    app.run(debug=True)
