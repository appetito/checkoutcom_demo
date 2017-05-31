# -*- coding: utf-8 -*-
import unittest
import mock

import app


class Resp:

    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    @mock.patch('requests.post')
    def test_checkouts_usd_ok(self, mock_post):
        payment = {
            "Payment": {
                "ID": 123,
                "Status": {"ID": 11, "Info": "Captured", "Reasons": []},
                "CreditCardToken": {"Value": "zxc"}
            }
        }
        mock_post.return_value = Resp(payment, 200)
        data = {
            "currency": "USD",
            "price_USD": "11",
            "price_EUR": "7",
            "amount": "2",
            "card_holder": "CH",
            "card_number": "333",
            "card_exp_month": "11",
            "card_exp_year": "22",
            "card_cvv": "123",
        }
        res = self.app.post('/checkouts', data=data)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/checkouts/123", res.location)
        mock_post.assert_called_with(
            'https://securetest.smart2pay.com/v1/payments',
            auth=mock.ANY,
            json={'Payment': {
                'MerchantTransactionID': mock.ANY,
                'Amount': 2200,
                'Currency': 'USD',
                'ReturnURL': 'https://smart2pay-demo-db2.herokuapp.com/redirect',
                'Customer': {'Email': 'youremail@email.com'},
                'Card': {'HolderName': 'CH', 'Number': '333', 'ExpirationMonth': '11',
                         'ExpirationYear': '22', 'SecurityCode': '123'},
                'Capture': True,
                'GenerateCreditCardToken': True}})

    @mock.patch('requests.post')
    def test_checkouts_eur_ok(self, mock_post):
        payment = {
            "Payment": {
                "ID": 123,
                "Status": {"ID": 11, "Info": "Captured", "Reasons": []},
                "CreditCardToken": {"Value": "zxc"}
            }
        }
        mock_post.return_value = Resp(payment, 200)
        data = {
            "currency": "EUR",
            "price_USD": "11",
            "price_EUR": "7",
            "amount": "2",
            "card_holder": "CH",
            "card_number": "333",
            "card_exp_month": "11",
            "card_exp_year": "22",
            "card_cvv": "123",
        }
        res = self.app.post('/checkouts', data=data)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/checkouts/123", res.location)
        mock_post.assert_called_with(
            'https://securetest.smart2pay.com/v1/payments',
            auth=mock.ANY,
            json={'Payment': {
                'MerchantTransactionID': mock.ANY,
                'Amount': 1400,
                'Currency': 'EUR',
                'ReturnURL': 'https://smart2pay-demo-db2.herokuapp.com/redirect',
                'Customer': {'Email': 'youremail@email.com'},
                'Card': {'HolderName': 'CH', 'Number': '333', 'ExpirationMonth': '11',
                         'ExpirationYear': '22', 'SecurityCode': '123'},
                'Capture': True,
                'GenerateCreditCardToken': True}})

    @mock.patch('requests.get')
    def test_show(self, mock_get):
        payment = {
            "Payment": {
                "ID": 123321,
                "Status": {"ID": 11, "Info": "Captured", "Reasons": []},
                "CreditCardToken": {"Value": "zxc"}
            }
        }
        with app.app.test_client() as c:
            with c.session_transaction() as sess:
                sess["payment"] = payment["Payment"]
            res = c.get('/checkouts/123')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"zxc", res.data)
        self.assertIn(b"123321", res.data)

    @mock.patch('requests.post')
    def test_checkout_more(self, mock_post):
        payment = {
            "Payment": {
                "ID": 12344,
                "Status": {"ID": 11, "Info": "Captured", "Reasons": []},
                "CreditCardToken": {"Value": "zxc"}
            }
        }
        mock_post.return_value = Resp(payment, 200)
        with app.app.test_client() as c:
            with c.session_transaction() as sess:
                sess["payment_method_token"] = {"Value": "xyz222"}
            res = c.post('/checkouts/one_more', data={"price": "123"})
        self.assertEqual(res.status_code, 302)
        self.assertIn("/checkouts/12344", res.location)
        mock_post.assert_called_with(
            'https://securetest.smart2pay.com/v1/payments',
            auth=mock.ANY,
            json={
                'Payment': {
                    'MerchantTransactionID': mock.ANY,
                    'Amount': 12300,
                    'Currency': 'USD',
                    'ReturnURL': 'https://smart2pay-demo-db2.herokuapp.com/redirect',
                    'Customer': {
                        'Email': 'youremail@email.com'},
                    'CreditCardToken': {
                        'Value': 'xyz222'},
                    'Capture': True,
                    'Retry': True,
                    'GenerateCreditCardToken': True}})

    @mock.patch('requests.post')
    @mock.patch('requests.get')
    def test_refund(self, mock_get, mock_post):
        payment = {
            "Payment": {
                "ID": 321,
                "Amount": "1200"
            }
        }
        mock_get.return_value = Resp(payment, 200)
        mock_post.return_value = Resp({"OK": "OK"}, 200)
        res = self.app.post('/refund', data={'payment_id': 321, "tx_id": "abc"})
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"OK", res.data)
        mock_post.assert_called_with(
            'https://securetest.smart2pay.com/v1/payments/321/refunds',
            auth=mock.ANY,
            json={'Refund': {'MerchantTransactionID': 'abc', 'Amount': '1200'}})


    @mock.patch('requests.post')
    def test_refund_partial(self, mock_post):
        mock_post.return_value = Resp({"OK": "OK"}, 200)
        res = self.app.post('/refund/partial',
                            data={'payment_id': 321, "tx_id": "abc", "amount": 45})
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"OK", res.data)
        mock_post.assert_called_with(
            'https://securetest.smart2pay.com/v1/payments/321/refunds',
            auth=mock.ANY,
            json={'Refund': {'MerchantTransactionID': 'abc', 'Amount': 4500}})


if __name__ == '__main__':
    unittest.main()
