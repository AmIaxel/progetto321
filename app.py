from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session

app = Flask(
    __name__,
    template_folder='C:/Users/Axel/OneDrive - edu.ti.ch/Desktop/Progetto321/api/templates',
    static_folder='C:/Users/Axel/OneDrive - edu.ti.ch/Desktop/Progetto321/api/static'
)

# Configurazione del database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/flask_project'
app.config['SECRET_KEY'] = 'supersegreto123'

# Configurazione delle sessioni
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

db = SQLAlchemy(app)


class Courses(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Lunghezza aumentata a 255

    def __repr__(self):
        return f'<User {self.username}>'


@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    return render_template('main.html', username=session.get('username'))


@app.route('/courses')
def courses():
    if 'user_id' not in session:
        flash("Devi effettuare il login per accedere ai corsi.", "danger")
        return redirect(url_for('login'))
    
    try:
        allCourses = Courses.query.all()
        return render_template('courses.html', courses=allCourses, username=session.get('username'))
    except Exception as e:
        return f"Errore durante il recupero dei corsi: {e}"


@app.route('/about')
def about():
    return render_template('about.html', username=session.get('username'))


@app.route('/contact')
def contact():
    return render_template('contact.html', username=session.get('username'))




@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:  # Se già loggato, redirect alla home
        flash("Sei già loggato!", "info")
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Benvenuto {user.username}! Login effettuato con successo.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Credenziali errate. Riprova.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        print(f"🔍 Tentativo di registrazione: {username}, {email}")

        if User.query.filter((User.username == username) | (User.email == email)).first():
            print("⚠️ Username o email già registrati!")  
            flash('Username o Email già registrati.', 'warning')
            return redirect(url_for('register'))

        if len(password) < 6:
            print("⚠️ Password troppo corta!")
            flash('La password deve avere almeno 6 caratteri.', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        new_user = User(username=username, email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            print("✅ Registrazione avvenuta con successo!")
            flash('Registrazione completata! Ora puoi accedere.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            print(f"❌ Errore durante la registrazione: {str(e)}")
            flash(f'Errore durante la registrazione: {str(e)}', 'danger')

    return render_template('register.html')

@app.route('/send_contact', methods=['POST'])
def send_contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Per ora stampiamo nel terminale
    print(f"📩 Nuovo messaggio da {name} ({email}): {message}")

    flash('Messaggio inviato con successo! Ti risponderemo il prima possibile.', 'success')
    return redirect(url_for('contact'))

@app.route('/add_to_cart/<int:course_id>', methods=['POST'])
def add_to_cart(course_id):
    if 'user_id' not in session:
        flash("Devi essere loggato per aggiungere corsi al carrello.", "warning")
        return redirect(url_for('login'))

    # Se il carrello non esiste ancora, lo creiamo
    if 'cart' not in session:
        session['cart'] = []

    # Se non è già stato aggiunto, aggiungilo
    if course_id not in session['cart']:
        session['cart'].append(course_id)
        session.modified = True  # Per assicurarsi che Flask salvi i cambiamenti
        flash("Corso aggiunto al carrello!", "success")
    else:
        flash("Questo corso è già nel tuo carrello.", "info")

    return redirect(url_for('courses'))


@app.route('/logout')
def logout():
    session.clear()  # Rimuove tutti i dati della sessione
    flash("Logout effettuato con successo.", "info")
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
