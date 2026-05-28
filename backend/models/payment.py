"""
Fee & Payment Models
"""
from datetime import datetime
from decimal import Decimal
from models.user import db

class Fee(db.Model):
    """Student fee record"""
    __tablename__ = 'fees'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Fee Details
    fee_category = db.Column(db.String(100), nullable=False)  # Tuition, Accommodation, Lab, etc.
    amount_due = db.Column(db.Numeric(15, 2), nullable=False)
    amount_paid = db.Column(db.Numeric(15, 2), default=0)
    
    # Dates
    academic_year = db.Column(db.String(9), nullable=False)  # 2024/2025
    semester = db.Column(db.Integer, nullable=False)  # 1 or 2
    due_date = db.Column(db.DateTime, nullable=False)
    
    # Status
    status = db.Column(
        db.String(20),
        default='pending',
        nullable=False
    )  # pending, partial, paid, overdue, waived
    
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Fee {self.fee_category} - {self.amount_due}>'
    
    @property
    def amount_outstanding(self):
        """Calculate outstanding amount"""
        return self.amount_due - self.amount_paid
    
    @property
    def is_overdue(self):
        """Check if fee is overdue"""
        return datetime.utcnow() > self.due_date and self.status != 'paid'
    
    @property
    def payment_percentage(self):
        """Calculate payment percentage"""
        if self.amount_due == 0:
            return 0
        return float((self.amount_paid / self.amount_due) * 100)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'fee_category': self.fee_category,
            'amount_due': float(self.amount_due),
            'amount_paid': float(self.amount_paid),
            'amount_outstanding': float(self.amount_outstanding),
            'academic_year': self.academic_year,
            'semester': self.semester,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'payment_percentage': self.payment_percentage,
            'is_overdue': self.is_overdue,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def get_student_fees(student_id):
        """Get all fees for a student"""
        return Fee.query.filter_by(student_id=student_id).all()
    
    @staticmethod
    def get_outstanding_balance(student_id):
        """Calculate total outstanding balance for student"""
        fees = Fee.query.filter_by(student_id=student_id).all()
        return sum(fee.amount_outstanding for fee in fees)


class Payment(db.Model):
    """Payment transaction record"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Transaction Details
    transaction_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    reference_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Payment Method
    payment_method = db.Column(
        db.String(20),
        nullable=False
    )  # orange_money, africell_money, bank_transfer
    phone_number = db.Column(db.String(20), nullable=True)
    
    # Status
    status = db.Column(
        db.String(20),
        default='pending',
        nullable=False
    )  # pending, processing, completed, failed, refunded
    
    # Reconciliation
    reconciled = db.Column(db.Boolean, default=False)
    reconciled_by = db.Column(db.String(100), nullable=True)
    reconciled_at = db.Column(db.DateTime, nullable=True)
    
    # Receipt
    receipt_url = db.Column(db.String(255), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<Payment {self.reference_number} - {self.amount}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'transaction_id': self.transaction_id,
            'reference_number': self.reference_number,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'phone_number': self.phone_number,
            'status': self.status,
            'reconciled': self.reconciled,
            'receipt_url': self.receipt_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }
    
    @staticmethod
    def generate_reference():
        """Generate unique reference number"""
        import uuid
        return f"TXN-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    
    @staticmethod
    def get_student_payments(student_id, limit=10):
        """Get recent payments for a student"""
        return Payment.query.filter_by(student_id=student_id)\
            .order_by(Payment.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_by_reference(reference_number):
        """Get payment by reference number"""
        return Payment.query.filter_by(reference_number=reference_number).first()
    
    @staticmethod
    def get_by_transaction_id(transaction_id):
        """Get payment by transaction ID"""
        return Payment.query.filter_by(transaction_id=transaction_id).first()
    
    @staticmethod
    def get_pending_payments(limit=50):
        """Get all pending payments"""
        return Payment.query.filter_by(status='pending')\
            .order_by(Payment.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_payment_summary(academic_year=None):
        """Get payment summary statistics"""
        query = Payment.query.filter_by(status='completed')
        
        if academic_year:
            # Filter by academic year if provided
            start_date = datetime.strptime(f"{academic_year.split('/')[0]}-09-01", "%Y-%m-%d")
            end_date = datetime.strptime(f"{academic_year.split('/')[1]}-08-31", "%Y-%m-%d")
            query = query.filter(Payment.created_at.between(start_date, end_date))
        
        payments = query.all()
        total = sum(float(p.amount) for p in payments)
        count = len(payments)
        
        return {
            'total_collected': total,
            'transaction_count': count,
            'average_transaction': total / count if count > 0 else 0
        }
