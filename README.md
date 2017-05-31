# Checkout.com Flask Example

An example Checkout.com integration for python in the Flask framework.

## Demo app requirements

Here are the requirments for Checkout.com: 
Use Cases: 
- user wants to buy one product in USD 
- user wants to buy one product in EUR 
- user wants to buy one product with a quantity of 2 or more in USD 
- user cancels the buying process 
- user able to buy extra product on thank you page without submitting credit card info again 
- user enter a different mail and/or address information on the payment service provider site 
- refunds the sales order completely 
- refund the sales order partially

Requirements: 
- please implement every use case from above 
- use flask as a web framework 
- unit tests needed 
- you can use the offical SDK or a well supported opensource SDK if there is one. If not, please build one first. 
- the HTML part should be very minimalistic. No theme required. But you can use one if you want. 
- you can use any DB you want if you need one. MongoDB would be nice. 


Deliverables: 
- I need a process diagram how the communication with the payment method provider works (you can link the original picture/page if there is one) 
- instructions on how to run the project locally 
- deployment instructions


## Setup Instructions

1. Install requirements:
  ```sh
  pip install -r requirements.txt
  ```

2. Copy the contents of `example.env` into a new file named `.env` and fill in your Checkout.com API credentials. Credentials can be found by navigating to Account > My User > View Authorizations in the Checkout.com Control Panel. Full instructions can be [found on our support site](https://articles.Checkout.compayments.com/control-panel/important-gateway-credentials#api-credentials).

3. Start server:
  ```sh
  python app.py
  ```

## How it works

https://developers.Checkout.compayments.com/start/overview#how-it-works
https://developers.Checkout.compayments.com/guides/transactions/python#status
