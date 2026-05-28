"""
Admin Routes — Finance Staff Management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, AdminUser, db
from models.payment import Fee, Payment
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    """Get admin dashboard statistics"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get statistics
    total_students = User.query.count()
    total_fees = Fee.query.count()
    total_payments = Payment.query.count()
    
    completed_payments = Payment.query.filter_by(status='completed').all()
    total_revenue = sum(float(p.amount) for p in completed_payments)
    
    outstanding_fees = Fee.query.filter(Fee.status.in_(['pending', 'partial', 'overdue'])).all()
    total_outstanding = sum(float(f.amount_outstanding) for f in outstanding_fees)
    
    return jsonify({
        'stats': {
            'total_students': total_students,
            'total_fees': total_fees,
            'total_payments': total_payments,
            'total_revenue': total_revenue,
            'total_outstanding': total_outstanding,
            'collection_rate': (total_revenue / (total_revenue + total_outstanding) * 100) if (total_revenue + total_outstanding) > 0 else 0
        }
    }), 200


@admin_bp.route('/students', methods=['GET'])
@jwt_required()
def list_students():
    """List all students with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    faculty = request.args.get('faculty')
    search = request.args.get('search')
    
    query = User.query
    
    if faculty:
        query = query.filter_by(faculty=faculty)
    
    if search:
        query = query.filter(
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%')) |
            (User.student_id.ilike(f'%{search}%'))
        )
    
    paginated = query.paginate(page=page, per_page=per_page)
    
    students = []
    for user in paginated.items:
        outstanding = Fee.get_outstanding_balance(user.id)
        students.append({
            **user.to_dict(),
            'outstanding_balance': outstanding
        })
    
    return jsonify({
        'students': students,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200


@admin_bp.route('/student/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student_detail(student_id):
    """Get detailed student information"""
    user = User.query.get(student_id)
    
    if not user:
        return jsonify({'message': 'Student not found'}), 404
    
    # Get fees and payments
    fees = Fee.get_student_fees(student_id)
    payments = Payment.get_student_payments(student_id, limit=20)
    outstanding = Fee.get_outstanding_balance(student_id)
    
    return jsonify({
        'student': user.to_dict(),
        'outstanding_balance': outstanding,
        'fees': [f.to_dict() for f in fees],
        'payments': [p.to_dict() for p in payments]
    }), 200


@admin_bp.route('/payments', methods=['GET'])
@jwt_required()
def list_payments():
    """List all payments with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    method = request.args.get('method')
    
    query = Payment.query
    
    if status:
        query = query.filter_by(status=status)
    if method:
        query = query.filter_by(payment_method=method)
    
    paginated = query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=per_page)
    
    payments = []
    for payment in paginated.items:
        user = User.query.get(payment.student_id)
        payments.append({
            **payment.to_dict(),
            'student_name': f"{user.first_name} {user.last_name}" if user else 'Unknown'
        })
    
    return jsonify({
        'payments': payments,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200


@admin_bp.route('/payment/<int:payment_id>/reconcile', methods=['POST'])
@jwt_required()
def reconcile_payment(payment_id):
    """Mark payment as reconciled"""
    user_id = get_jwt_identity()
    admin = AdminUser.query.get(user_id)
    
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return jsonify({'message': 'Payment not found'}), 404
    
    payment.reconciled = True
    payment.reconciled_by = admin.username if admin else 'unknown'
    payment.reconciled_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'message': 'Payment reconciled',
        'payment': payment.to_dict()
    }), 200


@admin_bp.route('/fees', methods=['GET'])
@jwt_required()
def list_fees():
    """List all fees with filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    academic_year = request.args.get('academic_year')
    
    query = Fee.query
    
    if status:
        query = query.filter_by(status=status)
    if academic_year:
        query = query.filter_by(academic_year=academic_year)
    
    paginated = query.order_by(Fee.due_date.desc()).paginate(page=page, per_page=per_page)
    
    fees = []
    for fee in paginated.items:
        user = User.query.get(fee.student_id)
        fees.append({
            **fee.to_dict(),
            'student_name': f"{user.first_name} {user.last_name}" if user else 'Unknown'
        })
    
    return jsonify({
        'fees': fees,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200


@admin_bp.route('/fee/<int:fee_id>', methods=['PUT'])
@jwt_required()
def update_fee(fee_id):
    """Update fee record"""
    fee = Fee.query.get(fee_id)
    
    if not fee:
        return jsonify({'message': 'Fee not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'amount_paid' in data:
        fee.amount_paid = float(data['amount_paid'])
    
    if 'status' in data:
        fee.status = data['status']
    
    if 'notes' in data:
        fee.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Fee updated',
        'fee': fee.to_dict()
    }), 200


@admin_bp.route('/reports/collection', methods=['GET'])
@jwt_required()
def collection_report():
    """Generate collection report"""
    academic_year = request.args.get('academic_year', '2024/2025')
    
    # Get summary
    summary = Payment.get_payment_summary(academic_year)
    
    # Get by faculty
    students = User.query.all()
    faculty_stats = {}
    
    for student in students:
        if student.faculty not in faculty_stats:
            faculty_stats[student.faculty] = {
                'total': 0,
                'collected': 0,
                'students': 0
            }
        
        payments = Payment.query.filter_by(student_id=student.id, status='completed').all()
        faculty_stats[student.faculty]['collected'] += sum(float(p.amount) for p in payments)
        faculty_stats[student.faculty]['students'] += 1
    
    return jsonify({
        'academic_year': academic_year,
        'summary': summary,
        'by_faculty': faculty_stats
    }), 200


@admin_bp.route('/reports/outstanding', methods=['GET'])
@jwt_required()
def outstanding_report():
    """Generate outstanding fees report"""
    fees = Fee.query.filter(Fee.status.in_(['pending', 'partial', 'overdue'])).all()
    
    outstanding = []
    for fee in fees:
        user = User.query.get(fee.student_id)
        outstanding.append({
            'student_id': user.student_id,
            'student_name': f"{user.first_name} {user.last_name}",
            'faculty': user.faculty,
            'fee_category': fee.fee_category,
            'amount_due': float(fee.amount_due),
            'amount_paid': float(fee.amount_paid),
            'outstanding': float(fee.amount_outstanding),
            'due_date': fee.due_date.isoformat(),
            'days_overdue': (datetime.utcnow() - fee.due_date).days if fee.is_overdue else 0
        })
    
    return jsonify({
        'total_outstanding': sum(o['outstanding'] for o in outstanding),
        'records': outstanding
    }), 200


@admin_bp.route('/send-reminder', methods=['POST'])
@jwt_required()
def send_bulk_reminder():
    """Send fee reminder to students with outstanding balances"""
    data = request.get_json()
    
    min_outstanding = data.get('min_outstanding', 0)
    
    # Find students with outstanding fees
    fees = Fee.query.filter(
        (Fee.status.in_(['pending', 'partial', 'overdue'])) &
        (Fee.amount_outstanding > min_outstanding)
    ).all()
    
    reminded_count = 0
    
    for fee in fees:
        user = User.query.get(fee.student_id)
        if user and user.phone:
            from utils.sms import send_sms_notification
            result = send_sms_notification(
                user.phone,
                'payment_reminder',
                amount_due=int(fee.amount_outstanding),
                due_date=fee.due_date.strftime('%d %B %Y')
            )
            if result.get('success'):
                reminded_count += 1
    
    return jsonify({
        'message': f'Reminders sent to {reminded_count} students',
        'count': reminded_count
    }), 200


@admin_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    """Get system settings"""
    # This would be stored in database
    settings = {
        'academic_year': '2024/2025',
        'current_semester': 1,
        'payment_deadline': '2025-03-31',
        'sms_notifications_enabled': True,
        'email_notifications_enabled': True
    }
    return jsonify(settings), 200


@admin_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    """Update system settings"""
    data = request.get_json()
    
    # Validate and update settings
    # In production, store in database
    
    return jsonify({
        'message': 'Settings updated',
        'settings': data
    }), 200
