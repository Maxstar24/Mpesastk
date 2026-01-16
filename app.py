import os
import json
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration file path
CONFIG_FILE = 'config.json'


@app.context_processor
def inject_now():
    """Inject current datetime into all templates"""
    return {'now': datetime.now()}


def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'consumer_key': '',
        'consumer_secret': '',
        'business_shortcode': '',
        'passkey': '',
        'callback_url': '',
        'environment': 'sandbox'
    }


def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


def get_access_token(consumer_key, consumer_secret, environment='sandbox'):
    """Get M-Pesa access token"""
    base_url = 'https://sandbox.safaricom.co.ke' if environment == 'sandbox' else 'https://api.safaricom.co.ke'
    api_url = f'{base_url}/oauth/v1/generate?grant_type=client_credentials'
    
    try:
        response = requests.get(api_url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        return None


def generate_password(business_shortcode, passkey, timestamp):
    """Generate password for STK push"""
    data_to_encode = business_shortcode + passkey + timestamp
    encoded = base64.b64encode(data_to_encode.encode())
    return encoded.decode('utf-8')


@app.route('/')
def index():
    """Main page for initiating STK push"""
    config = load_config()
    is_configured = all(config.values())
    return render_template('index.html', is_configured=is_configured)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Settings page for managing credentials"""
    if request.method == 'POST':
        config = {
            'consumer_key': request.form.get('consumer_key', '').strip(),
            'consumer_secret': request.form.get('consumer_secret', '').strip(),
            'business_shortcode': request.form.get('business_shortcode', '').strip(),
            'passkey': request.form.get('passkey', '').strip(),
            'callback_url': request.form.get('callback_url', '').strip(),
            'environment': request.form.get('environment', 'sandbox').strip()
        }
        
        # Validate that required fields are filled
        required_fields = ['consumer_key', 'consumer_secret', 'business_shortcode', 'passkey', 'callback_url']
        if all(config.get(field) for field in required_fields):
            save_config(config)
            flash('Settings saved successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('All required fields must be filled!', 'error')
    
    config = load_config()
    return render_template('settings.html', config=config)


@app.route('/stk-push', methods=['POST'])
def stk_push():
    """Initiate STK push"""
    config = load_config()
    
    # Validate configuration
    if not all(config.values()):
        return jsonify({
            'success': False,
            'message': 'Please configure your M-Pesa credentials in settings first'
        }), 400
    
    # Get form data
    phone_number = request.form.get('phone_number', '').strip()
    amount = request.form.get('amount', '').strip()
    account_reference = request.form.get('account_reference', 'Payment').strip()
    transaction_desc = request.form.get('transaction_desc', 'Payment').strip()
    
    # Validate input
    if not phone_number or not amount:
        return jsonify({
            'success': False,
            'message': 'Phone number and amount are required'
        }), 400
    
    # Format phone number (remove + and spaces, ensure it starts with 254)
    phone_number = phone_number.replace('+', '').replace(' ', '')
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif not phone_number.startswith('254'):
        phone_number = '254' + phone_number
    
    try:
        # Get environment setting
        environment = config.get('environment', 'sandbox')
        
        # Get access token
        access_token = get_access_token(config['consumer_key'], config['consumer_secret'], environment)
        if not access_token:
            return jsonify({
                'success': False,
                'message': 'Failed to get access token. Please check your credentials.'
            }), 400
        
        # Generate timestamp and password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = generate_password(config['business_shortcode'], config['passkey'], timestamp)
        
        # Prepare STK push request
        base_url = 'https://sandbox.safaricom.co.ke' if environment == 'sandbox' else 'https://api.safaricom.co.ke'
        api_url = f'{base_url}/mpesa/stkpush/v1/processrequest'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': config['business_shortcode'],
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': config['business_shortcode'],
            'PhoneNumber': phone_number,
            'CallBackURL': config['callback_url'],
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        
        # Make the request
        response = requests.post(api_url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('ResponseCode') == '0':
            return jsonify({
                'success': True,
                'message': 'STK push sent successfully! Please check your phone.',
                'data': {
                    'merchant_request_id': response_data.get('MerchantRequestID'),
                    'checkout_request_id': response_data.get('CheckoutRequestID'),
                    'response_code': response_data.get('ResponseCode'),
                    'response_description': response_data.get('ResponseDescription'),
                    'customer_message': response_data.get('CustomerMessage')
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': response_data.get('errorMessage', 'Failed to initiate STK push'),
                'data': response_data
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
