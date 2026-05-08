from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from supabase_client import (
    get_leadership,
    get_ministries,
    get_sermons,
    get_testimonials,
    get_events,
    get_site_settings,
    get_blog_posts,
    supabase_insert,
    supabase_get
)
from admin import admin_bp
import os
port = int(os.environ.get('PORT', 5000))
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'generation-family-secret-key-2026')
app.register_blueprint(admin_bp)

@app.context_processor
def inject_settings():
    return {'settings': get_site_settings()}


@app.route('/')
def home():
    settings = get_site_settings()
    leadership = get_leadership()
    ministries = get_ministries()
    testimonials = get_testimonials()
    hero_images = supabase_get('hero_images', {'is_active': 'eq.true', 'order': 'created_at.desc'})
    return render_template(
        'index.html',
        settings=settings,
        leadership=leadership,
        ministries=ministries,
        testimonials=testimonials,
        hero_images=hero_images
    )

# ==================== ABOUT ====================
@app.route('/about')
def about():
    settings = get_site_settings()
    leadership = get_leadership()
    return render_template('about.html', settings=settings, leadership=leadership)


# ==================== MINISTRIES ====================
@app.route('/ministries')
def ministries():
    ministries = get_ministries()
    return render_template('ministries.html', ministries=ministries)


@app.route('/ministries/<slug>')
def ministry_detail(slug):
    ministries = get_ministries()
    ministry = next((m for m in ministries if m['slug'] == slug), None)
    return render_template('ministry-detail.html', ministry=ministry)


# ==================== PROGRAMS / EVENTS ====================
@app.route('/programs')
def programs():
    events = get_events()
    return render_template('programs.html', events=events)


# ==================== SERMONS ====================
@app.route('/sermons')
def sermons():
    sermons_list = get_sermons()
    return render_template('sermons.html', sermons=sermons_list)


# ==================== GIVING ====================
@app.route('/giving')
def giving():
    return render_template('giving.html')


# ==================== RESOURCES ====================
@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/resources/canvas')
def resources_canvas():
    return render_template('canvas.html')

@app.route('/resources/media')
def resources_media():
    return render_template('media.html')

@app.route('/resources/tgf-music')
def tgf_music():
    return render_template('tgf-music.html')

@app.route('/resources/tgf-drama')
def tgf_drama():
    return render_template('tgf-drama.html')

@app.route('/resources/tgf-poems')
def tgf_poems():
    return render_template('tgf-poems.html')

@app.route('/resources/sermons-mp3')
def sermons_mp3():
    sermons_list = get_sermons()
    return render_template('sermons-mp3.html', sermons=sermons_list)

@app.route('/resources/apparel')
def apparel():
    return render_template('apparel.html')

@app.route('/resources/books')
def books():
    return render_template('books.html')


# ==================== BLOG ====================
@app.route('/blog')
def blog():
    posts = get_blog_posts()
    return render_template('blog.html', posts=posts)


# ==================== CONTACT ====================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    settings = get_site_settings()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Save to Supabase
        supabase_insert('contact_submissions', {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        })
        
        # Send email via Brevo
        try:
            from brevo_client import send_contact_notification
            result = send_contact_notification(name, email, subject, message)
            print(f"DEBUG Brevo result: {result}")
        except Exception as e:
            print(f"DEBUG Brevo failed: {e}")
        
        return render_template('contact.html', settings=settings, success=True)
    
    return render_template('contact.html', settings=settings, success=False)



# ==================== FAQs ====================
@app.route('/faqs')
def faqs():
    return render_template('faqs.html')


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    
    if email:
        try:
            supabase_insert('newsletter_subscribers', {'email': email})
        except:
            pass
        
        try:
            from brevo_client import add_subscriber_to_brevo
            add_subscriber_to_brevo(email)
        except Exception as e:
            print(f"Brevo add subscriber failed: {e}")
        
        try:
            from brevo_client import send_subscriber_welcome
            send_subscriber_welcome(email)
        except Exception as e:
            print(f"Brevo welcome email failed: {e}")
        
        return jsonify({'status': 'success', 'message': 'Subscribed!'})
    
    return jsonify({'status': 'error', 'message': 'Email required.'})


if __name__ == '__main__':
    app.run(debug=True)