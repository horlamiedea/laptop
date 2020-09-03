<h1># laptop
an ecommerce website with django</h1>

<h2>After cloning this repo: TODO:
pip install -r requirements.txt<h2>

Inside the folder dir:
 run: 
 py manage.py makemigrations
 py manage.py migrate
 py manage.py createsuperuser -- To create a super user to access the admin page
 
 To run migrations on admin server
 
 run:
  py manage.py runserver --To run project on local host
   open browser follow the local host link and add "/admin" 
   Login with your superuser credentials 
   Go down to Items and create few items to display on the front-end
   
   <h2>Under template, check payment.html for the payment template and PaymentView in the views.py</h2>
   <h3> payment link is <span>http://127.0.0.1:8000/payment/credit/</span>
   <p> check urls.py to check available urls</p>
   
   
   
   
