from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from math import ceil
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to store uploaded images
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
db = SQLAlchemy(app)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.now())
    image_path = db.Column(db.String(255), nullable=True)


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    posts = BlogPost.query.order_by(BlogPost.date_created.desc()).paginate(page=page, per_page=per_page)
    return render_template('index.html', posts=posts)

@app.route('/add', methods=['POST'])
def add_post():
    title = request.form['title']
    content = request.form['content']
    image = request.files.get('image')  # Retrieve the uploaded file

    if image and image.filename != '':
        # Secure the filename and save the image
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        # Store only the relative path for serving the image
        image_path = f"uploads/{filename}"
    else:
        image_path = None

    # Create the new blog post with the image path
    new_post = BlogPost(title=title, content=content, image_path=image_path)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_post(id):
    post_to_delete = BlogPost.query.get_or_404(id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
