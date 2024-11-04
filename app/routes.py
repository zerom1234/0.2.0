from flask import Blueprint, render_template, send_from_directory, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .functions import get_current_time, handle_upload, category_insertion, show, module_insertion, match, encode,decode, query_ligne, initiate_transaction, RegistrationForm ,register, redirect_email, activate_account_by_id, custom_login_user, custom_logout_user, admin_required, user_required, selection_deux_facteur, match_objet, insertion_achat, get_entities_with_image, nombre_recherche
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    current_time = get_current_time()
    categorie = show('Category')
    module = show('module')

    if current_user.is_authenticated:
        username = current_user.username
        type = current_user.type
        if type == 'admin':
            return render_template('dashboard.html', time=current_time)
        if type == 'user':
            return render_template('index.html', time=current_time, categorie=categorie, module=module, username=username)
    else: 
        return render_template('index.html', time=current_time, categorie=categorie, module=module)
    
@main.route('/video_player', methods=['GET'])
@login_required
@user_required
def video():
    video_encoded_id = request.args.get('id')
    id_decoded = decode(video_encoded_id)
    result = query_ligne(id_decoded, 'Video')
    id = result.id
    namefile = result.filename
    return render_template('video.html', id=id, namefile=namefile)

@main.route('/show_module', methods=['GET'])
@login_required
@user_required
def show_video():
    video_encoded_id = request.args.get('id')
    id_decoded = decode(video_encoded_id)
    id_user = current_user.id
    result = match(id_decoded, 'Video', 'id_module')
    result_object = match_objet('Video', 'id_module', id_decoded)
    id = result_object.id
    namefile = result_object.filename
    id_encoded = result_object.encoded_id
    if selection_deux_facteur('video', id_user, id_decoded) == True:
        return render_template('show_module.html', result=result, video_encoded_id=video_encoded_id, id=id, namefile=namefile)
    else:
        return render_template('show_module.html', result=result, id=id, namefile=namefile, id_encoded=id_encoded)

@main.route('/show_category', methods=['GET'])
@login_required
@user_required
def show_module():
    module_encoded_id = request.args.get('id')
    id_decoded = decode(module_encoded_id)
    result = match(id_decoded, 'module', 'id_category')
    return render_template('show_category.html', result=result)

@main.route('/upload_video')
@login_required
@admin_required
def uploads_video():
    module = show('module')
    return render_template('upload_video.html',  module=module)

@main.route('/create_module')
@login_required
@admin_required
def create_module():
    categorie = show('Category')
    return render_template('add_module.html', categorie=categorie)

@main.route('/create_category')
@login_required
@admin_required
def create_category():
    return render_template('add_category.html')

#test foutsiny azo fafana rehefa vita test
@main.route('/test')
@login_required
def test():
    status = initiate_transaction("0342128276", "Myapp", 2000, "0340350732", "0342128276", "https://ecf3-154-126-56-89.ngrok-free.app/test")
    return render_template('test.html')

@main.route('/test2')
@login_required
def test2():
    count = nombre_recherche('User', 'id', 1)
    return render_template('test.html', count=count)

@main.route('/register', methods=['GET', 'POST'])
def add_register():
    form = RegistrationForm()
    result = register(form)
    if result is True:
        email = form.email.data
        redirect_url = redirect_email(email)
        return redirect(redirect_url)
    if result is False:
        return redirect(url_for('main.add_register'))
    return render_template('register.html', title='Inscription', form=form)

@main.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')
        response = custom_login_user(email, password, remember)
        if response == True:
            return redirect(url_for('main.home'))
        elif response == False:
            flash('Votre compte dois être activé, accedé a votre email est activé votre compte.')
            return render_template('login.html')
        else:
            flash('Login failed.')
            return render_template('login.html')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    custom_logout_user()
    return redirect(url_for('main.home'))

@main.route('/redirection', )
def redirection():
    return render_template('redirection.html')

@main.route('/payement', methods=['GET'])
@login_required
def payement():
    id_brut = current_user.id
    id = encode(id_brut)
    id_video_encoded = request.args.get('id')
    id_video_decoded = decode(id_video_encoded)
    result = query_ligne(id_video_decoded, 'Video')
    id_module = result.id_module
    result_module = query_ligne(id_module, 'module')
    id_modules_brute = result_module.id
    id_modules = encode(id_modules_brute)
    name_module = result_module.name_module
    description_module = result_module.description_module
    prix_module = result_module.prix
    id_image_module = result_module.id_image_module
    result_image = query_ligne(id_image_module, 'image')
    id_image = result_image.id
    image_name = result_image.image_filename
    return render_template('payement.html', id=id, id_modules=id_modules, name_module=name_module, description_module=description_module,prix_module=prix_module, id_image_module=id_image_module, id_image=id_image, image_name=image_name )
    
@main.route('/activate', methods=['GET'])
def activate_account():
    encoded_id = request.args.get('id')
    decoded_id = decode(encoded_id)
    response = activate_account_by_id(decoded_id)
    if response:
        return render_template('activation.html')

@main.route('/video/<int:folder_id>/<path:filename>')
def serve_video(folder_id ,filename):
    variable_folder = os.path.abspath(f'app/variable/video/{folder_id}') #à réglé
    return send_from_directory(variable_folder, filename)

@main.route('/image/<int:folder_id>/<path:filename>')
def serve_image(folder_id ,filename):
    variable_folder = os.path.abspath(f'app/variable/image/{folder_id}') #à réglé
    return send_from_directory(variable_folder, filename)

@main.route('/<int:folder_id>/key/<filename>')
def serve_key( folder_id, filename):
    variable_key = os.path.abspath(f'app/variable/video/{folder_id}/key') #à réglé
    return send_from_directory(variable_key, filename, mimetype='application/octet-stream')

@main.route('/upload', methods=['POST'])
def upload_video():
    output_path = handle_upload()
    if output_path:
        flash('Video uploaded and converted successfully!')
        return redirect(url_for('main.uploads_video'))
    
@main.route('/add_category_app', methods=['POST'])
def add_category():
    output_category_name = category_insertion()
    if output_category_name:
        flash('Image uploaded and converted successfully!')
        return redirect(url_for('main.create_category'))
    
@main.route('/add_module_app', methods=['POST'])
def add_module():
    output_module_name = module_insertion()
    if output_module_name:
        flash('Image uploaded and converted successfully!')
        return redirect(url_for('main.create_module'))
    
@main.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '')
    result = get_entities_with_image("module", query)

    if result:
        return jsonify(result) if result else jsonify([])
    
@main.route('/activation_success', methods=['POST'])
def activate_success():
    id_module = request.form.get('id_modules')
    id_user = request.form.get('id_user')
    decoded_id_user = decode(id_user)
    decoded_id_module = decode(id_module)
    video_result = match_objet("Video", 'id_module', decoded_id_module)
    id_video = video_result.encoded_id
    if insertion_achat(decoded_id_user, decoded_id_module) == True:
        return redirect(url_for('main.show_video', id=id_video))
    else:
        return redirect(url_for('main.show_video', id=id_video))

#redirection externe et interne
@main.route('/redirect_google')
def redirect_google():
        return redirect("https://www.google.com")

@main.route('/redirect_yahoo')
def redirect_yahoo():
        return redirect("https://www.yahoo.com")

