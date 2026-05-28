"""
Payment Routes — Payment Processing & History
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.payment import Fee, Payment
from utils.mobile_money import process_payment
from utils.email import EmailService
from utils.sms import send_sms_notification
from datetime import datetime
import uuid

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')


@payments_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    """Initiate a payment"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.get_json()
    
    # Validation
    required = ['amount', 'payment_method', 'phone_number']
    if not all(field in data for field in required):
        return jsonify({'message': 'Missing required fields'}), 400
    
    amount = float(data['amount'])
    payment_method = data['payment_method']
    phone_number = data['phone_number']
    
    if amount <= 0:
        return jsonify({'message': 'Invalid amount'}), 400
    
    if payment_method not in ['orange_money', 'africell_money', 'bank_transfer']:
        return jsonify({'message': 'Invalid payment method'}), 400
    
    try:
        # Generate transaction and reference numbers
        transaction_id = str(uuid.uuid4())
        reference_number = Payment.generate_reference()
        
        # Create payment record
        payment = Payment(
            student_id=user_id,
            transaction_id=transaction_id,
            reference_number=reference_number,
            amount=amount,
            payment_method=payment_method,
            phone_number=phone_number,
            status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # Process through payment gateway
        result = process_payment(payment_method, amount, phone_number, reference_number)
        
        if not result.get('success'):
            payment.status = 'failed'
            db.session.commit()
            return jsonify({'message': result.get('error', 'Payment processing failed')}), 400
        
        # Send confirmation SMS
        send_sms_notification(
            phone_number,
            'payment_confirmation',
            amount=int(amount),
            reference=reference_number
        )
        
        return jsonify({
            'message': 'Payment initiated',
            'transaction_id': transaction_id,
            'reference_number': reference_number,
            'status': 'pending',
            'next_step': 'Enter your PIN on your phone to complete payment'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@payments_bp.route('/verify/<transaction_id>', methods=['GET'])
@jwt_required()
def verify_payment(transaction_id):
    """Verify payment status"""
    user_id = get_jwt_identity()
    
    payment = Payment.query.filter_by(
        transaction_id=transaction_id,
        student_id=user_id
    ).first()
    
    if not payment:
        return jsonify({'message': 'Payment not found'}), 404
    
    # In real implementation, check with payment gateway
    # For demo, simulate verification
    
    return jsonify({
        'transaction_id': transaction_id,
        'status': payment.status,
        'amount': float(payment.amount),
        'reference': payment.reference_number,
        'created_at': payment.created_at.isoformat()
    }), 200


@payments_bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get student's payment history"""
    user_id = get_jwt_identity()
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status')  # Optional filter
    
    query = Payment.query.filter_by(student_id=user_id)
    
    if status:
        query = query.filter_by(status=status)
    
    paginated = query.order_by(Payment.created_at.desc()).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'payments': [p.to_dict() for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page
    }), 200


@payments_bp.route('/receipt/<transaction_id>', methods=['GET'])
@jwt_required()
def get_receipt(transaction_id):
    """Generate payment receipt"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    payment = Payment.query.filter_by(
        transaction_id=transaction_id,
        student_id=user_id
    ).first()
    
    if not payment:
        return jsonify({'message': 'Payment not found'}), 404
    
    if payment.status != 'completed':
        return jsonify({'message': 'Receipt only available for completed payments'}), 400
    
    # Generate PDF receipt (simplified)
    receipt_html = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2>Payment Receipt</h2>
            <p><strong>Reference:</strong> {payment.reference_number}</p>
            <p><strong>Student:</strong> {user.student_id}</p>
            <p><strong>Amount:</strong> SLL {payment.amount:,.0f}</p>
            <p><strong>Method:</strong> {payment.payment_method}</p>
            <p><strong>Date:</strong> {payment.created_at.strftime('%d %B %Y %H:%M')}</p>
            <p><strong>Status:</strong> {payment.status.upper()}</p>
            <p>Keep this receipt for your records.</p>
        </body>
    </html>
    """
    
    # In production, use ReportLab or similar to generate PDF
    return receipt_html, 200, {'Content-Type': 'text/html'}


@payments_bp.route('/send-reminder', methods=['POST'])
@jwt_required()
def send_payment_reminder():
    """Send payment reminder to student"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Get outstanding fees
    outstanding = Fee.get_outstanding_balance(user_id)
    
    if outstanding <= 0:
        return jsonify({'message': 'No outstanding fees'}), 400
    
    # Get next due date
    next_fee = Fee.query.filter_by(student_id=user_id).filter(
        Fee.status.in_(['pending', 'partial'])
    ).order_by(Fee.due_date.asc()).first()
    
    if next_fee:
        due_date = next_fee.due_date.strftime('%d %B %Y')
        result = send_sms_notification(
            user.phone,
            'payment_reminder',
            amount_due=int(outstanding),
            due_date=due_date
        )
        
        return jsonify({
            'message': 'Reminder sent',
            'outstanding': outstanding,
            'due_date': due_date
        }), 200
    
    return jsonify({'message': 'No outstanding fees'}), 200


@payments_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_payment_statistics():
    """Get payment statistics for student"""
    user_id = get_jwt_identity()
    
    payments = Payment.query.filter_by(student_id=user_id).all()
    completed = [p for p in payments if p.status == 'completed']
    failed = [p for p in payments if p.status == 'failed']
    
    total_paid = sum(float(p.amount) for p in completed)
    total_failed = sum(float(p.amount) for p in failed)
    
    # Payment method breakdown
    method_stats = {}
    for payment in completed:
        method = payment.payment_method
        if method not in method_stats:
            method_stats[method] = {'count': 0, 'total': 0}
        method_stats[method]['count'] += 1
        method_stats[method]['total'] += float(payment.amount)
    
    return jsonify({
        'total_transactions': len(payments),
        'completed': len(completed),
        'failed': len(failed),
        'pending': len([p for p in payments if p.status == 'pending']),
        'total_paid': total_paid,
        'total_failed': total_failed,
        'method_breakdown': method_stats,
        'average_transaction': total_paid / len(completed) if completed else 0
    }), 200


@payments_bp.route('/callback/orange', methods=['POST'])
def orange_money_callback():
    """Webhook for Orange Money payment confirmation"""
    data = request.get_json()
    
    reference_number = data.get('reference_number')
    status = data.get('status')
    
    payment = Payment.get_by_reference(reference_number)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    if status == 'completed':
        payment.status = 'completed'
        payment.processed_at = datetime.utcnow()
        
        # Update fee records
        outstanding = Fee.get_outstanding_balance(payment.student_id)
        if outstanding <= 0:
            # Find and mark fees as paid
            fees = Fee.get_student_fees(payment.student_id)
            for fee in fees:
                if fee.status != 'paid':
                    fee.amount_paid += payment.amount
                    if fee.amount_paid >= fee.amount_due:
                        fee.status = 'paid'
                        fee.amount_paid = fee.amount_due
        
        db.session.commit()
        
        # Send confirmation email
        user = User.query.get(payment.student_id)
        EmailService.send_payment_receipt(
            user.email,
            f"{user.first_name} {user.last_name}",
            float(payment.amount),
            reference_number,
            'Orange Money'
        )
    
    elif status == 'failed':
        payment.status = 'failed'
        db.session.commit()
        
        user = User.query.get(payment.student_id)
        send_sms_notification(
            user.phone,
            'payment_failed',
            reference=reference_number,
            reason='Payment declined'
        )
    
    return jsonify({'status': 'processed'}), 200


@payments_bp.route('/callback/africell', methods=['POST'])
def africell_money_callback():
    """Webhook for Africell Money payment confirmation"""
    # Similar to Orange Money callback
    return orange_money_callback()
