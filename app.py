from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from pip._vendor import requests
from wtforms import StringField, DecimalField, SelectField, DateField

# By: Samantha Fernandez
# Project: 4
# Course: COP 4813

app = Flask(__name__)
app.config["SECRET_KEY"] = "cop4813"
app.config["MONGO_URI"] = "mongodb+srv://sam:admin@project3.pu9tc.mongodb.net/Project3?retryWrites=true&w=majority"
mongo = PyMongo(app)


class Expenses(FlaskForm):
    # TO BE COMPLETED (please delete the word pass above)
    categories = ['Bills', 'Cash & Checks', 'Food',
                  'Travel', 'Entertainment', 'Shopping',
                  'Services', 'Medical', 'Legal']
    category = SelectField('Categories', choices=categories)
    description = StringField('Description')
    currency = SelectField('Currency', choices=[('us', 'US Dollar'),
                                                ('brazil', 'Brazilian Real'),
                                                ('euro', 'Euro'),
                                                ('colombian', 'Colombian Peso'),
                                                ('cuban', 'Cuban Peso')])
    cost = DecimalField('Cost ($)')
    date = DateField('Date', format='%m/%d/%Y')


def get_total_expenses(category):
    expenses_total = 0
    query = {"category": category}
    records = mongo.db.expenses.find(query)

    for i in records:
        expenses_total += float(i["cost"])
    return expenses_total

def currency_converter(cost,currency):
    url="http://api.currencylayer.com/live?access_key=12794a3fb5485f0a550bc92e13a4e2d5"
    response = requests.get(url).json()
    ### YOUR TASK IS TO COMPLETE THIS FUNCTION
    if currency == 'us':
        converted_cost = cost
    elif currency == 'brazil':
        converted_cost = cost / response["quotes"]["USDBRL"]
    elif currency == 'euro':
        converted_cost = cost / response["quotes"]["USDEUR"]
    elif currency == 'colombian':
        converted_cost = cost / response["quotes"]["USDCOP"]
    elif currency == 'cuban':
        converted_cost = cost / response["quotes"]["USDCUP"]
    return converted_cost

@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i["cost"])
    # expensesByCategory is a list of tuples
    # each tuple has two elements:
    ## a string containing the category label, for example, insurance
    ## the total cost of this category
    expensesByCategory = [('Bills', get_total_expenses('Bills')),
                          ('Cash & Checks', get_total_expenses('Cash & Checks')),
                          ('Food', get_total_expenses('Food')),
                          ('Travel', get_total_expenses('Travel')),
                          ('Entertainment', get_total_expenses('Entertainment')),
                          ('Shopping', get_total_expenses('Shopping')),
                          ('Services', get_total_expenses('Services')),
                          ('Medical', get_total_expenses('Medical')),
                          ('Legal', get_total_expenses('Legal'))]

    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)


@app.route('/addExpenses', methods=["GET", "POST"])
def addExpenses():
    # INCLUDE THE FORM
    expensesForm = Expenses()
    if request.method == "POST":
        # INSERT ONE DOCUMENT TO THE DATABASE
        # CONTAINING THE DATA LOGGED BY THE USER
        description = request.form['description']
        category = request.form['category']
        currency = request.form['currency']
        cost = request.form['cost']
        date = request.form['date']

        #convert cost inputed using currency converter function
        cost = currency_converter(float(cost), currency)

        # REMEMBER THAT IT SHOULD BE A PYTHON DICTIONARY
        document_data = {'description': description,
                         'category': category, 'cost': cost, 'date': date}

        mongo.db.expenses.insert_one(document_data)
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html", form=expensesForm)

app.run()
