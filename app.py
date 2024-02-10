from flask import Flask, render_template, send_from_directory
import os
import time
import re  # Import regex module

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
                    # Extract numeric prefix
                    match = re.match(r"(\d+)", filename)
                    if match:
                        prefix = int(match.group(1))
                    else:
                        prefix = float('inf')  # Ensure files without a prefix are sorted last
                    all_images.append({
                        'filename': filename,
                        'category': cat,
                        'ctime': creation_time,
                        'prefix': prefix  # Add prefix for sorting
                    })
    # Sort by numeric prefix first, then by the specified sort order
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



if __name__ == '__main__':
    app.run(debug=True)
