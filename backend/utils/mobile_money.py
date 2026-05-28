"""
Mobile Money Integration — Orange Money & Africell Money
"""
import requests
import json
from datetime import datetime
from flask import current_app
import hashlib
import hmac

class OrangeMoneyGateway:
    """Orange Money payment gateway"""
    
    API_URL = "https://api.orange.com/payment"
    
    def __init__(self):
        self.api_key = current_app.config.get('ORANGE_MONEY_API')
        self.api_secret = current_app.config.get('ORANGE_MONEY_SECRET')
    
    def initiate_payment(self, amount, phone, reference):
        """Initiate Orange Money payment"""
        try:
            payload = {
                'amount': amount,
                'phone': self._format_phone(phone),
                'reference': reference,
                'description': 'Njala University Fee Payment',
                'callback_url': 'https://njala-fees.edu.sl/api/payments/callback/orange'
            }
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(f"{self.API_URL}/initiate", json=payload, headers=headers, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'transaction_id': data.get('transaction_id'),
                    'status': 'pending'
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Payment initiation failed')
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, transaction_id):
        """Verify Orange Money payment status"""
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            response = requests.get(f"{self.API_URL}/verify/{transaction_id}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'status': data.get('status'),
                    'amount': data.get('amount'),
                    'timestamp': data.get('timestamp')
                }
            else:
                return {'success': False, 'error': 'Verification failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def _format_phone(phone):
        """Format phone number for Orange Money"""
        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        if phone.startswith('232'):
            return phone
        elif phone.startswith('76') or phone.startswith('78') or phone.startswith('79'):
            return f'232{phone}'
        else:
            return f'232{phone}'


class AfricellMoneyGateway:
    """Africell Money payment gateway"""
    
    API_URL = "https://api.africell.sl/payment"
    
    def __init__(self):
        self.api_key = current_app.config.get('AFRICELL_MONEY_API')
        self.api_secret = current_app.config.get('AFRICELL_MONEY_SECRET')
    
    def initiate_payment(self, amount, phone, reference):
        """Initiate Africell Money payment"""
        try:
            payload = {
                'amount': amount,
                'msisdn': self._format_phone(phone),
                'merchant_ref': reference,
                'merchant_id': self.api_key,
                'description': 'Njala University Fees',
                'callback': 'https://njala-fees.edu.sl/api/payments/callback/africell'
            }
            
            signature = self._generate_signature(payload)
            headers = {
                'X-Signature': signature,
                'Content-Type': 'application/json'
            }
            
            response = requests.post(f"{self.API_URL}/request", json=payload, headers=headers, timeout=10)
            data = response.json()
            
            if response.status_code == 200 and data.get('success'):
                return {
                    'success': True,
                    'transaction_id': data.get('transaction_id'),
                    'status': 'pending'
                }
            else:
                return {
                    'success': False,
                    'error': data.get('message', 'Payment initiation failed')
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_payment(self, transaction_id):
        """Verify Africell Money payment"""
        try:
            params = {
                'transaction_id': transaction_id,
                'merchant_id': self.api_key
            }
            
            signature = self._generate_signature(params)
            headers = {'X-Signature': signature}
            
            response = requests.get(f"{self.API_URL}/status", params=params, headers=headers, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'status': data.get('status'),
                    'amount': data.get('amount')
                }
            else:
                return {'success': False, 'error': 'Verification failed'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_signature(self, payload):
        """Generate HMAC signature for request"""
        message = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def _format_phone(phone):
        """Format phone for Africell Money"""
        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        if phone.startswith('232'):
            return phone[3:]  # Remove country code for Africell
        else:
            return phone


class BankTransferGateway:
    """Bank transfer / Direct bank payment"""
    
    BANK_DETAILS = {
        'bank_name': 'Sierra Leone Commercial Bank',
        'account_name': 'Njala University Finance',
        'account_number': '1234567890',
        'swift_code': 'SLCBSLDL'
    }
    
    @staticmethod
    def get_bank_details():
        """Get bank details for manual transfer"""
        return BankTransferGateway.BANK_DETAILS
    
    @staticmethod
    def initiate_payment(amount, reference):
        """Initiate bank transfer (creates pending record)"""
        return {
            'success': True,
            'transaction_id': reference,
            'bank_details': BankTransferGateway.BANK_DETAILS,
            'instructions': 'Please use the reference number in the description field of your transfer',
            'status': 'pending_bank_confirmation'
        }


class PaymentGatewayFactory:
    """Factory for creating payment gateway instances"""
    
    GATEWAYS = {
        'orange_money': OrangeMoneyGateway,
        'africell_money': AfricellMoneyGateway,
        'bank_transfer': BankTransferGateway
    }
    
    @staticmethod
    def get_gateway(payment_method):
        """Get payment gateway instance"""
        GatewayClass = PaymentGatewayFactory.GATEWAYS.get(payment_method)
        if not GatewayClass:
            raise ValueError(f"Unknown payment method: {payment_method}")
        return GatewayClass()


def process_payment(payment_method, amount, phone, reference):
    """Process payment through appropriate gateway"""
    try:
        gateway = PaymentGatewayFactory.get_gateway(payment_method)
        
        if payment_method == 'bank_transfer':
            return gateway.initiate_payment(amount, reference)
        else:
            return gateway.initiate_payment(amount, phone, reference)
    except Exception as e:
        return {'success': False, 'error': str(e)}
