import os
import shutil
import datetime
import markdown2
from jinja2 import Environment, FileSystemLoader
from template_globals import get_globals
from utils import HTMLTitleFinder, find_dates, clear_dir


###############################################
## find metadata for articles and categories ##
###############################################

def index_blog_structure(config):
    articles = []
    categories = []
    pages = []

    for root, sub_dirs, files in os.walk('articles', topdown=True):
        cur_category = find_category_meta(config, root)
        categories.append(cur_category)
        
        for filename in files:
            article = find_article_meta(config, os.path.join(root, filename))
            articles.append(article)

    for root, sub_dirs, files in os.walk('pages', topdown=True):
        for filename in files:
            page = find_page_meta(config, os.path.join(root, filename))
            pages.append(page)

    return articles, categories, pages

def find_category_meta(config, path):
    meta = {}
    meta['name'] = path
    meta['display_name'] = config['category_display_names'][path] if path in config['category_display_names'] else os.path.basename(path)
    meta['active_menu_item'] = 'BLOG_ARCHIVES'

    index_path = '/'.join([path, 'index.html'])
    meta['path'] = index_path
    meta['link'] = '/'.join([config['url'], index_path])
    return meta

def find_article_meta(config, path):
    meta = {}

    meta['name'] = path
    article_html = markdown2.markdown(open(path, 'r').read())
    meta['content'] = article_html
    title_finder = HTMLTitleFinder(article_html)
    meta['title'] = title_finder.headline
    meta['description'] = title_finder.first_paragraph
    meta['active_menu_item'] = 'BLOG_HOME'
    
    publication_date, last_update = find_dates(path)
    if publication_date:
        meta['publication_date'] = publication_date.astimezone(tz=datetime.timezone.utc).isoformat()
    else:
        meta['publication_date'] = None 
    if last_update:
        meta['last_update'] = last_update.astimezone(tz=datetime.timezone.utc).isoformat()
    else:
        meta['last_update'] = None

    article_path = os.path.splitext(path)[0] + '.html'
    meta['path'] = article_path
    meta['link'] = '/'.join([config['url'], article_path])
    return meta

def find_page_meta(config, path):
    meta = {}

    meta['name'] = path
    page_html = markdown2.markdown(open(path, 'r').read())
    meta['content'] = page_html
    meta['active_menu_item'] = path
    
    publication_date, last_update = find_dates(path)
    if publication_date:
        meta['publication_date'] = publication_date.astimezone(tz=datetime.timezone.utc).isoformat()
    else:
        meta['publication_date'] = None 
    if last_update:
        meta['last_update'] = last_update.astimezone(tz=datetime.timezone.utc).isoformat()
    else:
        meta['last_update'] = None

    page_path = os.path.splitext(os.path.basename(path))[0] + '.html'
    meta['path'] = page_path
    meta['link'] = '/'.join([config['url'], page_path])
    return meta

#################################################
## translate templated markdown code into html ##
#################################################

def generate_html(config, output_dir):
    articles, categories, pages = index_blog_structure(config)
    
    file_loader = FileSystemLoader(os.path.join('themes', config['theme'], 'templates'))
    env = Environment(loader=file_loader)
    env.globals = get_globals(config, articles, categories, pages)

    clear_dir(output_dir)
    generate_home(config, output_dir, env)

    for category in categories:
        generate_category_index(config, output_dir, env, category) 
    
    for article in articles:
        generate_article(config, output_dir, env, article)

    for page in pages:
        generate_page(config, output_dir, env, page)
    
    copy_assets(config, output_dir)

def generate_home(config, output_dir, environment):
    template = environment.get_template('home.template.html')
    this = {}
    this['active_menu_item'] = 'BLOG_HOME'
    html = template.render(this=this)

    export_path = os.path.join(output_dir, 'index.html')
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, 'w') as f:
        f.write(html)

def generate_category_index(config, output_dir, environment, category):
    template = environment.get_template('index.template.html')
    html = template.render(this=category)

    export_path = os.path.join(output_dir, category['path'])
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, 'w') as f:
        f.write(html)

def generate_article(config, output_dir, environment, article):
    template = environment.get_template('article.template.html')
    first_pass = template.render(this=article)
    second_pass = environment.from_string(first_pass).render()

    export_path = os.path.join(output_dir, article['path'])
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, 'w') as f:
        f.write(second_pass)

def generate_page(config, output_dir, environment, page):
    template = environment.get_template('page.template.html')
    first_pass = template.render(this=page)
    second_pass = environment.from_string(first_pass).render()

    export_path = os.path.join(output_dir, page['path'])
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, 'w') as f:
        f.write(second_pass)

def copy_assets(config, output_dir):
    export_path = os.path.join(output_dir, 'assets')
    os.makedirs(export_path, exist_ok=False)
    
    if os.path.exists(export_path):
        shutil.rmtree(export_path)

    shutil.copytree('assets', export_path, dirs_exist_ok=True)
    shutil.copytree(os.path.join('themes', config['theme'], 'assets'), export_path, dirs_exist_ok=True)
