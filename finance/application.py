from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from datetime import date, datetime

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    profile = db.execute("SELECT * FROM profile WHERE id = :id", id = session["user_id"])
    
    user = db.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])
    return render_template("index.html", profile = profile, users = user)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "GET":
        return render_template("buy.html")
    if request.method == "POST":
        symbol = request.form["symbol"]
        shares = request.form["shares"]
        quote = lookup(symbol)
        
        if not quote:
            return apology("Invalid Symbol")
        tot_price = float(quote.get('price')) * int(shares)
        rows = db.execute("SELECT username FROM users WHERE id = :id", id=session["user_id"])
        cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
        if not cash[0]["cash"] > tot_price:
            return apology("not enough money")
        result2 = db.execute("INSERT INTO history (id, username, company, shares, value, date) VALUES(:id, :username, :symbol, :shares, :value, :date )", username = rows[0].get('username'), shares = shares, symbol = quote.get('symbol'),  id = session["user_id"], value = quote.get('price'), date = str(date.today()))

        exists = db.execute("SELECT company FROM profile WHERE id = :id", id = session["user_id"])
        if  exists:   
            if  exists[0]['company'] != quote.get('name'):
               result = db.execute("INSERT INTO profile (id, username, company, shares, value, date, symbol, one_value) VALUES(:id, :username, :company, :shares, :value, :date, :symbol, :one_value )", username = rows[0].get('username'), shares = shares, company = quote.get('name'),  id = session["user_id"], value =tot_price, date = str(date.today()), symbol = quote.get('symbol'), one_value = quote.get('price'))
               new_cash = cash[0].get('cash') - tot_price
               ne = db.execute("UPDATE users SET cash= :cash WHERE id= :id", cash = new_cash, id = session["user_id"])
        
            else:    
              values = db.execute("SELECT * FROM profile WHERE id = :id", id = session["user_id"])
              result = db.execute("UPDATE profile SET shares = :tot_shares, value = :tot_value WHERE symbol = :symbol", tot_shares = int (shares) + int(values[0].get('shares')), tot_value =tot_price + values[0].get('value') , symbol = quote.get('symbol'))
        else:
               result = db.execute("INSERT INTO profile (id, username, company, shares, value, date, symbol, one_value) VALUES(:id, :username, :company, :shares, :value, :date, :symbol, :one_value )", username = rows[0].get('username'), shares = shares, company = quote.get('name'),  id = session["user_id"], value = tot_price, date = str(date.today()), symbol = quote.get('symbol'), one_value = quote.get('price'))
               new_cash = cash[0].get('cash') - tot_price
               ne = db.execute("UPDATE users SET cash= :cash WHERE id= :id", cash = new_cash, id = session["user_id"])
        
           
    return  redirect(url_for("index"))    


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    history = db.execute("SELECT * from history WHERE id=:id", id=session["user_id"])
    
    return render_template("history.html", history = history)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    if request.method == "POST":
        symbol = request.form['symbol']
        quote = lookup(symbol)
        if quote != None:
            return render_template("quoted.html", quote = quote)
        else:
            return apology("Invalid Symbol")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    if request.method == "GET":
        return render_template('register.html')
        
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['password_confirm']
        
        if len(username) < 1:
            return apology("Please Enter a Username")
            
        if password == confirm:
            hashed_password =  pwd_context.encrypt(password)
            result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username = username, hash = hashed_password)
            
            if not result:
                return apology("Username is already registered")
            
            session["user_id"] = result
            return redirect(url_for("index"))
        
        
        else:
            return apology("Passwords are different")
            
    
    

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "GET":
        return render_template('sell.html')
        
    if request.method == "POST":
        symbol = request.form['symbol']
        shares = request.form['shares']
        stock = lookup(symbol)
        
        if not stock:
            return apology('Invalid symbol')
            
        user_shares = db.execute("SELECT shares FROM profile \
                                 WHERE id = :id AND symbol=:symbol", \
                                 id=session["user_id"], symbol=stock["symbol"])
        if not user_shares or int(user_shares[0]["shares"]) < int(shares):
            return apology("Not enough shares")
    db.execute("INSERT INTO history (company, shares, value, id, date) \
                    VALUES(:symbol, :shares, :price, :id, :date)", \
                    symbol=stock["symbol"], shares=-int(shares), \
                    price=stock["price"], id=session["user_id"], date = str(date.today())) 
    db.execute("UPDATE users SET cash = cash + :purchase WHERE id = :id", \
                    id=session["user_id"], \
                    purchase=stock["price"] * float(shares))
    
    shares_total = user_shares[0]["shares"] - int(shares)
    if shares_total == 0:
            db.execute("DELETE FROM profile \
                        WHERE id=:id AND symbol=:symbol", \
                        id=session["user_id"], \
                        symbol=stock["symbol"])
    
    else:
            db.execute("UPDATE profile SET shares=:shares \
                    WHERE id=:id AND symbol=:symbol", \
                    shares=shares_total, id=session["user_id"], \
                    symbol=stock["symbol"])
    
    return redirect(url_for("index"))                

@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    """ change user password."""
    if request.method == "GET":
        return render_template('change.html')
        
    if request.method == "POST":
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm = request.form['confirm']
        result = db.execute("SELECT * FROM users WHERE id = :id", id = session["user_id"])
        if not new_password == confirm:
            return apology("Different Passwords")
        elif not pwd_context.verify(old_password, result[0]["hash"]):
            return apology("Wrong Password")
        else:
            result = db.execute("UPDATE users SET hash = :hash", hash = pwd_context.encrypt(new_password))
    return redirect(url_for("index"))      