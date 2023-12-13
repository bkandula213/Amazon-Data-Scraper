from flask import Flask, redirect, url_for, request, render_template
from flask_mail import Mail, Message
from test_selenium import scrape_data
import json

app = Flask(__name__)
mail = Mail(app)

# Basic Setup

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'temowork7@gmail.com'
app.config['MAIL_PASSWORD'] = 'zncf xkkm vgxy jxpo'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# Routes

@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/form')
def formpage():
    return render_template('index.html')

@app.route('/results', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        product = request.form['product']
        key_part = request.form['keyPart']
        min_price = float(request.form.get('minPrice', 0))
        max_price = float(request.form.get('maxPrice', float('inf')))

        data = scrape_data(product, key_part)

        # Filter data based on price range
        filtered_data = []
        for item in data:
            item_price_str = item.get('item_price', '')
            try:
                item_price = float(item_price_str)
                if min_price <= item_price <= max_price:
                    filtered_data.append(item)
            except ValueError:
                pass

        with open("filtered_output.json", "w") as file:
            json.dump(filtered_data, file)

        # Send mail of filtered data
        msg = Message('Amazon Scraper Results', sender='temowork7@gmail.com', recipients=['kogantiaditya1@gmail.com'])
        msg.body = "Hello Flask message sent from Flask-Mail 2"
        with app.open_resource("filtered_output.json") as file:
            msg.attach("filtered_output.json", 'application/json', file.read())
        mail.send(msg)

        # Render results template with filtered data
        return render_template('results.html', data=filtered_data)
    else:
        user = request.args.get('nm')
        return redirect(url_for('success', name=user))

if __name__ == '__main__':
    app.run(debug=True)
