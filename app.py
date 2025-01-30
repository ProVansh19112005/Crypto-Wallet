from flask import Flask, render_template, request, session, redirect, url_for
from wallet import create_wallet, get_balance, send_litecoin
import traceback

app = Flask(__name__)
app.secret_key = 'ac961dafeec55d08a258ccbae2c4cebf5cbcc3ca7632e19d636982b87ca7462c'

@app.route('/')
def home():
    # Pass the address from the session to the template
    address = session.get('address')  # Get address from session
    return render_template('index.html', address=address)

@app.route('/create_wallet', methods=['POST', 'GET'])
def create_wallet_page():
    if request.method == 'POST':
        address, private_key = create_wallet()
        if address and private_key:
            session['address'] = address  # Store address in session
            return render_template('wallet_created.html', address=address, private_key=private_key)
        else:
            return "Failed to create wallet", 500
    return render_template('create_wallet.html')  # Render the form if GET request

@app.route('/wallet_balance/<address>', methods=['GET'])
def wallet_balance(address):
    # Ensure the address exists in the session
    if not session.get('address') or session.get('address') != address:
        return redirect(url_for('home'))  # Redirect to home page if no address in session

    try:
        balance = get_balance(address)
        return render_template('wallet_balance.html', address=address, balance=balance)
    except Exception as e:
        return f"Error: {str(e)}\n{traceback.format_exc()}", 500

@app.route('/send', methods=["GET", "POST"])
def send_page():
    if request.method == "POST":
        private_key = request.form.get("private_key")
        recipient = request.form.get("recipient")
        amount = float(request.form.get("amount"))
        tx = send_litecoin(private_key, recipient, amount)
        if tx:
            return render_template("transaction_successful.html", tx=tx)
        else:
            return render_template("transaction_failure.html")
    return render_template("send_litecoin.html")

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}")
    return "Internal Server Error", 500

@app.route('/clear_session')
def clear_session():
    session.clear()  # Clear the session
    return "Session cleared!"

if __name__ == '__main__':
    app.run(debug=True)



