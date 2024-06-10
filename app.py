from flask import Flask, render_template, send_from_directory, redirect, url_for
import os
import time
import re
import json

app = Flask(__name__, static_url_path='/static')

def get_art_categories():
    art_categories = []
    art_path = os.path.join(app.static_folder, 'art')
    for folder in os.listdir(art_path):
        if os.path.isdir(os.path.join(art_path, folder)):
            art_categories.append(folder)
    return art_categories

def regex_replace(s, find, replace):
    """A custom Jinja filter to perform regex replacement."""
    return re.sub(find, replace, s)

app.jinja_env.filters['regex_replace'] = regex_replace

def get_images_with_categories(art_categories, category='all', sort='date-desc'):
    all_images = []
    for cat in art_categories:
        if category != 'all' and cat != category:
            continue
        category_path = os.path.join(app.static_folder, 'art', cat)
        for root, _, filenames in os.walk(category_path):
            for filename in filenames:
                if filename.lower().endswith(('.jpg', '.png', '.gif')):
                    file_path = os.path.join(root, filename)
                    creation_time = os.path.getctime(file_path)
                    match = re.match(r"(\d+)", filename)
                    if match:
                        prefix = int(match.group(1))
                    else:
                        prefix = float('inf')
                    all_images.append({
                        'filename': filename,
                        'category': cat,
                        'ctime': creation_time,
                        'prefix': prefix
                    })
    all_images.sort(key=lambda x: (x['prefix'], -x['ctime'] if sort == 'date-desc' else x['ctime']))
    return all_images

@app.route('/')
def index():
    art_categories = get_art_categories()
    images = get_images_with_categories(art_categories)
    return render_template('index.html', art_categories=art_categories, images=images)

@app.route('/portfolio/', defaults={'category': 'all'})
@app.route('/portfolio/<category>/')
def portfolio(category):
    art_categories = get_art_categories()
    images = get_images_with_categories(art_categories, category)
    return render_template('portfolio.html', art_categories=art_categories, images=images, selected_category=category)

@app.route('/laternen')
def laternen():
    visit_count = increment_visit('visits.js')
    redirect_url = 'https://www.etsy.com/listing/1717112463/'
    return redirect(redirect_url)

@app.route('/laternenqr')
def laternenqr():
    visit_count = increment_visit('visitsqr.js')
    redirect_url = 'https://www.etsy.com/listing/1717112463/'
    return redirect(redirect_url)

def increment_visit(log_filename):
    log_path = os.path.join(app.static_folder, log_filename)
    if not os.path.exists(log_path):
        visits = {'count': 0}
    else:
        with open(log_path, 'r') as file:
            visits = json.load(file)
    visits['count'] += 1
    visits['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, 'w') as file:
        json.dump(visits, file)
    return visits['count']

if __name__ == '__main__':
    app.run(debug=True)
