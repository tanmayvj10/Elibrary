import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import render_template,request,redirect,url_for,flash
from werkzeug.security import generate_password_hash,check_password_hash
from flask import session
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from collections import defaultdict

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "testdb.sqlite3")
db = SQLAlchemy(app)

## models

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique = True, nullable=False)
    passhash = db.Column(db.String(512), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    age = db.Column(db.Integer)
    user_img = db.Column(db.String(64), default='default.jpg')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.passhash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.passhash,password)
    
class Librarian(db.Model):
    lib_id = db.Column(db.Integer, primary_key=True)
    passhash = db.Column(db.String(512), nullable=False)
    name = db.Column(db.String(64))
    lib_img = db.Column(db.String(64), default='default.jpg')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,passhash):
        self.passhash = generate_password_hash(passhash)

    def check_password(self,passhash):
        return check_password_hash(self.passhash,passhash)

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    passhash = db.Column(db.String(512), nullable=False)
    name = db.Column(db.String(64))
    admin_img = db.Column(db.String(64), default='default.jpg')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.passhash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.passhash,password)

class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_title = db.Column(db.String(64), nullable=False)
    author = db.Column(db.String(32), nullable=False)
    rating = db.Column(db.Integer)
    description = db.Column(db.String(1024))
    link = db.Column(db.String(64), nullable=False)
    section_id = db.Column(db.String(16), nullable=False)
    book_cover = db.Column(db.String(64), default='book_cover.jpg')
    added_by = db.Column(db.String(16), nullable=False)
    date_added = db.Column(db.Date,nullable=False)
    # Relationship to Books_reviews
    reviews = db.relationship('Books_reviews', backref='book', lazy='dynamic')

    @property
    def rating(self):
        # Calculate the average rating using SQLAlchemy's func.avg
        avg_rating = db.session.query(func.avg(Books_reviews.rating)).filter_by(book_id=self.id).scalar()
        # Return the average rating, or None if no reviews exist
        return avg_rating or None


class Books_issued(db.Model):
    issue_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    issued_by = db.Column(db.String(16), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    access_date = db.Column(db.Date, nullable=False)

class Books_reviews(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    reviews = db.Column(db.String(1024))

class Books_completed(db.Model):
    record = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
class Sections(db.Model):
    section_id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(1024))
    added_by = db.Column(db.String(16), nullable=False)
    prime = db.Column(db.String(1), default='0')
    date_added = db.Column(db.Date,nullable=False)
class Favorites(db.Model):
    fav_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
class User_req(db.Model):
    req_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    days = db.Column(db.Integer, nullable=False)

class Prime(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    
class Prime_req(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    
class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=16)])
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    age = StringField('Age', validators=[DataRequired()])
    update_profile = SubmitField('Update Profile')

class DeleteAccountForm(FlaskForm):
    confirm_delete = SubmitField('Delete Profile')

with app.app_context():
    db.create_all()
    admin=Admin.query.filter_by(admin_id=1024).first()
    if not admin:
        admin_id = '1024'
        password = 'pass'
        passhash=generate_password_hash(password)
        name = 'admin1'
        admin=Admin(admin_id=admin_id,passhash=passhash,name=name)
        db.session.add(admin)
        db.session.commit()

##routes

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login", methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    user = User.query.filter_by(username=username).first()
    if not user:
        flash("User doesnot exsist")
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash("Incorrect Password")
        return redirect(url_for('login'))
        # Successful login
    session['user_id'] = user.id
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    else:
        return redirect(url_for("booksdash"))
       
@app.route("/booksdash")
def booksdash():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
    else:
        return redirect(url_for('login'))
    pc = Prime.query.filter_by(user_id=user_id).first()
    sections = Sections.query.all() if pc else Sections.query.filter_by(prime='0').all()
    req = User_req.query.filter_by(user_id=user_id).all()
    
    filter_type = request.args.get('filter_type')
    search_input = request.args.get('search_input')

    if filter_type == 'section' and search_input:
        sections = Sections.query.filter(Sections.section.ilike(f'%{search_input}%')).all()
        for section in sections:
            section.books = Books.query.filter_by(section_id=section.section_id).all()
        if search_input=="":
            flash("Please enter a search input.")
    
    elif filter_type == 'author' and search_input:
        filtered_books = Books.query.filter(Books.author.ilike(f'%{search_input}%')).all()
        # Filter sections to include only those that have filtered books
        sections_with_books = []
        for section in sections:
            section.books = Books.query.filter((Books.section_id == section.section_id) & (Books.id.in_([book.id for book in filtered_books]))).all()
            if section.books:
                section.books = section.books
                sections_with_books.append(section)
            sections = sections_with_books
        if search_input=="":
            flash("Please enter a search input.")

    elif filter_type == 'book' and search_input:
        filtered_books = Books.query.filter(Books.book_title.ilike(f'%{search_input}%')).all()
        # Filter sections to include only those that have filtered books
        sections_with_books = []
        for section in sections:
            section.books = Books.query.filter((Books.section_id == section.section_id) & (Books.id.in_([book.id for book in filtered_books]))).all()
            if section.books:
                section.books = section.books
                sections_with_books.append(section)
            sections = sections_with_books
        if search_input=="":
            flash("Please enter a search input.")

        
    else:
        # If no filter applied or search input is empty, load all sections and their books
        for section in sections:
            section.books = Books.query.filter_by(section_id=section.section_id).all()
    latest = datetime.now().date()
    latest-= timedelta(days=7)
    return render_template('Dashboard.html', sections=sections, user=user, req=req,filter_type=filter_type,search_input=search_input,latest=latest)

@app.route("/filter-and-search", methods=['POST'])
def filter_and_search():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        session['referring_url'] = request.referrer
        
        # Retrieve form data
        filter_option = request.form['filter_option']
        search_query = request.form['search_query']
        
        # Filter books based on the selected option
        if filter_option == 'section':
            filtered_books = Books.query.filter_by(section_id=search_query).all()
        elif filter_option == 'book':
            filtered_books = Books.query.filter(Books.book_title.ilike(f'%{search_query}%')).all()
        else:
            filtered_books = []  # Handle invalid filter option
        
        # You can further process the filtered_books as needed
        
        # Convert filtered books data to a list of book IDs
        filtered_book_ids = [book.id for book in filtered_books]
        
        # Append filtered books data to the redirect URL as URL parameters
        
        # Redirect back to the referring URL with filtered books data
        return redirect(url_for('booksdash', filter_type=request.form['filter_option'], search_input=request.form['search_query']))
    else:
        # Handle case when user is not logged in
        flash('Please log in to access this feature.', 'warning')
        return redirect(url_for('login'))
    
@app.route("/book/<int:book_id>",methods=['GET','POST'])
def book(book_id):
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
    book = Books.query.filter_by(id=book_id).first()
     # Query the database to calculate the distribution of ratings
    ratings_distribution = db.session.query(
        Books_reviews.rating,
        db.func.count(Books_reviews.rating)
    ).filter_by(book_id=book_id).group_by(Books_reviews.rating).all()
    
    # Calculate the total number of ratings
    total_ratings = sum(count for _, count in ratings_distribution)

    # Calculate the percentage of ratings for each value
    ratings_percentage = {rating: (count / total_ratings) * 100 for rating, count in ratings_distribution}
    rating_percentage_list=[]
    for key in ratings_percentage:
        rating_percentage_list.append([key,ratings_percentage[key]])
    
    issue_count=Books_issued.query.filter_by(user_id=user_id).count()
    requested_count = User_req.query.filter_by(user_id=user_id).count() is not None
    count=issue_count+requested_count
    # Check if the book is already requested by the user or is already issued
    is_requested = User_req.query.filter_by(book_id=book_id, user_id=user_id).first() is not None
    is_issued = Books_issued.query.filter_by(book_id=book_id, user_id=user_id).first() is not None
    
    # Calculate age group distribution
    # Fetch all users
    all_users = User.query.all()

    # Calculate age group distribution
    age_groups = {'0-10': 0, '10-20': 0, '20-30': 0, '30-40': 0, '40-50': 0, '50-60': 0, '60-70': 0, '70-80': 0, '80-90': 0, '90+': 0, 'Ambigous': 0}
    for user in all_users:
        if user.age is not None:
            age_group = (user.age // 10) * 10
            if age_group < 0:
                age_group = '0-10'
            elif age_group >= 90:
                age_group = '90+'
            else:
                age_group = f'{age_group}-{age_group + 10}'
            age_groups[age_group] += 1
        else:
            age_group = 'Ambigous'
            age_group = f'{age_group}-{age_group + 10}'
            age_groups[age_group] += 1
    total_users = sum(age_groups.values())
    section=Sections.query.filter_by(section_id=book.section_id).first()    
    return render_template('book.html', book=book, user=user, is_requested=is_requested, is_issued=is_issued,count=count,ratings_percentage=ratings_percentage, age_groups=age_groups,total_users=total_users,section=section,rating_percentage_list=rating_percentage_list)

@app.route('/issue_book/<int:book_id>', methods=['POST'])
def issue_book(book_id):
    if 'user_id' in session:
        user_id = session['user_id']
    if request.method == 'POST':
        # Retrieve the number of days from the form
        days = request.form.get('days')
        # Add the request to the user_request table
        req = User_req(book_id=book_id, user_id=user_id, days=days)
        db.session.add(req)
        db.session.commit()
        flash('Book issued successfully!', 'success')
        return redirect(url_for('booksdash'))

@app.route("/add_review/<int:book_id>", methods=["POST"])
def add_review(book_id):
    if 'user_id' in session:
        user_id = session['user_id']
        rating = int(request.form['rating'])
        review_text = request.form['review']
        
        # Create a new Books_reviews object and add it to the database
        new_review = Books_reviews(book_id=book_id, user_id=user_id, rating=rating, reviews=review_text)
        db.session.add(new_review)
        db.session.commit()
        
    return redirect(url_for('book', book_id=book_id))

@app.route("/mybooks")
def mybooks():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        # Retrieve requested book IDs
        requested_books = User_req.query.filter_by(user_id=user_id).all()
        requested_book_ids = [requested.book_id for requested in requested_books]
        
        # Retrieve requested book details from Books table
        requested_book_details = Books.query.filter(Books.id.in_(requested_book_ids)).all()

        #auto revoke
        current_date = datetime.now().date()  # Get the current date
        # # Query for books issued to the user
        book_issued = Books_issued.query.filter_by(user_id=user_id).all()
        message = ''
        for book in book_issued:
            # Extract book access date and title
            access_date = book.access_date
            if access_date < current_date:
                # Find the corresponding book issuance record
                book_issue = Books_issued.query.filter_by(user_id=user_id, book_id=book.book_id).first()
                if book_issue:
                    # Delete the book issuance record
                    db.session.delete(book_issue)
                    db.session.commit()
                    # Append book title to message
        #             message += title + ', '
        # if message:
        #     message=message[:-2]+'where revoked'
        #     flash(message, 'success')
          
        # Retrieve issued books
        book_issued = Books_issued.query.filter_by(user_id=user_id).all()
        issued_book_ids = [issued.book_id for issued in book_issued]
        mybooks = Books.query.filter(Books.id.in_(issued_book_ids)).all()
        # Retrieve completed books
        completed_books = Books_completed.query.filter_by(user_id=user_id).all()
        completed_book_ids = [completed_book.book_id for completed_book in completed_books]
        # Group books by section
        books_by_section = defaultdict(list)
        for book in mybooks:
            books_by_section[book.section_id].append(book)
        
        # Fetch sections
        pc = Prime.query.filter_by(user_id=user_id).first()
        if pc:
            sections = Sections.query.all()
        else:
            sections = Sections.query.filter_by(prime='0').all()
        
        # Assign books to sections
        for section in sections:
            section.books = books_by_section[str(section.section_id)]
        favorite_books = Favorites.query.filter_by(user_id=user.id).all()
        
        return render_template('mybooks.html', sections=sections, user=user, requested_book_details=requested_book_details, completed_book_ids=completed_book_ids,book_issued=book_issued,favorite_books=favorite_books)
    else:
        # Handle case when user is not logged in
        flash('Please log in to access your books.', 'warning')
        return redirect(url_for('login'))

@app.route('/return_book', methods=['POST'])
def return_book():
    book_id = request.form.get('book_id')
    if book_id:
        # Remove the book from the Books_issued table
        Books_issued.query.filter_by(book_id=book_id).delete()
        db.session.commit()
        flash('Book returned successfully!', 'success')
    else:
        flash('Invalid book ID!', 'error')
    return redirect(url_for('mybooks'))

@app.route('/cancel_request', methods=['POST'])
def cancel_request():
    book_id = request.form.get('book_id')
    user_id = request.form.get('user_id')
    cr = User_req.query.filter_by(user_id=user_id, book_id=book_id).first()
    if cr:
        db.session.delete(cr)
        db.session.commit()  # Don't forget to commit the changes
        flash('Request deleted')
    return redirect(url_for('mybooks'))

@app.route("/add_book_as_completed/<int:book_id>", methods=['POST'])
def add_book_as_completed(book_id):
    book_id=book_id
    user_id=request.form.get('user_id')
    completed_book = Books_completed(user_id=user_id, book_id=book_id)
    db.session.add(completed_book)
    db.session.commit()
    flash('Book marked as completed')
    return redirect(url_for('mybooks'))

@app.route("/remove_from_completed/<int:book_id>", methods=['POST'])
def remove_from_completed(book_id):
    book_id=book_id
    user_id=request.form.get('user_id')
    completed_book = Books_completed.query.filter_by(user_id=user_id, book_id=book_id).first()
    if completed_book:
        db.session.delete(completed_book)
        db.session.commit()
        flash('Book removed from completed')
    return redirect(request.referrer or url_for('mybooks'))

@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    # Check if the user is logged in
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
    else:
        # Redirect to login if user is not logged in
        flash('Please log in to access your profile.', 'warning')
        return redirect(url_for('login'))
    issued_books=Books_issued.query.filter_by(user_id=user_id).all()

     # Fetch completed books
    completed_books = Books_completed.query.filter_by(user_id=user_id).all()
    section_counts = {}

    # Iterate over completed books to count books in each section
    for completed_book in completed_books:
        book = Books.query.get(completed_book.book_id)
        section_id = book.section_id
        if section_id in section_counts:
            section_counts[section_id] += 1
        else:
            section_counts[section_id] = 1

    # Fetch section names
    section_names = {}
    sections = Sections.query.all()
    for section in sections:
        section_names[section.section_id] = section.section

    data_list=[]
    for key1 in section_names:
        for key2 in section_counts:
            if int(key1)==int(key2):
                data_list.append([section_names[key1],section_counts[key2]])
    # Initialize forms
    update_form = UpdateProfileForm(obj=user)
    delete_form = DeleteAccountForm()
    
    if request.method == 'POST':
        if 'update-profile' in request.form:
            if update_form.validate_on_submit():
                # Update user profile
                user.name = update_form.name.data
                user.age = update_form.age.data
                db.session.commit()
                flash('Profile updated successfully.', 'success')
            else:
                flash('Profile update failed. Please check the form.', 'danger')
        
        elif 'delete-account' in request.form:
            if delete_form.validate_on_submit():
                # Delete user account
                # Perform necessary actions to delete user data
                # Redirect to logout or any other page after deletion
                flash('Account deleted successfully.', 'success')
                return redirect(url_for('logout'))
            else:
                flash('Account deletion failed. Please check the form.', 'danger')
    
    # Fetch user's favorite books and completed books
    favorite_books = Favorites.query.filter_by(user_id=user.id).all()
    favorite_books_details = []
    for favorite_book in favorite_books:
        book = Books.query.get(favorite_book.book_id)
        favorite_books_details.append({'id':book.id,'title': book.book_title,'author': book.author})
    
    completed_books = Books_completed.query.filter_by(user_id=user.id).all()
    completed_books_details= []
    for completed_book in completed_books:
        book = Books.query.get(completed_book.book_id)
        completed_books_details.append({'book_id':book.id,'title': book.book_title,'author': book.author})
    
    prime_check=False
    prime_req_check=False
    pc=Prime.query.filter_by(user_id=user_id).first()
    if pc:
        prime_check=True
    prc=Prime_req.query.filter_by(user_id=user_id).first()
    if prc:
        prime_req_check=True
    
    
    return render_template('User_profile.html', user=user, update_form=update_form,
                           delete_form=delete_form, favorite_books_details=favorite_books_details,
                           completed_books_details=completed_books_details,prime_check=prime_check,prime_req_check=prime_req_check,issued_books=issued_books,data_list=data_list)
                            # user_sections=user_sections)
@app.route('/add_favourite/<int:book_id>', methods=['POST'])
def add_favourite(book_id):
    # Get user ID from the form data
    user_id = request.form.get('user_id')
    
    # Check if the book is already in favorites for the user
    existing_favorite = Favorites.query.filter_by(user_id=user_id, book_id=book_id).first()
    
    # If the book is not already in favorites, add it
    if not existing_favorite:
        new_favorite = Favorites(user_id=user_id, book_id=book_id)
        db.session.add(new_favorite)
        db.session.commit()
        # flash('Book added to favorites successfully.')
    else:
        flash('Book is already in favorites.')

    # Redirect the user back to the previous page using referrer
    return redirect(request.referrer or url_for('mybooks'))

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    user_id=request.form.get('user_id')
    user=User.query.filter_by(id=user_id).first()
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            # Save the uploaded file to a directory on the server
            photo.save("static/"+photo.filename)

            user.user_img =  photo.filename
            db.session.commit()
            return redirect(url_for("user_profile"))
    flash( 'No file uploaded or invalid filename.')
@app.route("/subscribe/<int:id>",methods=['POST'])
def subscribe(id):
    user_id=id
    new_prime_req = Prime_req(user_id=user_id)
    db.session.add(new_prime_req)
    db.session.commit()
    return redirect(url_for("user_profile"))

@app.route("/unsubscribe/<int:id>",methods=['POST'])
def unsubscribe(id):
    user_id=id
    unsub=Prime.query.filter_by(user_id=user_id).first()
    if unsub:
        db.session.delete(unsub)
        db.session.commit()
    else:
        return "user not found"
    return redirect(url_for("user_profile"))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)

        # Retrieve form data
        name = request.form.get('name')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        # Check if the current password matches the one in the database
        if not user.check_password(current_password):
            flash('Incorrect current password.', 'danger')
            return redirect(url_for('user_profile'))

        # Update name if provided
        if name:
            user.name = name

        # Update password if provided
        if new_password:
            user.password = new_password

        # Commit changes to the database
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('user_profile'))
    else:
        flash('User session not found. Please log in.', 'danger')
        return redirect(url_for('login'))


@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    if 'user_id' in session:
        user_id = session['user_id']
        book_id = request.form['book_id']
        
        # Find the favorite record
        favorite_record = Favorites.query.filter_by(user_id=user_id, book_id=book_id).first()
        if favorite_record:
            # Delete the favorite record
            db.session.delete(favorite_record)
            db.session.commit()
            # flash('Book removed from favorites successfully.', 'success')
        else:
            flash('Book not found in favorites.', 'danger')
    else:
        flash('User session not found. Please log in.', 'danger')
    
    prev_page = request.referrer
    return redirect(prev_page)


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/lib")
def lib():
    return render_template("Lib.html")

@app.route("/admin")
def admin():
    return render_template("Admin.html")

@app.route("/register", methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    age = request.form.get('age')
    
    if username == '' or password == '':
        flash("Username or Password cannot be empty")
        return redirect(url_for('register'))

    if User.query.filter_by(username=username).first():
        flash('user with this username already exsists')
        return redirect(url_for('register'))
    user=User(username=username,password=password,name=name,age=age)
    db.session.add(user)
    db.session.commit()
    flash('User Successfully registered')
    return redirect(url_for('login'))

@app.route("/admin", methods=['POST'])
def admin1():
    admin_id = request.form.get('admin_id')
    passhash = request.form.get('password')
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    if not admin:
        flash("Admin doesnot exsist")
        return redirect(url_for('admin'))
    if not admin.check_password(passhash):
        flash("Incorrect Password")
        return redirect(url_for('admin'))
        # Successful login
    session['admin_id'] = admin.admin_id
    return redirect(url_for('admin_dashboard'))

@app.route("/admin_dashboard")
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin'))
    else:
        users=User.query.all()
        total_users = User.query.count()
        total_books = Books.query.count()
        librarians = Librarian.query.all()
        books = Books.query.all()
        total_sections=Sections.query.count()
        sections= Sections.query.all()
        return render_template('admin_dashboard.html',total_users=total_users, total_books=total_books, librarians=librarians,users=users, books=books,total_sections=total_sections,sections=sections)

@app.route('/prime_access')
def prime_access():
    prime_users = Prime.query.all()
    prime_req_users = Prime_req.query.all()

    prime_user_details = []
    prime_user_req_details = []

    # Fetch details of prime users
    for prime_user in prime_users:
        user = User.query.get(prime_user.user_id)
        prime_user_details.append({'user_id': user.id, 'username': user.username})

    # Fetch details of users requesting prime access
    for prime_user_req in prime_req_users:
        user = User.query.get(prime_user_req.user_id)
        prime_user_req_details.append({'user_id': user.id, 'username': user.username})

    return render_template('prime_access.html', prime_users_details=prime_user_details, prime_req_users_details=prime_user_req_details)

# Route to revoke access
@app.route('/revoke_access/<int:user_id>', methods=['POST'])
def revoke_access(user_id):
    prime_user = Prime.query.filter_by(user_id=user_id).first()
    if prime_user:
        db.session.delete(prime_user)
        db.session.commit()
    return redirect(url_for('prime_access'))

# Route to grant access
@app.route('/grant_access/<int:user_id>', methods=['POST'])
def grant_access(user_id):
    prime_req_user = Prime_req.query.filter_by(user_id=user_id).first()
    if prime_req_user:
        prime_user = Prime(user_id=user_id)
        db.session.add(prime_user)
        db.session.delete(prime_req_user)
        db.session.commit()
    return redirect(url_for('prime_access'))

@app.route("/create_librarian", methods=['POST'])
def create_librarian():
    lib_id = request.form.get('lib_id')
    lib_name = request.form.get('lib_name')
    lib_password = request.form.get('lib_password')
    
    if Librarian.query.filter_by(lib_id=lib_id).first():
        flash('Librarian with this ID already exists', 'error')
    else:
        new_librarian = Librarian(lib_id=lib_id, name=lib_name)
        new_librarian.password = lib_password
        db.session.add(new_librarian)
        db.session.commit()
        flash('Librarian created successfully', 'success')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/upload_photo_admin', methods=['POST'])
def upload_photo_admin():
    admin_id=request.form.get('admin_id')
    admin=Admin.query.filter_by(admin_id=admin_id).first()
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            # Save the uploaded file to a directory on the server
            photo.save("static/"+photo.filename)

            admin.admin_img =  photo.filename
            db.session.commit()
            return redirect(url_for("admin_profile"))
    flash( 'No file uploaded or invalid filename.')

@app.route('/admin_profile', methods=['GET', 'POST'])
def admin_profile():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        admin = Admin.query.get(admin_id)
        if request.method == 'POST':
            name = request.form.get('name')
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')

            if not admin.check_password(current_password):
                return "Current password is incorrect."

            admin.name = name
            if new_password:
                admin.password = new_password

            db.session.commit()
            return redirect(url_for('admin_profile'))

        return render_template('admin_profile.html', admin=admin)
    else:
        return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))  # Redirect to your login page

@app.route("/lib", methods=['POST'])
def libr():
    lib_id = request.form.get('lib_id')
    passhash = request.form.get('password')
    lib = Librarian.query.filter_by(lib_id=lib_id).first()
    if not lib:
        flash("Librarian doesnot exsist")
        return redirect(url_for('lib'))
    if not lib.check_password(passhash):
        flash("Incorrect Password")
        return redirect(url_for('lib'))
        # Successful login
    session['lib_id'] = lib.lib_id
    return redirect(url_for('librarian_dashboard'))

       
@app.route("/librarian_dashboard")
def librarian_dashboard():
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)

    sections = Sections.query.all()
    
    filter_type = request.args.get('filter_type')
    search_input = request.args.get('search_input')

    if filter_type == 'section' and search_input:
        sections = Sections.query.filter(Sections.section.ilike(f'%{search_input}%')).all()
        for section in sections:
            section.books = Books.query.filter_by(section_id=section.section_id).all()
        if search_input=="":
            flash("Please enter a search input.")
    elif filter_type == 'author' and search_input:
        filtered_books = Books.query.filter(Books.author.ilike(f'%{search_input}%')).all()
        # Filter sections to include only those that have filtered books
        sections_with_books = []
        for section in sections:
            section.books = Books.query.filter((Books.section_id == section.section_id) & (Books.id.in_([book.id for book in filtered_books]))).all()
            if section.books:
                section.books = section.books
                sections_with_books.append(section)
            sections = sections_with_books
        if search_input=="":
            flash("Please enter a search input.")

    elif filter_type == 'book' and search_input:
        filtered_books = Books.query.filter(Books.book_title.ilike(f'%{search_input}%')).all()
        # Filter sections to include only those that have filtered books
        sections_with_books = []
        for section in sections:
            section.books = Books.query.filter((Books.section_id == section.section_id) & (Books.id.in_([book.id for book in filtered_books]))).all()
            if section.books:
                section.books = section.books
                sections_with_books.append(section)
            sections = sections_with_books
        if search_input=="":
            flash("Please enter a search input.")

        
    else:
        # If no filter applied or search input is empty, load all sections and their books
        for section in sections:
            section.books = Books.query.filter_by(section_id=section.section_id).all()
    return render_template('Librarian_dashboard.html', sections=sections, lib=lib,filter_type=filter_type,search_input=search_input)

@app.route("/filter-and-search_lib", methods=['POST'])
def filter_and_search_lib():
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)
        
        session['referring_url'] = request.referrer
        
        # Retrieve form data
        filter_option = request.form['filter_option']
        search_query = request.form['search_query']
        
        # Filter books based on the selected option
        if filter_option == 'section':
            filtered_books = Books.query.filter_by(section_id=search_query).all()
        elif filter_option == 'book':
            filtered_books = Books.query.filter(Books.book_title.ilike(f'%{search_query}%')).all()
        else:
            filtered_books = []  # Handle invalid filter option
        
        # You can further process the filtered_books as needed
        
        # Convert filtered books data to a list of book IDs
        filtered_book_ids = [book.id for book in filtered_books]
        
        # Append filtered books data to the redirect URL as URL parameters
        
        # Redirect back to the referring URL with filtered books data
        return redirect(url_for('librarian_dashboard', filter_type=request.form['filter_option'], search_input=request.form['search_query']))
    else:
        # Handle case when user is not logged in
        flash('Please log in to access this feature.', 'warning')
        return redirect(url_for('login'))

@app.route('/upload_photo_book', methods=['POST'])
def upload_photo_book():
    book_id=request.form.get('book_id')
    book=Books.query.filter_by(id=book_id).first()
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            # Save the uploaded file to a directory on the server
            photo.save("static/"+photo.filename)

            book.book_cover =  photo.filename
            db.session.commit()
            return redirect(url_for("librarian_dashboard"))
    flash( 'No file uploaded or invalid filename.')

@app.route("/edit_book/<int:book_id>")
def edit_book(book_id):
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)    
    book = Books.query.filter_by(id=book_id).first()
    section = Sections.query.filter_by(section_id=book.section_id).first()
    sections=Sections.query.all()
    # Fetch the user_id associated with the review for this book
    user_id = None
    user_review = Books_reviews.query.filter_by(book_id=book_id).first()
    if user_review:
        user_id = user_review.user_id

    # Query the database to calculate the distribution of ratings
    ratings_distribution = db.session.query(
        Books_reviews.rating,
        db.func.count(Books_reviews.rating)
    ).filter_by(book_id=book_id).group_by(Books_reviews.rating).all()
    
    # Calculate the total number of ratings
    total_ratings = sum(count for _, count in ratings_distribution)

    # Calculate the percentage of ratings for each value
    ratings_percentage = {rating: (count / total_ratings) * 100 for rating, count in ratings_distribution}
    rating_percentage_list=[]
    for key in ratings_percentage:
        rating_percentage_list.append([key,ratings_percentage[key]])

    return render_template('edit_book.html', book=book, user_id=user_id, ratings_percentage=ratings_percentage,section=section,sections=sections,rating_percentage_list=rating_percentage_list)

@app.route("/update_book", methods=['POST'])
def update_book():
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)
        
        # Extract data from the form
        book_id = request.form.get('book_id')
        title = request.form.get('title')
        author = request.form.get('author')
        description = request.form.get('description')
        link = request.form.get('link')
        section_id = request.form.get('section_id')
        
        # Retrieve the book from the database
        book = Books.query.get(book_id)
        if book:
            # Update the book record
            book.book_title = title
            book.author = author
            book.description = description
            book.link = link
            book.section_id = section_id

            db.session.commit()
            flash('Book updated successfully.', 'success')
            return redirect(url_for('edit_book', book_id=book_id))
        else:
            flash('Book not found.', 'error')
            return redirect(url_for('edit_book', book_id=book_id))
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))

@app.route("/delete_review/<int:user_id>", methods=['POST'])
def delete_review(user_id):
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)

        if request.method == 'POST':
            # Assuming you have a way to determine the review_id based on user_id
            review = Books_reviews.query.filter_by(user_id=user_id).first()
            if review:
                db.session.delete(review)
                db.session.commit()
                flash('Review deleted successfully.', 'success')
                return redirect(url_for('edit_book', book_id=review.book_id))
            else:
                flash('Review not found.', 'error')
                return redirect(url_for('edit_book', book_id=review.book_id))
        else:
            flash('Invalid request method.', 'error')
            return redirect(url_for('edit_book', book_id=review.book_id))
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('login'))
@app.route("/add_book", methods=['GET', 'POST'])
def add_book():
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)
        
    sections = Sections.query.all()
    section_id = request.args.get('section_id')  # Retrieve section_id from query parameters
    
    return render_template("add_book.html", sections=sections, id=section_id)

@app.route("/submit_book", methods=['POST'])
def submit_book():
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)
    else:
        # Handle the case when no librarian is logged in
        flash('You must be logged in as a librarian to submit a book.', 'error')
        return redirect(url_for('login'))  # Redirect to the login page or any suitable route
    
    # Retrieve form data
    title = request.form.get('title')
    author = request.form.get('author')
    description = request.form.get('description')
    link = request.form.get('link')
    section_id = request.form.get('section')
    current_date = datetime.now().date()
    # Handle file upload
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            # Save the uploaded file to a directory on the server
            photoc = photo.filename
            photo.save(photoc)
        else:
            photoc = None
    else:
        photoc = None
    # Create a new Book object and add it to the database
    new_book = Books(
        book_title=title,
        author=author,
        description=description,
        link=link,
        section_id=section_id,
        added_by=lib_id,
        book_cover=photoc,
        date_added=current_date
    )
    db.session.add(new_book)
    db.session.commit()

    flash('Book added successfully.', 'success')
    return redirect(url_for('librarian_dashboard'))  # Redirect to the librarian dashboard
@app.route("/delete_book/<int:book_id>", methods=['GET','POST'])
def delete_book(book_id):
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)    
    book = Books.query.filter_by(id=book_id).first()
    if book:
        # Delete associated records from other tables
        Books_reviews.query.filter_by(book_id=book_id).delete()
        Books_completed.query.filter_by(book_id=book_id).delete()
        User_req.query.filter_by(book_id=book_id).delete()
        Books_issued.query.filter_by(book_id=book_id).delete()
        Favorites.query.filter_by(book_id=book_id).delete()
        
        # Delete the book itself
        db.session.delete(book)
        db.session.commit()    
        flash('Book deleted successfully.', 'success')
    return redirect(url_for("librarian_dashboard"))
# # Get the previous URL from the request
#     previous_page = request.referrer
#     # Redirect back to the previous page or to the default if previous_page is None
#     return redirect(previous_page or url_for("librarian_dashboard"))

@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    data_list = []  # Define data_list outside of the conditional block
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)
    sections = Sections.query.all()
    all_sections = Sections.query.all()

    books = Books.query.all()
    section_counts = {}
    for book in books:
        section_id = book.section_id
        if section_id in section_counts:
            section_counts[section_id] += 1
        else:
            section_counts[section_id] = 1
    # Fetch section names
    section_names = {}
    sections = Sections.query.all()
    for section in sections:
        section_names[section.section_id] = section.section

    # Populate data_list
    for key1 in section_names:
        for key2 in section_counts:
            if int(key1) == int(key2):
                data_list.append([section_names[key1], section_counts[key2]])

    if request.method == 'POST':
        # Retrieve form data
        section_name = request.form.get('section_name')
        description = request.form.get('description')
        section_type = request.form.get('type')
        current_date = datetime.now().date()
        # Check if all fields are filled
        if not (section_name and description and section_type):
            flash('All fields are required.', 'error')
            return redirect(url_for('librarian_dashboard'))  # Redirect to a suitable route

        # Create a new Section object and add it to the database
        new_section = Sections(
            section=section_name,
            description=description,
            added_by=lib_id,  # Assuming you have a current_user variable representing the currently logged-in user
            prime=(section_type == 'prime'),# Convert section_type to boolean
            date_added=current_date
        )
        db.session.add(new_section)
        db.session.commit()

        flash('Section added successfully.', 'success')
        return redirect(url_for('librarian_dashboard'))  # Redirect to a suitable route

    return render_template("add_section.html", sections=sections, all_sections=all_sections, data_list=data_list)


@app.route("/delete_section/<int:section_id>", methods=['POST'])
def delete_section(section_id):
    section = Sections.query.filter_by(section_id=section_id).first()
    if section:
        db.session.delete(section)
        db.session.commit()    
        books = Books.query.filter_by(section_id=section_id).all()
        for book in books:
            db.session.delete(book)
        db.session.commit()
    return redirect(url_for('add_section'))
@app.route("/edit_section/<int:section_id>", methods=['GET'])
def edit_section(section_id):
    section = Sections.query.filter_by(section_id=section_id).first()
    if section:    
        books = Books.query.filter_by(section_id=section_id).all()
    return render_template("edit_section.html",section=section,books=books)
@app.route("/update_section/<int:section_id>", methods=['POST'])
def update_section(section_id):
    if request.method == 'POST':
        # Retrieve form data
        section_name = request.form.get('section_name')
        description = request.form.get('description')
        section_type = request.form.get('type')

        # Find the section by ID
        section = Sections.query.get(section_id)
        if section:
            # Update the section details
            section.section = section_name
            section.description = description
            section.prime = (section_type == 'prime')
            
            # Commit changes to the database
            db.session.commit()
            flash('Section updated successfully.', 'success')
        else:
            flash('Section not found.', 'error')
        
    return redirect(url_for('librarian_dashboard'))  # Redirect to a suitable route

@app.route("/book_access")
def book_access():
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)
        
        # Join Books_issued and User tables to get user_id and username for issued books
        
        book_iss = db.session.query(Books_issued.book_id, User.id, User.username ).join(User, Books_issued.user_id == User.id).all()
        # Join User_req and User tables to get user_id and username for requested books
        book_req = db.session.query(User_req.book_id, User.id, User.username,User_req.days).join(User, User_req.user_id == User.id).all()
        return render_template("book_access.html", lib=lib, book_iss=book_iss, book_req=book_req)
    else:
        return redirect(url_for('lib')) 

@app.route("/grant_book_access", methods=["POST"])
def grant_book_access():
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)
    # Retrieve data from the form
    user_id = request.form.get("user_id")
    book_id = request.form.get("book_id")
    
    # Perform actions to delete the record from user_Req and add it to book_issued
    # Assuming you have corresponding models and methods to handle these actions
    user_request = User_req.query.filter_by(user_id=user_id, book_id=book_id).first()
    
    if user_request:
        days=user_request.days
        # Delete the record from user_Req
        db.session.delete(user_request)
        current_date = datetime.now().date()  # Get the current date
        new_date = current_date + timedelta(days=days)  # Add 1 day
    # Create a new record in book_issued
        new_issued_book = Books_issued(
            user_id=user_id,
            book_id=book_id,
            issued_by=lib_id,
            issue_date=current_date,
            access_date=new_date
            )
        db.session.add(new_issued_book)
    
    # Commit the changes to the database
        db.session.commit()
        flash('Access granted successfully.', 'success')
    else:
        flash('User request not found.', 'error')
    
    # Redirect back to the book_access page
    return redirect(url_for("book_access"))

@app.route("/discard_access", methods=["POST"])
def discard_access():
    # Retrieve data from the form
    user_id = request.form.get("user_id")
    book_id = request.form.get("book_id")
    user_request = User_req.query.filter_by(user_id=user_id, book_id=book_id).first()
    if user_request:
        # Delete the record from user_Req
        db.session.delete(user_request)
    # Commit the changes to the database
        db.session.commit()
        flash('Discarded successfully.', 'success')
    else:
        flash('User request not found.', 'error')
    
    # Redirect back to the book_access page
    return redirect(url_for("book_access"))
@app.route("/revoke_book_access", methods=["POST"])
def revoke_book_access():
    # Retrieve data from the form
    user_id = request.form.get("user_id")
    book_id = request.form.get("book_id")
    
    # Find all book issue records matching the user ID and book ID
    book_issues = Books_issued.query.filter_by(user_id=user_id, book_id=book_id).first()
    print
    if book_issues:
        # If records exist, delete them
        db.session.delete(book_issues)
        db.session.commit()
        flash('Access revoked successfully.', 'success')
    else:
        # If no records exist, flash an error message
        flash('No matching book access requests found.', 'error')
    
    # Redirect back to the book_access page
    return redirect(url_for("book_access"))
@app.route('/upload_photo_lib', methods=['POST'])
def upload_photo_lib():
    lib_id=request.form.get('lib_id')
    lib=Librarian.query.filter_by(lib_id=lib_id).first()
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            # Save the uploaded file to a directory on the server
            photo.save("static/"+photo.filename)

            lib.lib_img =  photo.filename
            db.session.commit()
            return redirect(url_for("lib_profile"))
    flash( 'No file uploaded or invalid filename.')

@app.route("/lib_profile")
def lib_profile():
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)
        all_sections=Sections.query.all()
        lib_sections=Sections.query.filter_by(added_by=lib_id).all()
        lib_books=Books.query.filter_by(added_by=lib_id).all()
        return render_template("lib_profile.html",lib=lib,all_sections=all_sections,lib_sections=lib_sections,lib_books=lib_books)

@app.route("/update_password", methods=['POST'])
def update_password():
    if 'lib_id' in session:
        lib_id = session['lib_id']
        lib = Librarian.query.get(lib_id)
        if lib:
            # Retrieve form data
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')

            # Check if the current password matches the stored password
            if lib.check_password(current_password):
                # Update the password if provided
                if new_password:
                    lib.password = new_password  # Use set_password method

                # Commit changes to the database
                db.session.commit()
                flash('Password updated successfully.', 'success')
            else:
                flash('Incorrect current password.', 'error')
        else:
            flash('Librarian not found.', 'error')
    
    return redirect(url_for("lib_profile"))
@app.route("/delete_account", methods=["POST"])
def delete_account():
    role=request.form.get('role')
    if role=='user':
        user_id = request.form.get('user_id')
        user = User.query.get(user_id)
        if user:
            # Delete the librarian record
            db.session.delete(user)
            db.session.commit()
            flash('account has been deleted.', 'success')
        else:
            flash('User not found.', 'error')

    elif role=='lib':
        lib_id=request.form.get('lib_id')
        lib = Librarian.query.get(lib_id)
        if lib:
            # Delete the librarian record
            db.session.delete(lib)
            db.session.commit()
            flash('account has been deleted.', 'success')
        else:
            flash('Librarian not found.', 'error')
    
    prev_page = request.referrer
    if not prev_page or prev_page == request.url or '/admin_dashboard' not in prev_page:
        return redirect(url_for('login'))
    else:
        return redirect(prev_page)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True,
        port=8080)
    