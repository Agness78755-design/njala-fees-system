"""
Fees Routes — Fee Management & Display
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models.user import User
from backend.models.payment import Fee, Payment

fees_bp = Blueprint('fees', __name__, url_prefix='/api/fees')


@fees_bp.route('/balance', methods=['GET'])
@jwt_required()
def get_fee_balance():
    """Get student's fee balance"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get all fees for student
    fees = Fee.get_student_fees(user_id)
    
    total_due = sum(float(f.amount_due) for f in fees)
    total_paid = sum(float(f.amount_paid) for f in fees)
    outstanding = total_due - total_paid
    
    fees_list = [f.to_dict() for f in fees]
    
    return jsonify({
        'student_id': user.student_id,
        'total_due': total_due,
        'total_paid': total_paid,
        'outstanding': outstanding,
        'paid_percentage': (total_paid / total_due * 100) if total_due > 0 else 0,
        'fees': fees_list
    }), 200


@fees_bp.route('/list', methods=['GET'])
@jwt_required()
def list_fees():
    """List all fees for student with pagination"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    fees_query = Fee.query.filter_by(student_id=user_id).order_by(Fee.due_date.desc())
    paginated = fees_query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'fees': [f.to_dict() for f in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200


@fees_bp.route('/<int:fee_id>', methods=['GET'])
@jwt_required()
def get_fee_detail(fee_id):
    """Get detailed fee information"""
    user_id = get_jwt_identity()
    
    fee = Fee.query.get(fee_id)
    
    if not fee:
        return jsonify({'message': 'Fee not found'}), 404
    
    if fee.student_id != user_id:
        return jsonify({'message': 'Unauthorized access'}), 403
    
    return jsonify(fee.to_dict()), 200


@fees_bp.route('/by-semester/<academic_year>/<int:semester>', methods=['GET'])
@jwt_required()
def get_semester_fees(academic_year, semester):
    """Get fees for specific semester"""
    user_id = get_jwt_identity()
    
    fees = Fee.query.filter_by(
        student_id=user_id,
        academic_year=academic_year,
        semester=semester
    ).all()
    
    if not fees:
        return jsonify({'fees': [], 'message': 'No fees found for this semester'}), 200
    
    total_due = sum(float(f.amount_due) for f in fees)
    total_paid = sum(float(f.amount_paid) for f in fees)
    
    return jsonify({
        'academic_year': academic_year,
        'semester': semester,
        'fees': [f.to_dict() for f in fees],
        'total_due': total_due,
        'total_paid': total_paid,
        'outstanding': total_due - total_paid
    }), 200


@fees_bp.route('/breakdown', methods=['GET'])
@jwt_required()
def get_fee_breakdown():
    """Get detailed fee breakdown by category"""
    user_id = get_jwt_identity()
    
    fees = Fee.get_student_fees(user_id)
    
    # Group by category
    breakdown = {}
    for fee in fees:
        category = fee.fee_category
        if category not in breakdown:
            breakdown[category] = {
                'total_due': 0,
                'total_paid': 0,
                'count': 0
            }
        
        breakdown[category]['total_due'] += float(fee.amount_due)
        breakdown[category]['total_paid'] += float(fee.amount_paid)
        breakdown[category]['count'] += 1
    
    # Format response
    categories = []
    for category, data in breakdown.items():
        categories.append({
            'category': category,
            'total_due': data['total_due'],
            'total_paid': data['total_paid'],
            'outstanding': data['total_due'] - data['total_paid'],
            'payment_percentage': (data['total_paid'] / data['total_due'] * 100) if data['total_due'] > 0 else 0,
            'fee_count': data['count']
        })
    
    return jsonify({'breakdown': categories}), 200


@fees_bp.route('/payment-schedule', methods=['GET'])
@jwt_required()
def get_payment_schedule():
    """Get upcoming payment schedule"""
    user_id = get_jwt_identity()
    
    fees = Fee.query.filter_by(student_id=user_id).filter(
        Fee.status.in_(['pending', 'partial', 'overdue'])
    ).order_by(Fee.due_date.asc()).all()
    
    schedule = []
    for fee in fees:
        schedule.append({
            'fee_id': fee.id,
            'category': fee.fee_category,
            'amount': float(fee.amount_outstanding),
            'due_date': fee.due_date.isoformat(),
            'status': fee.status,
            'is_overdue': fee.is_overdue
        })
    
    return jsonify({
        'upcoming_payments': schedule,
        'total_outstanding': sum(f['amount'] for f in schedule)
    }), 200


@fees_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_fee_summary():
    """Get complete fee summary for student"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    fees = Fee.get_student_fees(user_id)
    payments = Payment.get_student_payments(user_id, limit=5)
    
    total_due = sum(float(f.amount_due) for f in fees)
    total_paid = sum(float(f.amount_paid) for f in fees)
    outstanding = total_due - total_paid
    
    # Count by status
    status_counts = {}
    for fee in fees:
        status = fee.status
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return jsonify({
        'student': {
            'id': user.student_id,
            'name': f"{user.first_name} {user.last_name}",
            'faculty': user.faculty,
            'level': user.level
        },
        'finances': {
            'total_due': total_due,
            'total_paid': total_paid,
            'outstanding': outstanding,
            'paid_percentage': (total_paid / total_due * 100) if total_due > 0 else 0
        },
        'status_summary': status_counts,
        'recent_payments': [p.to_dict() for p in payments],
        'fee_count': len(fees)
    }), 200


@fees_bp.route('/export', methods=['GET'])
@jwt_required()
def export_fees():
    """Export fee data as CSV/JSON"""
    user_id = get_jwt_identity()
    format_type = request.args.get('format', 'json')  # json or csv
    
    fees = Fee.get_student_fees(user_id)
    
    if format_type == 'json':
        return jsonify({
            'fees': [f.to_dict() for f in fees]
        }), 200
    
    elif format_type == 'csv':
        import io
        import csv
        
        si = io.StringIO()
        writer = csv.writer(si)
        writer.writerow(['Category', 'Amount Due', 'Amount Paid', 'Outstanding', 'Status', 'Due Date'])
        
        for fee in fees:
            writer.writerow([
                fee.fee_category,
                float(fee.amount_due),
                float(fee.amount_paid),
                float(fee.amount_outstanding),
                fee.status,
                fee.due_date.strftime('%Y-%m-%d')
            ])
        
        output = io.BytesIO()
        output.write(si.getvalue().encode('utf-8'))
        output.seek(0)
        
        return output.getvalue(), 200, {
            'Content-Disposition': 'attachment; filename=fees.csv',
            'Content-Type': 'text/csv'
        }
    
    else:
        return jsonify({'message': 'Invalid format'}), 400
