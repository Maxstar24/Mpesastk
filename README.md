# M-Pesa STK Push Application

A Flask-based web application for initiating M-Pesa STK push payments. This application provides a simple interface for sending payment requests to mobile phone numbers using Safaricom's M-Pesa Daraja API.

## Features

- 🚀 Easy-to-use web interface for initiating STK push payments
- ⚙️ Settings page for managing M-Pesa API credentials
- 🔒 Secure credential storage
- 📱 Phone number validation and formatting
- ✅ Real-time payment status feedback
- 🎨 Modern, responsive UI design

## Prerequisites

- Python 3.7 or higher
- M-Pesa Daraja API credentials (Consumer Key, Consumer Secret, Business Shortcode, Passkey)
- A valid callback URL (can use ngrok for local testing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Maxstar24/Mpesastk.git
cd Mpesastk
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Create a `.env` file for environment variables:
```bash
cp .env.example .env
# Edit .env with your preferred secret key
```

## Getting M-Pesa Credentials

1. Visit the [Safaricom Daraja Portal](https://developer.safaricom.co.ke)
2. Create an account or log in
3. Create a new app and select "Lipa Na M-Pesa Online"
4. Note down your Consumer Key and Consumer Secret
5. For sandbox testing, use the test credentials provided
6. Get your Business Shortcode and Passkey from the portal

## Configuration

### Option 1: Using the Web Interface (Recommended)

1. Start the application (see Usage section below)
2. Navigate to the Settings page
3. Enter your M-Pesa credentials
4. Click "Save Settings"

### Option 2: Using Environment Variables

Edit the `.env` file with your credentials:
```
SECRET_KEY=your-secret-key-here
```

Then configure credentials via the web UI.

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Configure your M-Pesa credentials in the Settings page (if not already done)

  - The callback URL field now auto-fills with your workspace URL (for example, Codespaces will use `https://<codespace>-5000.app.github.dev`). You can override it with any reachable HTTPS endpoint if needed.

4. Return to the Home page and fill in the payment details:
   - Phone Number (format: 254XXXXXXXXX or 07XXXXXXXX)
   - Amount (in KES)
   - Account Reference (optional)
   - Transaction Description (optional)

5. Click "Send STK Push" and the user will receive a payment prompt on their phone

## Testing

For testing in sandbox environment:
- Use Safaricom's sandbox credentials
- Test phone number: 254708374149 (or other test numbers provided by Safaricom)
- Set up a callback URL using ngrok or similar service for local testing:
  ```bash
  ngrok http 5000
  ```
  Then use the ngrok URL as your callback URL in settings

## Project Structure

```
Mpesastk/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore file
├── README.md             # This file
├── config.json           # M-Pesa credentials (auto-generated, not in git)
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Home page (STK push form)
    └── settings.html     # Settings page (credentials)
```

## Security Considerations

- Never commit `config.json` or `.env` files to version control
- Use environment variables for production deployments
- Implement proper authentication for production use
- Use HTTPS for callback URLs in production
- Consider encrypting stored credentials

## API Endpoints

- `GET /` - Home page (STK push form)
- `GET /settings` - Settings page
- `POST /settings` - Save M-Pesa credentials
- `POST /stk-push` - Initiate STK push payment

## Troubleshooting

**Issue: "Failed to get access token"**
- Verify your Consumer Key and Consumer Secret are correct
- Check if you're using the correct API endpoint (sandbox vs production)

**Issue: "STK push failed"**
- Ensure the phone number is in the correct format (254XXXXXXXXX)
- Verify the business shortcode and passkey are correct
- Check if the amount is valid (minimum 1 KES)

**Issue: "Callback URL error"**
- Ensure your callback URL is accessible from the internet
- For local testing, use ngrok to create a public URL

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
