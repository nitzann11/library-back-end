import json
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import jsonify

from datetime import datetime, timedelta
#----------------------------------------------------------------------------------------------------------
#database, cors,flaskapp
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.sqlite3'
app.config['SECRET_KEY'] = "random string"
 
db = SQLAlchemy(app)
CORS(app)
#----------------------------------------------------------------------------------------------------------
# model - Books , Customers , Loans , BookType
class BookType(db.Model):
    id = db.Column( db.Integer, primary_key = True)
    description = db.Column(db.String(200))
    maxDay = db.Column(db.Integer)
    booktype = db.relationship('Books', lazy='select',
        backref=db.backref('booktype', lazy='joined'))

    def __init__(self, description,maxDay):
        self.description = description
        self.maxDay = maxDay

class Books(db.Model):
    id = db.Column( db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    author = db.Column(db.String(100))
    yearPublished = db.Column(db.Integer)
    booktypeId = db.Column(db.Integer, db.ForeignKey(BookType.id))
    loans = db.relationship('Loans', lazy='select',backref=db.backref('booksLoan', lazy='joined'))
    active = db.Column(db.String(10), nullable=False, server_default='active')
    
    def __init__(self,name,author,yearPublished,booktypeId,active='active'):
        self.name = name
        self.author = author
        self.yearPublished = yearPublished
        self.booktypeId = booktypeId
        self.active = active



class Customers(db.Model):
    id = db.Column( db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(200))
    age=db.Column(db.Integer)
    active = db.Column(db.String(10), nullable=False, server_default='active')
    
    def __init__(self, name,city,age,active='active'):
        self.name = name
        self.city = city
        self.age = age
        self.active = active

class Loans(db.Model):
    custId = db.Column(db.Integer, db.ForeignKey('customers.id'),primary_key = True)
    bookId = db.Column(db.Integer, db.ForeignKey('books.id'),primary_key = True)  
    loandate = db.Column(db.DateTime,default=datetime.now,primary_key = True)
    returndate=db.Column(db.DateTime,default=None)
   
    books = db.relationship('Books', lazy='select',
        backref=db.backref('books', lazy='joined'))
    customers = db.relationship('Customers', lazy='select',
        backref=db.backref('customers', lazy='joined'))

    def __init__(self, custId,bookId,loandate):
        self.custId = custId
        self.bookId = bookId
        self.loandate = loandate
    
# model
 #----------------------------------------------------------------------------------------------------------
# views
# Books CRUD
@app.route('/books/', methods = ['GET', 'POST'])
@app.route('/books/<id>', methods = ['GET','DELETE','PUT'])
def get_all_books(id=-1):

    if request.method == "GET": #read
        res=[]
        for book in Books.query.order_by(Books.name.asc()).all():
            res.append({"id":book.id,"name":book.name,"author":book.author,"yearPublished":book.yearPublished,"booktypeId":book.booktypeId,"booktypeName":book.booktype.description,"active":book.active})
        return  (json.dumps(res))

    if request.method == "POST": #create
        request_data = request.get_json()
        name = request_data["name"]
        author = request_data["author"]
        yearPublished = request_data["yearPublished"]
        booktypeId = request_data["booktypeId"]     #need to chek the booktypeId of 
        newBook = Books(name,author,yearPublished,booktypeId,active='active') 
        db.session.add (newBook)
        db.session.commit()
        return {'massage' :"a new Book was create"}

    if request.method == "DELETE": #DELETE
        if(len(Loans.query.filter(Loans.bookId==id).all())>0):#check if book exists in loan 
            return("Can not delete books that have loans!")
        db.session.delete(Books.query.get(id))
        db.session.commit()
        # del_book = Books.query.get(id)
        # del_book.active = 'false'
        # db.session.commit()
        return  {'massage' :"the book deleted"}

    if request.method == "PUT": #update
        update_book = Books.query.get(id)
        active = request.json['active']
        update_book.active = active
        db.session.commit()
        return  {'massage' : 'a book was Activated'}

 #----------------------------------------------------------------------------------------------------------
# Customers CRUD
@app.route('/customers/<id>', methods = ['GET','DELETE','PUT'])
@app.route('/customers/', methods = ['GET', 'POST'])
def get_all_customers(id=-1):

    if request.method == "POST": #create
        request_data = request.get_json()
        # print(request_data['city'])
        name = request_data["name"]
        city = request_data["city"]
        age = request_data["age"]
        newCustomer = Customers(name,city,age,active='active') 
        print(newCustomer)
        db.session.add (newCustomer)
        db.session.commit()
        return {'massage' :"a new Customer create"}

    if request.method == "GET": #read 
        res=[]
        for cust in Customers.query.order_by(Customers.name.asc()).all():
            res.append({"id":cust.id,"name":cust.name,"city":cust.city,"age":cust.age,"active":cust.active})
        return  (json.dumps(res))

    if request.method == "DELETE": #delete
        if(len(Loans.query.filter(Loans.custId==id).all())>0):#check if customer exists in loan 
            return("Can not delete customers that have loans!")
        db.session.delete(Customers.query.get(id))
        db.session.commit()
        # del_customer = Customers.query.get(id)
        # del_customer.active = "false"
        # db.session.commit()
        return  {'massage' :"the Customer deleted"}
    if request.method == "PUT": #update
        print(id)  # checking the id in the terminal
        update_customer = Customers.query.get(id)
        active = request.json['active']
        update_customer.active = active
        db.session.commit()
        return  {'massage' :"the Customer update"}

#----------------------------------------------------------------------------------------------------------
# loans CRUD
@app.route('/loans/<id>', methods = ['GET','DELETE','PUT'])
@app.route('/loans/', methods = ['GET', 'POST'])
def get_all_loans(id=-1):

    if request.method == "GET": #read
        res=[]
        for loan in Loans.query.order_by(Loans.loandate.desc()).all():
            returnDate=loan.returndate if (loan.returndate==None) else loan.returndate.date()
            res.append({"custId":loan.custId,"bookId":loan.bookId,"loandate":str(loan.loandate.date()),"returndate":str(returnDate),"bookname":loan.books.name,"custname":loan.customers.name})
        return  json.dumps(res)

    if request.method == 'POST':
        request_data = request.get_json()
        custId= request_data["custId"]
        bookId= request_data["bookId"]
        now=datetime.now().strftime('%m/%d/%y %H:%M:%S')
        loandate = datetime.strptime(now, '%m/%d/%y %H:%M:%S')
        newLoan= Loans(custId,bookId,loandate)
        db.session.add (newLoan)
        db.session.commit()
        return{'massage': 'Book Was Loaned'}

    if request.method == "PUT": #return a book
        print(id)
        loan= Loans.query.filter((Loans.bookId == id) & (Loans.returndate==None)).first()   
        now=datetime.now().strftime('%m/%d/%y %H:%M:%S')
        returndate = datetime.strptime(now, '%m/%d/%y %H:%M:%S')
        loan.returndate=returndate    
        db.session.commit()
        return  ("the book was returned")
#----------------------------------------------------------------------------------------------------------
# late loans CRUD
@app.route('/lateloans', methods = ['GET'])
def get_lateLoans(id=-1):
    if request.method == "GET": #read get late loans
        res=[]
        now=datetime.now()
        for loan in Loans.query.filter((Loans.returndate==None)).order_by(Loans.loandate.desc()).all():
            maxday=loan.books.booktype.maxDay
            loandate=loan.loandate
            maxDateReturn=(loandate+ timedelta(days=maxday)).date()
            nowDate=datetime.now().date()
            dayslate=(maxDateReturn-nowDate).days
            if dayslate < 0:
                res.append({"custname":loan.customers.name,"bookname":loan.books.name,"loandate":str(loan.loandate),"dayslate":dayslate})
        return  (json.dumps(res))

#----------------------------------------------------------------------------------------------------------
# booktypes CRUD
@app.route('/booktypes/<id>', methods = ['GET'])
@app.route('/booktypes/', methods = ['GET','POST'])
def get_all_booktypes(id=-1):
    if request.method == "GET": #read 
        res=[]
        if(id!=-1):# if send booktype id get book type by id
            booktype=BookType.query.get(id)
            res.append({"id":booktype.id,"description":booktype.description,"maxDay":booktype.maxDay})
        else:# if not send booktype id get all book types 
            for booktype in BookType.query.all():
                res.append({"id":booktype.id,"description":booktype.description,"maxDay":booktype.maxDay})
        return  (json.dumps(res)) 
    # if request.method == "POST":      # ////////////////////////////// the post method was to add the initial days info
    #     request_data = request.get_json()
    #     description = request_data["description"]
    #     maxDay = request_data["maxDay"]
    #     newBooktype = BookType(description,maxDay) #,active='active'
    #     print(newBooktype)
    #     db.session.add (newBooktype)
    #     db.session.commit()
    #     return {'massage' :"a newBooktype"}


    

#----------------------------------------------------------------------------------------------------------
#test
@app.route('/')
def hello():
    return {'massage' :'Hello, World!' }
#----------------------------------------------------------------------------------------------------------
#create all

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug = True)



