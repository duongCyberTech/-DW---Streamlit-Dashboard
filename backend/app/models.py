from .extensions import db

class Retail(db.Model):
    __tablename__ = 'retail'

    invoice_no = db.Column(db.String(20), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    totalamount = db.Column(db.Numeric(12, 2), nullable=False)
    customer_id = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    payment_method = db.Column(db.String(20))
    invoice_date = db.Column(db.Date)
    day = db.Column(db.Integer)
    month = db.Column(db.Integer)
    quarter = db.Column(db.Integer)
    year = db.Column(db.Integer)
    category = db.Column(db.String(50))
    shopping_mall = db.Column(db.String(100))

    def __repr__(self):
        return f"<Retail {self.invoice_no}>"

    # ✅ Convert SQLAlchemy model to dict
    def to_dict(self):
        return {
            "invoice_no": self.invoice_no,
            "quantity": self.quantity,
            "price": float(self.price),
            "totalamount": float(self.totalamount),
            "customer_id": self.customer_id,
            "gender": self.gender,
            "age": self.age,
            "payment_method": self.payment_method,
            "invoice_date": self.invoice_date.isoformat() if self.invoice_date else None,
            "day": self.day,
            "month": self.month,
            "quarter": self.quarter,
            "year": self.year,
            "category": self.category,
            "shopping_mall": self.shopping_mall
        }

class Rfm(db.Model):
    __tablename__ = 'rfm'

    invoice_no = db.Column(db.String(20), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    totalamount = db.Column(db.Numeric(12, 2), nullable=False)
    customer_id = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    payment_method = db.Column(db.String(20))
    invoice_date = db.Column(db.Date)
    day = db.Column(db.Integer)
    month = db.Column(db.Integer)
    quarter = db.Column(db.Integer)
    year = db.Column(db.Integer)
    category = db.Column(db.String(50))
    shopping_mall = db.Column(db.String(100))
    recency = db.Column(db.Integer)
    freq = db.Column(db.Integer)
    monetary = db.Column(db.Numeric(10,2))

    def __repr__(self):
        return f"<Rfm {self.invoice_no}>"

    # ✅ Convert SQLAlchemy model to dict
    def to_dict(self):
        return {
            "invoice_no": self.invoice_no,
            "quantity": self.quantity,
            "price": float(self.price),
            "totalamount": float(self.totalamount),
            "customer_id": self.customer_id,
            "gender": self.gender,
            "age": self.age,
            "payment_method": self.payment_method,
            "invoice_date": self.invoice_date.isoformat() if self.invoice_date else None,
            "day": self.day,
            "month": self.month,
            "quarter": self.quarter,
            "year": self.year,
            "category": self.category,
            "shopping_mall": self.shopping_mall,
            "recency": self.recency,
            "freq": self.freq,
            "monetary": self.monetary
        }