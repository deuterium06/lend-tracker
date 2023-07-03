'''
    A Flask web app to track the items you lend to borrower
'''

# Importing the required modules
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc

# Creating the Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configuring the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lend-tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creating the database object
db = SQLAlchemy(app)


# Creating the database model
class Lend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(200), nullable=False)
    # Add borrower_id column as a foreign key
    borrower_id = db.Column(db.Integer, db.ForeignKey('borrower.borrower_id'), nullable=False)
    date_borrowed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_returned = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Lend %r>' % self.id

# Creating the database model for borrower
class Borrower(db.Model):
    borrower_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)

    # Add a relationship to Lend table
    lends = db.relationship('Lend', backref='borrower', lazy=True)

    def __repr__(self):
        return '<Borrower %r>' % self.borrower_id

with app.app_context():
    db.create_all()

# Creating the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item = request.form['item']
        borrower_id = request.form['borrower']
        lend = Lend(item=item, borrower_id=borrower_id)

        try:
            db.session.add(lend)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your lend'
    else:
        #Create a lend query with join in order to get the borrower name
        lends = Lend.query\
            .join(Borrower, Lend.borrower_id==Borrower.borrower_id)\
            .add_columns(Lend.id, Lend.item, Lend.borrower_id, Borrower.name, Lend.date_borrowed, Lend.date_returned)\
            .order_by(desc(Lend.date_borrowed))\
            .all()\

        borrowers = Borrower.query.all()
        
        return render_template('index.html', lends=lends, borrowers=borrowers)

# Creating the update page
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    lend = Lend.query.get_or_404(id)

    if request.method == 'POST':
        lend.item = request.form['item']
        date_returned = request.form.get('is_returned')

        if date_returned == 'on':
            lend.date_returned = datetime.utcnow()

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your lend'
    else:
        return render_template('update.html', lend=lend)

# Creating the delete page
@app.route('/delete/<int:id>')
def delete(id):
    lend = Lend.query.get_or_404(id)

    try:
        db.session.delete(lend)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an issue deleting your lend'

# Creating the borrower page
@app.route('/new_borrower', methods=['GET', 'POST'])
def new_borrower():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']

        borrower = Borrower(name=name, phone=phone, email=email)

        try:
            db.session.add(borrower)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your borrower'
    else:
        return render_template('new_borrower.html')

# Creating the borrower details page
@app.route('/borrower_details/<int:id>')
def borrower_details(id):
    lends = Lend.query.filter_by(borrower_id=id).order_by(desc(Lend.date_borrowed)).all()
    borrower = Borrower.query.get_or_404(id)

    return render_template('borrower_details.html', lends=lends, borrower=borrower)

# Running the app
if __name__ == '__main__':
    app.run(debug=True)