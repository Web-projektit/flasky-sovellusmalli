from flask import render_template,request, \
     flash,redirect,url_for,jsonify,current_app, \
     send_from_directory, make_response
from flask_login import login_required,current_user
from ..decorators import admin_required,debuggeri
from ..models import User
from .forms import ProfileForm,ProfileFormAdmin
from app import db
from . import main
from sqlalchemy import text
import os
from werkzeug.utils import secure_filename
from flask_babel import _
from openai import OpenAI
import json
from difflib import SequenceMatcher
from flask import Flask, request, jsonify
import polib
from .. import csrf





client = OpenAI()
# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# if you saved the key under a different environment variable name, you can do something like:
# client = OpenAI(api_key=os.environ.get("CUSTOM_ENV_NAME"))
import os
import openai

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def strip_code_block(markdown_text):
    """
    Remove Markdown code block markers from the beginning and end of the text.
    """
    lines = markdown_text.strip().splitlines()
    # Check and remove the first line if it starts with ```
    if lines and lines[0].startswith("```"):
        lines.pop(0)
    # Check and remove the last line if it starts with ```
    if lines and lines[-1].startswith("```"):
        lines.pop()
    return "\n".join(lines)


def analyze_python_code(code):
    """
    Analyze Python code and decide whether to wrap strings with _l() (lazy_gettext)
    or _() (gettext) based on their context.
    """
    """"
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=(
                "Analyze the following Python code. Identify all user-facing strings that should "
                "be localized. Use _l() for strings that are lazily evaluated (e.g., delayed contexts "
                "in Flask) and _() for strings that are immediately evaluated. Return the updated "
                "code with the appropriate wrapping applied.\n\nCode:\n"
                f"{code}"
            ),
            max_tokens=1000,
            temperature=0,
        )
        return response.choices[0].text.strip()
    """
    try:
        completion = client.chat.completions.create(
            # model="gpt-3.5-turbo",  # Use a suitable model for translation
            model="gpt-4o",
            messages=[
                {
                "role": "system",
                "content": f"Analyze the following code and identify all user-facing strings that \
                should be localized. Wrap these strings with _() for gettext and _l() for lazy_gettext. \
                Preserve the original code structure and ensure proper placement of the wrapping function. Assume \
                lazy_gettext for forms. Return the updated code with the appropriate wrapping applied.",
                },
                {
                "role": "user",
                "content": code,
                },
            ],
            temperature=0,  # Lower temperature for more deterministic output
            # prompt=f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}",
            # max_tokens=500,
            )
        response = completion.choices[0].message.content.strip()
        response = strip_code_block(response)
        print("response:",response)
        return response
    
    except Exception as e:
        print(f"Error calling OpenAI API for Python: {e}")
        return None

def analyze_html_template(code):
    """
    Analyze HTML template code and wrap all user-facing strings with _() (gettext).
    """
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=(
                "Analyze the following HTML template code and identify all user-facing strings that "
                "should be localized. Wrap these strings with _() for gettext. Preserve the original "
                "template structure and ensure proper placement of the wrapping function.\n\nCode:\n"
                f"{code}"
            ),
            max_tokens=1000,
            temperature=0,
        )
        return response.choices[0].text.strip()
    """
    try:
        completion = client.chat.completions.create(
            # model="gpt-3.5-turbo",  # Use a suitable model for translation
            model="gpt-4o",
            messages=[
                {
                "role": "system",
                "content": f"Analyze the following code and identify all user-facing strings that \
                should be localized. Wrap these strings with _() for gettext and _l() for lazy_gettext. \
                Preserve the original code structure and ensure proper placement of the wrapping function. Assume \
                lazy_gettext for forms. Return the updated code with the appropriate wrapping applied.",
                },
                {
                "role": "user",
                "content": code,
                },
            ],
            temperature=0,  # Lower temperature for more deterministic output
            # prompt=f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}",
            # max_tokens=500,
            )
        # return response["choices"][0]["message"]["content"].strip()
        response = completion.choices[0].message.content.strip()
        response = strip_code_block(response)
        print("response:",response)
        return response
    
    except Exception as e:
        print(f"Error calling OpenAI API for HTML: {e}")
        return None

def process_file(file_path):
    """
    Process a single file and wrap translatable strings with _l() or _() based on context and file type.
    """
    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Determine if the file is Python or HTML
        if file_path.endswith(".py"):
            updated_code = analyze_python_code(code)
        elif file_path.endswith(".html"):
            updated_code = analyze_html_template(code)
        else:
            print(f"Skipping unsupported file: {file_path}")
            return

        if updated_code:
            # Save changes back to the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(updated_code)
            print(f"Updated file: {file_path}")
        else:
            print(f"No changes made to file: {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def process_directory(directory):
    """
    Process all .py and .html files in a given directory.
    """
    if not os.path.isdir(directory):
        if os.path.isfile(directory):
            process_file(directory)
        else:
            print(f"Invalid file path: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") or file.endswith(".html"):
                process_file(os.path.join(root, file))
    return jsonify(OK="Files processed successfully.")
# Example: Process the current directory


def translate_text(text, model="gpt-4o", source_lang="English", target_lang="Finnish"):
    """Use OpenAI API to translate text."""
    print("TEXT:"+text)
    try:
        completion = client.chat.completions.create(
            # model="gpt-3.5-turbo",  # Use a suitable model for translation
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a translator converting text from {source_lang} to {target_lang}.",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            temperature=0,  # Lower temperature for more deterministic output
            # prompt=f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}",
            # max_tokens=500,
            )
        # return response["choices"][0]["message"]["content"].strip()
        response = completion.choices[0].message
        print("response:",response.content.strip()) 
        return response.content.strip()
    except Exception as e:
        return str(e)


@debuggeri
def shorten(filename):
    name, extension = os.path.splitext(filename)
    # print("SHORTEN:"+name+" "+extension)
    length = 64 - len(extension)
    return name[:length] + extension

'''def allowed_file(filename):
    app.fi_translations.install()    app = current_app._get_current_object()
    ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
'''

def tee_kuvanimi(id,kuva):
    return str(id) + '_' + kuva

def poista_vanha_kuva(id,kuva):
    kuvanimi = tee_kuvanimi(id,kuva)
    app = current_app._get_current_object()
    KUVAPOLKU = app.config['KUVAPOLKU']
    filename = os.path.join(KUVAPOLKU, kuvanimi)
    print("POISTETAAN:"+filename)
    try:
        os.remove(filename)
    except Exception as e:
        app.logger.info(e)
        return False
    else:   
        return True

@main.route('/set_language/<lang>')
def set_language(lang = None):
    app = current_app._get_current_object()
    app.logger.info("SET_LANGUAGE:"+lang)      
    if lang not in app.config['BABEL_SUPPORTED_LOCALES']:
        lang = app.config['BABEL_DEFAULT_LOCALE']
    # Aseta kieli evästeeseen ja ohjaa käyttäjä takaisin samalle sivulle
    response = redirect(request.referrer or url_for('index'))
    response.set_cookie('lang', lang)
    return response
 
@main.route('/')
def index():
    print("INDEX " + _('Hello'))
    return render_template('index.html',greeting=_('Hello'))

@main.route('/img/')
@main.route('/img/<path:filename>')
def img(filename = None):
    app = current_app._get_current_object()
    KUVAPOLKU = app.config['KUVAPOLKU']
    if filename is None:
        return send_from_directory('static','default_profile.png')
    return send_from_directory(KUVAPOLKU, filename)

@main.route('/edit_profile', methods=['GET', 'POST'])  
@login_required
def edit_profile():
    user = User.query.get_or_404(current_user.id)
    form = ProfileForm(obj=user, max_file_size=current_app.config.get('MAX_FILE_SIZE', 1 * 1024 * 1024))
    app = current_app._get_current_object()
    KUVAPOLKU = app.config['KUVAPOLKU']
    kuvanimi = ''
    # Huom. omat validointifunktiot ProfileForm-luokassa
    # Huom. kuvan nimen tallennus tietokantaan perustuu img-kenttään,
    # kuvatiedoston tallennus palvelimelle files-kenttään. Img-kenttä
    # tarvitaan, 1) jotta muuttamaton kuva säilyy, sillä sitä ei
    # tule valituksi files-kenttään lomakkeelta ja 2) kuvan poistaminen
    # ilmenee tyhjästä img-kentästä.
    if form.validate_on_submit():
        # check if the post request has the file part
        print("FILES:"+str(request.files))
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            kuvanimi = file.filename
            print("file.filename:"+kuvanimi)
            if current_user.img and kuvanimi != current_user.img:
                poista_vanha_kuva(current_user.id,current_user.img)
            # if kuvanimi and allowed_file(kuvanimi):
            if kuvanimi:    
                # Lomakkeelta lähetettynä paikallinen tallennus,
                # S3- ja Azure-tallennus tehty erikseen Javascriptillä
                kuvanimi = shorten(secure_filename(kuvanimi))
                filename = tee_kuvanimi(current_user.id,kuvanimi)
                file.save(os.path.join(KUVAPOLKU, filename))
        form.populate_obj(user)
        print("KUVANIMI:"+kuvanimi)
        # Huom. Alkuperäinen kuvan nimi on lyhentämätön ja se tallenetaan
        # lyhennettynä tietokantaan ilman id-tunnistetta, kuvatiedosto
        # tallennetaan id-tunnisteella, jotta se on yksilöllinen.
        print("IMG:"+user.img)
        user.img = kuvanimi if kuvanimi else user.img
        # db.session.add(current_user._get_current_object())
        try:
            db.session.commit()
            flash('Your profile has been updated.', 'success')
            return redirect(url_for('.user', username=user.username))
        except Exception as e:
            db.session.rollback()
            flash('Virhe tallennuksessa.', 'danger')
            app.logger.info(e)
            kuva = tee_kuvanimi(user.id, kuvanimi) if kuvanimi else ''
            return render_template('edit_profile.html', form=form,kuva=kuva)
    kuva = tee_kuvanimi(user.id,user.img) if user.img else ''  
    print("kuva:"+kuva) 
    return render_template('edit_profile.html', form=form,kuva=kuva,API_KEY=app.config.get('GOOGLE_API_KEY'))


@main.route('/edit_profile_admin', methods=['GET', 'POST']) 
@login_required
@admin_required
def edit_profile_admin():
    app = current_app._get_current_object()
    user = User.query.get_or_404(request.args.get('id'))
    # Tulosta MySQL-kyselyn arvot
    for key, value in vars(user).items():
        print(f'{key}: {value}')   
    kuva = tee_kuvanimi(user.id,user.img) if user.img else ''
    form = ProfileFormAdmin(obj=user)
    print("FORM:"+str(form))
    if form.validate_on_submit():
        form.populate_obj(user)
        try: 
            db.session.commit()
            flash('Käyttäjän tiedot on päivitetty.', 'success')
            return redirect(url_for('.users'))
        except Exception as e:
            db.session.rollback()
            flash('Virhe tallennuksessa.', 'danger')
            current_app.logger.info(e)
            return render_template('edit_profile_admin.html', form=form,user=user,kuva=kuva,API_KEY=app.config.get('GOOGLE_API_KEY'))
    return render_template('edit_profile_admin.html', form=form,user=user,kuva=kuva,API_KEY=app.config.get('GOOGLE_API_KEY'))
    
@main.route('/user', methods=['GET'])
@login_required
def user(): 
    kuva = tee_kuvanimi(current_user.id,current_user.img) if current_user.img else ''
    return render_template('user.html',user=current_user,kuva=kuva,API_KEY=current_app.config.get('GOOGLE_API_KEY'))   

@main.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    if request.form.get('painike'):
        users = request.form.getlist('users')
        if len(users) > 0:
            query_start = "INSERT INTO users (id,active) VALUES "
            query_end = " ON DUPLICATE KEY UPDATE active = VALUES(active)"
            query_values = ""
            active = request.form.getlist('active')
            for v in users:
                if v in active:
                    query_values += "("+v+",1),"
                else:
                    query_values += "("+v+",0),"
                # query_values += "("+v+"," + ("1" if v in active else "0") + "),"        
                # query_values += f"({v}, {'1' if v in active else '0'}),"
            query_values = query_values[:-1]
            query = query_start + query_values + query_end
            # print("\n"+query+"\n")
            # result = db.session.execute('SELECT * FROM my_table WHERE my_column = :val', {'val': 5})
            db.session.execute(text(query))
            db.session.commit()
            # return query
            #return str(request.form.getlist('users')) + \
            #       "<br>" + \
            #        str(request.form.getlist('active'))
        else:
            flash("Käyttäjälista puuttuu.")
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.name).paginate(
        page=page, per_page=current_app.config.get('FS_POSTS_PER_PAGE', 25),
        error_out=False)
    lista = pagination.items
    return render_template('users.html',users=lista,pagination=pagination,page=page)

@main.route('/poista', methods=['GET', 'POST'])
@login_required
@admin_required
def poista():
    # print("POISTA:"+request.form.get('id'))
    user = User.query.get(request.form.get('id'))
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        flash(f"Käyttäjä {user.name} on poistettu")
        return jsonify(OK="käyttäjä on poistettu.")
    else:
        return jsonify(virhe="käyttäjää ei löydy.")

def is_similar(a, b, threshold=0.8):
    return SequenceMatcher(None, a, b).ratio() > threshold

@main.route('/principles', methods=['GET', 'POST'])
@login_required
@admin_required
def principles():
    principles_file = 'principles.json'
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {"role": "system", "content": "You are a programming professor, skilled in explaining complex programming concepts by known phrases."},
        {"role": "user", "content": "Compose a raw json list without any preface,json keyword or comments of 100 basic proven programming principles. For each listing include id, principle and description properties,"}
        ])

    response = completion.choices[0].message
    response_content = response.content.strip("```json").strip("```")
    print(response_content)
    
    try:
        # Filter out any text before the actual JSON list
        json_start = response_content.find('[')
        json_end = response_content.rfind(']') + 1
        response_json = json.loads(response_content[json_start:json_end])
    except json.JSONDecodeError as e:
        current_app.logger.error(f"JSON decode error: {e}")
        return jsonify(error="Failed to decode JSON response from OpenAI"), 500
    
    # Load existing principles
    if os.path.exists(principles_file):
        try:
            with open(principles_file, 'r') as json_file:
                existing_principles = json.load(json_file)
        except json.JSONDecodeError:
            existing_principles = []
    else:
        existing_principles = []

    # Extract abbreviations from existing principles
    existing_abbreviations = set()
    for principle in existing_principles:
        words = principle['principle'].split()
        for word in words:
            clean_word = word.strip('()')
            if clean_word.isupper():
                existing_abbreviations.add(clean_word)

    # Add only new items that are not duplicates and do not contain existing abbreviations
    existing_principles_set = {principle['principle'] for principle in existing_principles}
    new_principles = []
    for item in response_json:
        if item['principle'] not in existing_principles_set and not any(is_similar(item['principle'], existing['principle']) for existing in existing_principles):
            words = item['principle'].split()
            if not any(word.strip('()') in existing_abbreviations for word in words if word.strip('()').isupper()):
                new_principles.append(item)

    # Replace IDs for new principles
    for i, principle in enumerate(new_principles, start=1):
        principle['id'] = i

    # Save the updated principles
    updated_principles = existing_principles + new_principles
    with open(principles_file, 'w') as json_file:
        json.dump(updated_principles, json_file, indent=4)
    
    # Identify duplicates based on the meaning of the principle
    principles_count = {}
    for principle in updated_principles:
        principle_text = principle['principle']
        found = False
        for key in principles_count:
            if is_similar(principle_text, key):
                principles_count[key].append(principle)
                found = True
                break
        if not found:
            principles_count[principle_text] = [principle]

    duplicates = [principles for principles in principles_count.values() if len(principles) > 1]
    return render_template('principles.html', content=updated_principles, duplicates=duplicates)

@main.route('/practices', methods=['GET', 'POST'])
@login_required
@admin_required
def practices():
    principles_file = 'practices.json'
    existing_principles = []
    if os.path.exists(principles_file):
        try:
            with open(principles_file, 'r') as json_file:
                existing_principles = json.load(json_file)
        except json.JSONDecodeError:
            existing_principles = []
    length_of_practices = len(existing_principles)        
    existing_practices_string = str([principle['practice'] for principle in existing_principles]) 

    number_of_new_practices = "10" if existing_principles else "100"   
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
        {"role": "system", "content": "You are a programming professor, skilled in explaining web programming concepts by known phrases."},
        {"role": "user", "content": "Take an existing .json list of best Web programming practices: " + existing_practices_string + ". Make a new list of " + number_of_new_practices + " best unique Web programming best practices that are not yet included in the existing .json list: \
          and add these new items to the existing .json list. Sort the new combined .json list by the importance of the practice if you can. Return the whole combined .json list which should now have at least all items from the existing list. For each item include id, practice and description properties."}
        ])

    response = completion.choices[0].message
    response_content = response.content.strip("```json").strip("```")
    print(response_content)
    
    try:
        # Filter out any text before the actual JSON list
        json_start = response_content.find('[')
        json_end = response_content.rfind(']') + 1
        response_json = json.loads(response_content[json_start:json_end])
    except json.JSONDecodeError as e:
        current_app.logger.error(f"JSON decode error: {e}")
        return jsonify(error="Failed to decode JSON response from OpenAI"), 500
    
    if length := len(response_json) < length_of_practices:
        return jsonify(error=f"Received only {length} new practices from OpenAI, expected at least {length_of_practices} practices")
    '''
    # Extract abbreviations from existing principles
    existing_abbreviations = set()
    for principle in existing_principles:
        words = principle['practice'].split()
        for word in words:
            clean_word = word.strip('()')
            if clean_word.isupper():
                existing_abbreviations.add(clean_word)
    
    print("existing_abbreviations:",existing_abbreviations)
    # Add only new items that are not duplicates and do not contain existing abbreviations
    existing_principles_set = {principle['practice'] for principle in existing_principles}
    new_principles = []
    for item in response_json:
        if item['practice'] not in existing_principles_set and not any(is_similar(item['practice'], existing['practice']) for existing in existing_principles):
            words = item['practice'].split()
            print("words:",words)
            if not any(word.strip('()') in existing_abbreviations for word in words if word.strip('()').isupper()):
                new_principles.append(item)
    '''
    # Replace IDs for new principles
    for i, principle in enumerate(response_json, start=1):
        if principle['id'] != i:
            print("id vaihtuu: ",principle['id'],"=>",i)
            principle['id'] = i

    # Save the updated principles
    updated_principles = response_json
    with open(principles_file, 'w') as json_file:
        json.dump(updated_principles, json_file, indent=4)
    
    # Identify duplicates based on the meaning of the principle
    principles_count = {}
    for principle in updated_principles:
        principle_text = principle['practice']
        found = False
        for key in principles_count:
            if is_similar(principle_text, key):
                principles_count[key].append(principle)
                found = True
                break
        if not found:
            principles_count[principle_text] = [principle]

    duplicates = [principles for principles in principles_count.values() if len(principles) > 1]
    # duplicates = principles_count
    duplicates  = duplicates[0] if duplicates else []
    print("duplicates:",duplicates)
    return render_template('practices.html', content=updated_principles, duplicates=duplicates)


@main.route('/translate', methods=['GET'])
@csrf.exempt
def translate():
    """
    Translate a .po file from English to Finnish, save the translated content as .mo.
    Expected input: JSON with "file_path" key for the .po file.
    """
    language_codes = current_app.config.get('BABEL_SUPPORTED_LOCALES', ['fi'])
    default_language_code = current_app.config.get('BABEL_DEFAULT_LOCALE', 'en')
    languages = current_app.config.get('SUPPORTED_LANGUAGES', {'en':'English', 'fi':'Finnish'})
    source_language = languages[default_language_code]
    dir = "translations/"
    print("language_codes:",language_codes)
    for lang in language_codes:
        file_path = f"{dir}{lang}/LC_MESSAGES/messages.po"
        print(f"LANG:{lang}, FILE_PATH:{file_path}")
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "Invalid file path provided."}), 400
        try:
            # Load the .po file
            po = polib.pofile(file_path)
            if lang == default_language_code:
                target_language = source_language
            else:
                target_language = languages[lang]    

            # Translate each entry
            for entry in po:
                print(f"Entry: {entry}")
                if 'fuzzy' in entry.flags:
                    entry.msgstr = ''
                if entry.msgid and not entry.msgstr:  # Only translate if msgstr is empty
                    if source_language == target_language:
                        entry.msgstr = entry.msgid
                    else:
                        entry.msgstr = translate_text(entry.msgid, model="gpt-4o", source_lang=source_language, target_lang=target_language)
                    print(f"Translated: {entry.msgid} => {entry.msgstr}")
            # Save the translated content as .po and .mo
            po.save(file_path)
            mo_file_path = file_path.replace(".po", ".mo")
            po.save_as_mofile(mo_file_path)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"message": "Translations completed."})

    '''
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            translation = client.translate(
                engine="text-davinci-003",
                text=text,
                target_language="fi"
                )
            return jsonify(translation=translation)
    return jsonify(error="No text provided"), 400
'''

@main.route('/add_babel_calls', methods=['GET'])
@csrf.exempt
def add_babel_calls():
    project_directory = os.path.join(current_app.root_path, 'templates', '500.html')  # Change this to your project's directory
    process_directory(project_directory)
    return jsonify(OK="Files processed successfully.")


