from flask import Flask, render_template, request, redirect, url_for, flash, session



from werkzeug.security import generate_password_hash, check_password_hash



from werkzeug.utils import secure_filename



from datetime import datetime



import os



from functools import wraps



import tempfile







app = Flask(__name__)



app.secret_key = 'your-secret-key'  # Change this to a secure secret key



UPLOAD_FOLDER = 'static/uploads'



ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'}







app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER







# Dummy database (Replace with a real database in production)



users = {



    'teacher': {



        'password': generate_password_hash('teacher123'),



        'type': 'teacher',



        'name': 'AASTU Geology Teacher'



    },



    'student': {



        'password': generate_password_hash('student123'),



        'type': 'student',



        'name': 'AASTU Geology Student'



    }



}







materials = []



news = []







# Login decorators



def teacher_required(f):



    @wraps(f)



    def decorated_function(*args, **kwargs):



        if not session.get('logged_in') or session.get('user_type') != 'teacher':



            flash('Please login as a teacher to access this page.')



            return redirect(url_for('login'))



        return f(*args, **kwargs)



    return decorated_function







def student_required(f):



    @wraps(f)



    def decorated_function(*args, **kwargs):



        if not session.get('logged_in') or session.get('user_type') != 'student':



            flash('Please login as a student to access this page.')



            return redirect(url_for('login'))



        return f(*args, **kwargs)



    return decorated_function







@app.route('/')



def login():



    return render_template('login.html')







@app.route('/login', methods=['POST'])



def process_login():



    username = request.form['username']



    password = request.form['password']



    



    if username in users:



        if check_password_hash(users[username]['password'], password):



            session['logged_in'] = True



            session['user_type'] = users[username]['type']



            session['username'] = username



            session['name'] = users[username]['name']



            



            if users[username]['type'] == 'teacher':



                return redirect(url_for('teacher_dashboard'))



            else:



                return redirect(url_for('student_dashboard'))



    



    flash('Invalid credentials')



    return redirect(url_for('login'))







@app.route('/teacher/dashboard')



@teacher_required



def teacher_dashboard():



    return render_template('teacher/dashboard.html', materials=materials, news=news)







@app.route('/student/dashboard')



@student_required



def student_dashboard():



    return render_template('student/dashboard.html', materials=materials, news=news)







@app.route('/upload_material', methods=['GET', 'POST'])



@teacher_required



def upload_material():



    if request.method == 'POST':



        if 'file' not in request.files:



            flash('No file selected')



            return redirect(request.url)



        



        file = request.files['file']



        if file.filename == '':



            flash('No file selected')



            return redirect(request.url)



        



        if file and allowed_file(file.filename):



            filename = secure_filename(file.filename)



            # Use temporary file for Render deployment



            with tempfile.NamedTemporaryFile(delete=False) as tmp:



                file.save(tmp.name)



                # Here you would typically upload to cloud storage



                # For now, we'll still save locally



                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)



                os.rename(tmp.name, file_path)



            



            materials.append({



                'name': request.form['name'],



                'description': request.form['description'],



                'filename': filename



            })



            flash('Material uploaded successfully')



            return redirect(url_for('teacher_dashboard'))



    



    return render_template('teacher/upload_material.html')







@app.route('/post_news', methods=['GET', 'POST'])



@teacher_required



def post_news():



    if request.method == 'POST':



        news.append({



            'title': request.form['title'],



            'content': request.form['content'],



            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")



        })



        flash('News posted successfully')



        return redirect(url_for('teacher_dashboard'))



    



    return render_template('teacher/post_news.html')







@app.route('/logout')



def logout():



    session.clear()



    return redirect(url_for('login'))







def allowed_file(filename):



    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS







@app.route('/manage_users')



@teacher_required



def manage_users():



    return render_template('teacher/manage_users.html', users=users)







@app.route('/change_password', methods=['POST'])



@teacher_required



def change_password():



    username = request.form['username']



    new_password = request.form['new_password']



    



    if username in users:



        users[username]['password'] = generate_password_hash(new_password)



        flash(f'Password changed successfully for {username}')



    else:



        flash('User not found')



    



    return redirect(url_for('manage_users'))







if __name__ == '__main__':



    os.makedirs(UPLOAD_FOLDER, exist_ok=True)



    port = int(os.environ.get("PORT", 10000))



    app.run(host='0.0.0.0', port=port, debug=False) 


