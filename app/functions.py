import os
import ffmpeg
import random
from flask import request, redirect, url_for, flash, current_app, render_template
from flask_login import login_user, logout_user, current_user
from sqlalchemy.inspection import inspect
from datetime import datetime, timezone
from functools import wraps
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from mvola import Mvola
from mvola.tools import Transaction
from .static.model.model import Video, Category, image, module, User, Video_buy
from PIL import Image
from . import db, mail
from itsdangerous import URLSafeSerializer
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_mail import Message
from time import sleep
import uuid

dotevent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static/app.env'))
load_dotenv(dotevent_path)
secret_key = 'a537db731f47686adff47985249e2481d8931aa32e1e1a722649adb66d2d0f8f'
serializer = URLSafeSerializer(secret_key)

# Paths to ffmpeg and ffprobe binaries
FFMPEG_BIN = os.path.abspath('app/static/outils/ffempg/ffmpeg')
FFPROBE_BIN = os.path.abspath('app/static/outils/ffempg/ffprobe')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

def nombre_recherche(model_class, column_name, value):
    if not hasattr(model_class, column_name):
        raise ValueError("colone non trouvé")
    
    count = db.session.query(db.func.count(getattr(model_class, column_name))).filter(getattr(model_class, column_name) == value).scalar() 
    return count

def generate_correlation_id():
    random_hex = ''.join(random.choices('0123456789abcdef', k=32))
    return f"{random_hex[:8]}-{random_hex[8:12]}-{random_hex[12:16]}-{random_hex[16:20]}-{random_hex[20:]}"

def send_Mail(subject, recipient, html):
    msg = Message( subject=subject, recipients=[recipient])
    msg.html = html
    with current_app.app_context():
        mail.send(msg)

def register(form):
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
       
        if existing_user:
            flash('Cet mail est déja utilisé.', 'danger')
            return redirect(url_for('main.add_register'))

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            activate=0,
            type='user'
        )
        db.session.add(new_user)
        db.session.commit()
        user_id = new_user.id
        encoded_id = encode(user_id)
        subject = "Inscription de " + form.username.data + " à la plateforme Eray learning"
        recipient = form.email.data
        html = render_template('email_template.html', recipient=encoded_id, username = form.username.data)
        try:
            send_Mail(subject, recipient, html)
            return True
        except Exception as e:
            db.session.rollback()
            return None
    return None

def load_user(user_id):
    return User.query.get(int(user_id))

def custom_login_user(email, password, remember=None):
    user = User.query.filter_by(email=email).first()
    if user.activate == 1:
        if user and user.check_passord(password):
            login_user(user, remember=bool(remember))
            return True
        return False
    return False

def custom_logout_user():
    logout_user()

def forgot_password(email):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        encoded_id = encode(existing_user.id)
        subject = "Initialisation de mot de passe de " + existing_user.username + " à la plateforme Eray learning"
        recipient = existing_user.email
        html = render_template('forgot_password.html', recipient=encoded_id, username = existing_user.username)
        try:
            send_Mail(subject, recipient, html)
            return True
        except Exception as e:
            return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.type != 'admin':
            flash("vous n'avez pas la permission nécessaires pour accéder à cette page", "error")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.type != 'user':
            flash("vous n'avez pas la permission nécessaires pour accéder à cette page", "error")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated_function

def redirect_email(email):
    domain = email.split('@')[-1]
    if domain == 'gmail.com':
        url = "https://mail.google.com"
        return url
    elif domain == 'yahoo.com':
        url = "https://www.yahoo.com"
        return url
    else:
        return url_for('main.redirection')

def activate_account_by_id(decoded_id):
    recherche = query_ligne(decoded_id, 'User')
    if recherche:
        recherche.activate = 1
        db.session.commit()
        return decoded_id

def get_current_time():
    # Générer l'heure actuelle en UTC au format requis
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def encode(variable_brut):
    return serializer.dumps(str(variable_brut))

def decode(variable_encoded):
    return int(serializer.loads(variable_encoded))

def generate_key(idkey):
    key = Fernet.generate_key()
    key_folder = os.path.join('app', 'variable', 'video', f'{idkey}', 'key')
    os.makedirs(key_folder, exist_ok=True)
    key_file_path = os.path.join(key_folder, 'enc.key')
    with open(key_file_path, 'wb') as key_file:
        key_file.write(key)
    return key_file_path, key.decode()

def convert_video(input_file, idC):
    output_folder = os.path.join('app', 'variable', 'video', f'{idC}')
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, os.path.splitext(os.path.basename(input_file))[0] + '.m3u8')
    key_file_path, key_string = generate_key(idC)
    key_uri = f'http://127.0.0.1:5000/{idC}/key/enc.key'  # A changé pendant le déployement
    key_info_dir = os.path.join('app', 'variable', 'video', f'{idC}', 'key','key_info.txt')
    with open(key_info_dir, 'w') as ki:
        ki.write(f"{key_uri}\n{key_file_path}\n")
    try:
        (
            ffmpeg
            .input(input_file)
            .output(output_file, format='hls', 
                    hls_time=3,
                    hls_list_size=0,
                    hls_playlist_type='vod',
                    hls_key_info_file= key_info_dir)
            .run(cmd=FFMPEG_BIN)
        )
        return output_file
    except Exception as e:
        print(f"Error during conversion: {e}")
        return None
def handle_upload():
    if 'video_file' not in request.files:
        return None
    video_file = request.files['video_file']
    image_file = request.files['image_video']
    if video_file.filename == '' or image_file == '' or (video_file.filename == '' and image_file == ''):
        return None
    video_name = video_file.filename
    name_image_file = image_file.filename
    new_filename = str(uuid.uuid4())
    temp_path = os.path.join('app/temp', new_filename)
    os.makedirs('app/temp', exist_ok=True)
    video_file.save(temp_path)
    new_module_id = request.form.get('module')
    output_path_image = upload_image(image_file, name_image_file)
    new_video = Video(filename=new_filename, id_module=new_module_id, original_namefile=video_name, id_image_video=output_path_image)
    try:
        db.session.add(new_video)
        db.session.commit()
        video_id = new_video.id
        output_path = convert_video(temp_path, video_id)
        if output_path:
            os.remove(temp_path)
            return output_path
    except Exception as e:
        print(f"Erreur lors de l'enregistrement dans la base de données : {e}")
        db.session.rollback()
        os.remove(temp_path)
    return None
#Photo

def compress_image(input_image, output_image_path, quality=85, max_width=800):
    img = Image.open(input_image)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width /float(img.width)
        new_height = int((float(img.height) * float(ratio)))
        img = img.resize((max_width, new_height), Image.ANTIALIAS)
    img.save(output_image_path, "JPEG", quality=quality)
    return output_image_path

def upload_image(input_image_file, name_file):
    new_image_filename = str(uuid.uuid4()) + os.path.splitext(name_file)[1]
    temp_path = os.path.join('app/temp', new_image_filename)
    os.makedirs('app/temp', exist_ok=True)
    input_image_file.save(temp_path)
    new_image = image(image_filename=new_image_filename, image_original_name=name_file)
    try:
        db.session.add(new_image)
        db.session.commit()
        image_id = new_image.id
        output_image_path = os.path.join('app', 'variable', 'image', f'{image_id}')
        os.makedirs(output_image_path, exist_ok=True)
        output_file_path = os.path.join(output_image_path, f'{new_image_filename}')
        output_path = compress_image(temp_path, output_file_path)
        if output_path:
            os.remove(temp_path)
            return image_id
    except Exception as e:
        print(f"Erreur lors de l'enregistrement dans la base de données : {e}")
        db.session.rollback()
        os.remove(temp_path)

    return None

def category_insertion():
    if 'image_category' not in request.files:
        return "Aucun fichier n'a été télechargé", 404
    image_file = request.files['image_category']
    namefile_image = image_file.filename
    name_category = request.form.get('name_category')
    if namefile_image == '':
        return "Le nom du ficher est vide", 404
    output_category_name = upload_image(image_file, namefile_image)
    if not output_category_name:
        return "Ereur du fonction upload_image"
    new_category = Category(category_name=name_category, image_id=output_category_name)
    try:
        db.session.add(new_category)
        db.session.commit()
        return output_category_name
    except Exception as e:
        print(f"Erreur lors de l'enregistrement dans la base de données : {e}")
    return None

#creation de module

def module_insertion():

    if 'image_module' not in request.files:
        return "Aucun fichier n'a été télechargé", 404
    image_file = request.files['image_module']
    namefile_image = image_file.filename
    name_module = request.form.get('name_module')
    prix = request.form.get('prix') 
    description_module = request.form.get('description_module')
    id_category = request.form.get('category')
    if namefile_image == '':
        return "Le nom du ficher est vide", 404
    output_module_name = upload_image(image_file, namefile_image)
    if not output_module_name:
        return "Ereur du fonction upload_image"
    new_module = module(name_module=name_module, description_module=description_module, id_image_module=output_module_name, id_category=id_category, prix=prix)
    try:
        db.session.add(new_module)
        db.session.commit()
        return output_module_name
    except Exception as e:
        print(f"Erreur lors de l'enregistrement dans la base de données : {e}")
    return None
#impression de la base de donné

def show(db_name):
    try:
        if db_name == 'Category':
            tableau_result = Category.query.all()
        elif db_name == 'Video':
            tableau_result = Video.query.all()
        elif db_name == 'image':
            tableau_result = Image.query.all()
        elif db_name == 'module':
            tableau_result = module.query.all()
        elif db_name == 'User':
            tableau_result = User.query.all()
        elif db_name == 'Video_buy':
            tableau_result = Video_buy.query.all()
            #ajoute des model.db selon dans model.py
        else:
            print(f"Le model '{db_name}' table n'existe pas dans la base de donné")
            return []
        for tableau in tableau_result:
            tableau.encoded_id = encode(tableau.id)
        return tableau_result
    except Exception as e:
        print(f"Erreur d'execution du la fonction show")
        return []

#recherche specifique
#retourne liste
def match(value, table_name, colone_name):
    try:
        if table_name == 'Category':
            result_cherche = Category.query.filter(getattr(Category, colone_name) == value).all()
        elif table_name == 'Video':
            result_cherche = Video.query.filter(getattr(Video, colone_name) == value).all()
        elif table_name == 'image':
            result_cherche = image.query.filter(getattr(image, colone_name) == value).all()
        elif table_name == 'module':
            result_cherche = module.query.filter(getattr(module, colone_name) == value).all()
        elif table_name == 'User':
            result_cherche = User.query.filter(getattr(User, colone_name) == value).all()
        elif table_name == 'Video_buy':
            result_cherche = Video_buy.query.filter(getattr(Video_buy, colone_name) == value).all()
        
        for result_recherches in result_cherche:
            result_recherches.encoded_id = encode(result_recherches.id)
        return result_cherche

    except Exception as e:
        return ":{e}", 400
    
    #retourne objet
def match_objet(table_name, param_name ,param_value):
    try:
        if table_name == 'Video':
            result_cherche = Video.query.filter_by(**{param_name:param_value}).first()
            result_cherche.encoded_id = encode(result_cherche.id)
            return result_cherche
    except Exception as e:
        return ":{e}", 400
#retourne Objet

def query_ligne(id_match, table_name):
    try:
        if table_name == 'Category':
            result_cherche = Category.query.get(id_match)
        elif table_name == 'Video':
            result_cherche = Video.query.get(id_match)
        elif table_name == 'image':
            result_cherche = image.query.get(id_match)
        elif table_name == 'module':
            result_cherche = module.query.get(id_match)
        elif table_name == 'User':
            result_cherche = User.query.get(id_match)
        elif table_name == 'Video_buy':
            result_cherche = Video_buy.query.get(id_match)

        return result_cherche

    except Exception as e:
        return "{str(e)}", 400
#selection deux facteur reponse boleans
def selection_deux_facteur(table_name, id_1, id_2):
    if table_name == "video":
        result = Video_buy.query.filter_by(id_user=id_1, id_module=id_2).first()
    return result is not None

def get_entities_with_image(table_name, search_criteria):
    model_mapping = {
        'module': module,
        'video': Video,
    }

    model_class = model_mapping.get(table_name)

    if not model_class:
        return None

    # Requête pour récupérer les entités et les images associées
    results = db.session.query(model_class, image).filter(
        model_class.name_module.like(f"%{search_criteria}%")
    ).outerjoin(image, model_class.id_image_module == image.id).all()

    if results:
        combined_results = []
        for entity, images in results:
            # Accéder aux colonnes de l'entité et de l'image
            entity_data = {f"entity_{key}": value for key, value in entity.__dict__.items()}
            image_data = {f"image_{key}": value for key, value in images.__dict__.items() if images} if images else {}

            # Supprimer les clés SQLAlchemy internes
            entity_data.pop('entity__sa_instance_state', None)
            image_data.pop('image__sa_instance_state', None)

            # Fusionner les deux dictionnaires avec les préfixes pour éviter l'écrasement
            combined_data = {**entity_data, **image_data}
            combined_results.append(combined_data)

        return combined_results
    else:
        return []

def initiate_transaction(user_account_identifier, partner_name, amount, credit, debit, x_callback_url, currency="Ar", description_text="Transaction_1"):
    api = Mvola(os.getenv('CUNSUMER_KEY'), os.getenv('SECRET_KEYS'), status="SANDBOX")

    # Vérification des paramètres requis

    # Validation de la description
    if len(description_text) > 50:
        print("Erreur : la description doit contenir au maximum 50 caractères.")
        return None

    invalid_chars = set('!@#$%^&*()+=[]{}|;:<>?/~` ')
    if any(char in invalid_chars for char in description_text):
        print("Erreur : la description contient des caractères non autorisés.")
        return None

    # Validation du user_account_identifier
    if not user_account_identifier.startswith("034") or len(user_account_identifier) != 10:
        print("Erreur : user_account_identifier doit commencer par '034' et faire 10 chiffres.")
        return None

    # Générer le token d'accès
    token_response = api.generate_token()

    # Débogage pour le token_response
    print("Token Response:", token_response)

    if isinstance(token_response, str):
        print("Erreur : Réponse inattendue lors de la génération du token:", token_response)
        return None

    if hasattr(token_response, 'Error') and token_response.Error:
        print(f"Erreur lors de la génération du token: {token_response.Error}")
        return None

    # Accéder au token d'accès
    if token_response.success:
        api.token = token_response.response
        tokenify = api.token
    # Préparer la transaction
    transaction = Transaction(
        token=tokenify,
        user_language="FR",
        user_account_identifier=user_account_identifier,
        partner_name=partner_name,
        x_callback_url=x_callback_url,
        amount=amount,
        currency=currency,
        original_transaction_reference="original",
        requesting_organisation_transaction_reference="ozcbajq",
        description_text="fevvs",
        request_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.999Z"),
        debit=debit,
        credit=credit,
    )

    # Initialiser la transaction
    transaction_response = api.init_transaction(transaction)

    # Débogage pour le transaction_response
    print("Transaction Response:", transaction_response)

    if isinstance(transaction_response, str):
        print("Erreur : Réponse inattendue lors de l'initiation de la transaction:", transaction_response)
        return None

    if hasattr(transaction_response, 'Error') and transaction_response.Error:
        print(f"Erreur lors de l'initiation de la transaction: {transaction_response.Error}")
        return None
    
    if transaction_response:
        status = transaction_response.response['status']

    return status

def insertion_achat(id_user, id_module):
    new_buy = Video_buy(id_user=id_user, id_module=id_module)
    try:
        db.session.add(new_buy)
        db.session.commit()

        return True
    except Exception as e:
        print(f"Erreur lors de l'enregistrement dans la base de données : {e}")
        db.session.rollback()
    return False