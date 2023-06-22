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
    borrower = db.Column(db.String(200), nullable=False)
    date_borrowed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_returned = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Lend %r>' % self.id

with app.app_context():
    db.create_all()

# Creating the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        item = request.form['item']
        borrower = request.form['borrower']
        lend = Lend(item=item, borrower=borrower)

        try:
            db.session.add(lend)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your lend'
    else:
        lends = Lend.query.order_by(desc(Lend.date_borrowed)).all()
        
        #Format date & time
        for lend in lends:
            lend.date_borrowed = lend.date_borrowed.strftime('%d/%m/%Y %H:%M')
            if lend.date_returned:
                lend.date_returned = lend.date_returned.strftime('%d/%m/%Y %H:%M')
        
        return render_template('index.html', lends=lends)

# Creating the update page
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    lend = Lend.query.get_or_404(id)

    if request.method == 'POST':
        lend.item = request.form['item']
        lend.borrower = request.form['borrower']
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

# Running the app
if __name__ == '__main__':
    app.run(debug=True)