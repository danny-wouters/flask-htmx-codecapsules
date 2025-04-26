from app import app, db
from flask import render_template, request, redirect, url_for
from app.models import Author, Book, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if db.session.query(User).filter(User.username == username).first():
            return render_template("sign_up.html", error="Username is already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("sign_up.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        user = db.session.query(User).filter_by(username=username).first()
        print(user)
        print(user.username)

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/home", methods=["GET"])
@app.route("/", methods=["GET"])
@login_required
def home():
    books = db.session.query(Book, Author).filter(Book.author_id == Author.author_id).all()
    return render_template("index.html", books=books, username=current_user.username)

@app.route("/submit", methods=["POST"])
def submit():
    global_book_object = Book()

    title = request.form["title"]
    author_name = request.form["author"]

    author_exists = db.session.query(Author).filter(Author.name == author_name).first()
    # check if author already exists in db
    if author_exists:
        author_id = author_exists.author_id
        book = Book(author_id=author_id, title=title)
        db.session.add(book)
        db.session.commit()
        global_book_object = book
    else:
        author = Author(name=author_name)
        db.session.add(author)
        db.session.commit()

        book = Book(author_id=author.author_id, title=title)
        db.session.add(book)
        db.session.commit()
        global_book_object = book

    response = f"""
    <tr>
        <td>{title}</td>
        <td>{author_name}</td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-edit-form/{global_book_object.book_id}">
                Edit Title
            </button>
        </td>
        <td>
            <button class="btn btn-primary"
                hx-delete="/delete/{global_book_object.book_id}">
                Delete
            </button>
        </td>
    </tr>
    """
    return response

@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_book(id):
    book = Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return ""

@app.route("/get-edit-form/<int:id>", methods=["GET"])
def get_edit_form(id):
    book = Book.query.get(id)
    author = Author.query.get(book.author_id)

    response = f"""
    <tr hx-trigger="cancel" class="editing" hx-get="/get-book-row/{id}">
        <td><input name="title" value="{book.title}"/></td>
        <td>{author.name}</td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-book-row/{id}">
                Cancel
            </button>
            <button class="btn btn-primary"
                hx-put="/update/{id}" hx-include="closest tr">
                Save
            </button>
        </td>
    </tr>
    """
    return response

@app.route("/get-book-row/<int:id>", methods=["GET"])
def get_book_row(id):
    book = Book.query.get(id)
    author = Author.query.get(book.author_id)

    response = f"""
    <tr>
        <td>{book.title}</td>
        <td>{author.name}</td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-edit-form/{id}">
                Edit Title
            </button>
        </td>
        <td>
            <button class="btn btn-primary"
                hx-delete="/delete/{id}">
                Delete
            </button>
        </td>
    </tr>
    """
    return response

@app.route("/update/<int:id>", methods=["PUT"])
def update_book(id):
    title = request.form["title"]
    book = Book.query.get(id)
    author = Author.query.get(book.author_id)

    db.session.query(Book).filter(Book.book_id == id).update({"title": title})
    db.session.commit()

    response = f"""
    <tr>
        <td>{title}</td>
        <td>{author.name}</td>
        <td>
            <button class="btn btn-primary"
                hx-get="/get-edit-form/{id}">
                Edit Title
            </button>
        </td>
        <td>
            <button class="btn btn-primary"
                hx-delte="/delete/{id}">
                Delete
            </button>
        </td>
    </tr>
    """
    return response
