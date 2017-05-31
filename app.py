from flask import Flask, redirect, url_for, render_template, request, flash, session, jsonify

import decimal
import os
import uuid
from os.path import join, dirname
from dotenv import load_dotenv
import requests

app = Flask(__name__)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
app.secret_key = os.environ.get('APP_SECRET_KEY')


API_URL = "https://sandbox.checkout.com/api2/v2"
auth_headers = {"Authorization": os.environ.get('SECRET_KEY')}



@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('new_checkout'))


@app.route('/checkouts/new', methods=['GET'])
def new_checkout():
    return render_template('checkouts/new.html')


@app.route('/checkouts/<tx_id>', methods=['GET'])
def show_checkout(tx_id):
    # url = API_URL + '/payments/{}'.format(tx_id)
    # resp = requests.get(url, auth=auth_pair)
    payment = session["payment"]
    result = {}
    if payment["status"] == 'Authorised':
        result = {
            'header': 'Sweet Success!',
            'icon': 'success',
            'message': ('Your test transaction has been successfully processed.'
                        'See the API response and try again.')
        }
    else:
        result = {
            'header': 'Transaction Failed',
            'icon': 'fail',
            'message': ('Your test transaction has a status of '
                        '{responseCode} ({responseMessage}): {responseAdvancedInfo}. See'
                        ' API response and try again.').format(**payment)
        }

    return render_template('checkouts/show.html', payment=payment, result=result)

"""
curl https://sandbox.checkout.com/api2/v2/charges/card
  -H "Authorization: sk_test_55aedccc-7f53-4ccc-b0a6-d943decc3c31"
  -H "Content-Type:application/json;charset=UTF-8"
  -X POST
  -d '{
        "autoCapTime": "24",
        "autoCapture": "Y",
        "chargeMode": 1,
        "email": "testuser@email.com",
        "customerName": "Seymour Duncan",
        "description": "charge description",
        "value": "4298",
        "currency": "GBP",
        "trackId": "TRK12345",
        "transactionIndicator": "1",
        "customerIp":"96.125.185.51",
        "card": {
          "name": "Seymour Duncan",
          "number": "4242424242424242",
          "expiryMonth": "06",
          "expiryYear": "2018",
          "cvv": "100",
          "billingDetails": {
              "addressLine1": "623 Slade Street",
              "addressLine2": "Flat 9",
              "postcode": "E149SR",
              "country": "UK",
              "city": "London",
              "state": "Greater London",
              "phone" : {
                  "countryCode" : "44",
                  "number" : "12345678"
              }
          }
        },
        "shippingDetails": {
              "addressLine1": "623 Slade Street",
              "addressLine2": "Flat 9",
              "postcode": "E149SR",
              "country": "UK",
              "city": "London",
              "state": "Greater London",
              "phone" : {
                  "countryCode" : "44",
                  "number" : "12345678"
              }
        },
        "products": [
          {
            "description": "Tablet 1 gold limited",
            "image": null,
            "name": "Tablet 1 gold limited",
            "price": 100.0,
            "quantity": 1,
            "shippingCost": 10.0,
            "sku": "1aab2aa",
            "trackingUrl": "https://www.tracker.com"
          },
          {
            "description": "Tablet 2 gold limited",
            "image": null,
            "name": "Tablet 2 gold limited",
            "price": 200.0,
            "quantity": 2,
            "shippingCost": 10.0,
            "sku": "1aab2aa",
            "trackingUrl": "https://www.tracker.com"
          }
        ],
        "metadata": {
          "key1": "value1"
        },
        "udf1": "udf 1 value",
        "udf2": "udf 2 value",
        "udf3": "udf 3 value",
        "udf4": "udf 4 value",
        "udf5": "udf 5 value"
      } '
"""

@app.route('/checkouts', methods=['POST'])
def create_checkout():
    curr = request.form['currency']
    price_key = 'price_' + curr
    price = decimal.Decimal(request.form[price_key])
    tx_amount = int(request.form['amount']) * price * 100
    tx_data = {
        "email": 'mail@example.com',
        "value": int(tx_amount),
        "currency": curr,
        "trackId": str(uuid.uuid4())[:8],
        "card": {
          "name": request.form['card_holder'],
          "number": request.form['card_number'],
          "expiryMonth": request.form['card_exp_month'],
          "expiryYear": request.form['card_exp_year'],
          "cvv": request.form['card_cvv'],
        }}
    resp = requests.post(API_URL + '/charges/card', json=tx_data, headers=auth_headers)
    print("PUSHED::", tx_data)
    print("RESP::", resp)
    # return resp.content
    payment = resp.json()
    # s = payment["Status"]
    session["payment"] = payment

    if payment["status"] == "Authorised":  # Transaction Approved
        session["card_id"] = payment["card"]["id"]
        print("ALLOK    ")
        return redirect(url_for('show_checkout', tx_id=payment["id"]))
    else:
        return redirect(url_for('show_checkout', tx_id=payment["id"] or 'xxx'))


@app.route('/checkouts/one_more', methods=['POST'])
def create_checkout_more():
    price = decimal.Decimal(request.form["price"])

    tx_amount = price * 100
    tx_data = {
        "email": 'mail@example.com',
        "value": int(tx_amount),
        "currency": "USD",
        "trackId": str(uuid.uuid4())[:8],
        # "cardId": session["card_id"],
    }

    resp = requests.post(API_URL + '/charges/customer', json=tx_data, headers=auth_headers)
    print("PUSHED::", tx_data)
    print("RESP::", resp.content)
    print("RESP::", resp)
    payment = resp.json()

    session["payment"] = payment
    if payment["status"] == "Authorised":  # Transaction Approved
        return redirect(url_for('show_checkout', tx_id=payment["id"]))
    else:
        return redirect(url_for('show_checkout', tx_id=payment["id"] or 'xxx'))


@app.route('/refund/partial', methods=['POST'])
def refund_partial():
    data = {
        "value": int(decimal.Decimal(request.form["amount"])) * 100
    }
    url = API_URL + '/charges/{}/refund'.format(request.form["payment_id"])
    
    result = requests.post(url, json=data, headers=auth_headers)
    print("PUSHED::", url, data)
    return jsonify(result.json())


@app.route('/refund', methods=['POST'])
def refund():
    url = API_URL + '/charges/{}/history'.format(request.form["payment_id"])
    result = requests.get(url, headers=auth_headers)
    for charge in result.json()["charges"]:
        if charge["status"] == "Captured":
            chargeId = charge["id"]

    url = API_URL + '/charges/{}/refund'.format(chargeId)
    result = requests.post(url, json={}, headers=auth_headers)
    print("PUSHED::", url)
    return jsonify(result.json())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4567, debug=True)
