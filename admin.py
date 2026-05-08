from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os
from dotenv import load_dotenv
from supabase_client import (
    supabase_get,
    supabase_get_one,
    supabase_insert,
    supabase_update,
    supabase_delete,
    get_site_settings
)
from cloudinary_client import upload_image, upload_audio

load_dotenv()

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'generation2026')

# ==================== LOGIN DECORATOR ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== LOGIN ====================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        error = 'Incorrect password.'
    return render_template('admin/login.html', error=error)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

# ==================== DASHBOARD ====================
@admin_bp.route('/')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

# ==================== SITE SETTINGS ====================
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    message = None
    error = None
    
    if request.method == 'POST':
        updates = {
            'mission': request.form.get('mission'),
            'vision': request.form.get('vision'),
            'values': request.form.get('values'),
            'lives_impacted': request.form.get('lives_impacted'),
            'years_in_existence': request.form.get('years_in_existence'),
            'cities': request.form.get('cities'),
            'meetings_held': request.form.get('meetings_held'),
            'year_theme': request.form.get('year_theme'),
            'hero_tagline': request.form.get('hero_tagline'),
            'church_address': request.form.get('church_address'),
            'church_phone': request.form.get('church_phone'),
            'church_email': request.form.get('church_email'),
        }
        
        for key, value in updates.items():
            if value is not None:
                try:
                    existing = supabase_get('site_settings', {'setting_key': f'eq.{key}'})
                    if existing:
                        supabase_update('site_settings', existing[0]['id'], {'setting_value': value})
                    else:
                        supabase_insert('site_settings', {'setting_key': key, 'setting_value': value})
                except Exception as e:
                    print(f"Error updating {key}: {e}")
        
        message = "Settings saved successfully!"
    
    current_settings = get_site_settings()
    return render_template('admin/settings.html', settings=current_settings, message=message, error=error)

# ==================== SERMONS (CRUD) ====================
@admin_bp.route('/sermons', methods=['GET', 'POST'])
@login_required
def manage_sermons():
    message = None
    error = None
    
    if request.method == 'POST':
        sermon_id = request.form.get('sermon_id')
        title = request.form.get('title')
        speaker = request.form.get('speaker')
        date = request.form.get('date')
        series = request.form.get('series')
        description = request.form.get('description')
        audio_url = request.form.get('audio_url') or ''
        
        audio_file = request.files.get('audio_file')
        if audio_file and audio_file.filename:
            audio_file.seek(0, 2)
            file_size = audio_file.tell()
            audio_file.seek(0)
            
            if file_size > 40 * 1024 * 1024:
                error = "File too large. Max 40MB. Please compress the MP3."
                sermons = supabase_get('sermons', {'order': 'date.desc'})
                return render_template('admin/sermons.html', sermons=sermons, error=error, message=message)
            
            result = upload_audio(audio_file, folder='generation/sermons')
            audio_url = result['url']
        
        data = {
            'title': title,
            'speaker': speaker,
            'date': date,
            'series': series,
            'description': description,
            'audio_url': audio_url
        }
        
        if sermon_id:
            supabase_update('sermons', int(sermon_id), data)
            message = "Sermon updated!"
        else:
            supabase_insert('sermons', data)
            message = "Sermon added!"
    
    sermons = supabase_get('sermons', {'order': 'date.desc'})
    return render_template('admin/sermons.html', sermons=sermons, message=message, error=error)

@admin_bp.route('/sermons/<int:sermon_id>/edit')
@login_required
def edit_sermon(sermon_id):
    sermon = supabase_get_one('sermons', sermon_id)
    sermons = supabase_get('sermons', {'order': 'date.desc'})
    return render_template('admin/sermons.html', sermons=sermons, edit_sermon=sermon)

@admin_bp.route('/sermons/<int:sermon_id>/delete', methods=['POST'])
@login_required
def delete_sermon(sermon_id):
    supabase_delete('sermons', sermon_id)
    return redirect(url_for('admin.manage_sermons'))

# ==================== LEADERSHIP (CRUD) ====================
@admin_bp.route('/leadership', methods=['GET', 'POST'])
@login_required
def manage_leadership():
    message = None
    error = None
    
    if request.method == 'POST':
        leader_id = request.form.get('leader_id')
        name = request.form.get('name')
        title = request.form.get('title')
        bio = request.form.get('bio')
        display_order = request.form.get('display_order', 0)
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/leadership')
            image_url = result['url']
        
        data = {
            'name': name,
            'title': title,
            'bio': bio,
            'display_order': int(display_order),
            'image_url': image_url
        }
        
        if leader_id:
            supabase_update('leadership', int(leader_id), data)
            message = "Leader updated!"
        else:
            supabase_insert('leadership', data)
            message = "Leader added!"
    
    leaders = supabase_get('leadership', {'order': 'display_order.asc'})
    return render_template('admin/leadership.html', leaders=leaders, message=message, error=error)

@admin_bp.route('/leadership/<int:leader_id>/edit')
@login_required
def edit_leader(leader_id):
    leader = supabase_get_one('leadership', leader_id)
    leaders = supabase_get('leadership', {'order': 'display_order.asc'})
    return render_template('admin/leadership.html', leaders=leaders, edit_leader=leader)

@admin_bp.route('/leadership/<int:leader_id>/delete', methods=['POST'])
@login_required
def delete_leader(leader_id):
    supabase_delete('leadership', leader_id)
    return redirect(url_for('admin.manage_leadership'))

# ==================== MINISTRIES (CRUD) ====================
@admin_bp.route('/ministries', methods=['GET', 'POST'])
@login_required
def manage_ministries():
    message = None
    error = None
    
    if request.method == 'POST':
        ministry_id = request.form.get('ministry_id')
        name = request.form.get('name')
        description = request.form.get('description')
        icon = request.form.get('icon', 'fa-church')
        slug = request.form.get('slug')
        display_order = request.form.get('display_order', 0)
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/ministries')
            image_url = result['url']
        
        data = {
            'name': name,
            'description': description,
            'icon': icon,
            'slug': slug,
            'display_order': int(display_order),
            'image_url': image_url
        }
        
        if ministry_id:
            supabase_update('ministries', int(ministry_id), data)
            message = "Ministry updated!"
        else:
            supabase_insert('ministries', data)
            message = "Ministry added!"
    
    ministries = supabase_get('ministries', {'order': 'display_order.asc'})
    return render_template('admin/ministries.html', ministries=ministries, message=message, error=error)

@admin_bp.route('/ministries/<int:ministry_id>/edit')
@login_required
def edit_ministry(ministry_id):
    ministry = supabase_get_one('ministries', ministry_id)
    ministries = supabase_get('ministries', {'order': 'display_order.asc'})
    return render_template('admin/ministries.html', ministries=ministries, edit_ministry=ministry)

@admin_bp.route('/ministries/<int:ministry_id>/delete', methods=['POST'])
@login_required
def delete_ministry(ministry_id):
    supabase_delete('ministries', ministry_id)
    return redirect(url_for('admin.manage_ministries'))

# ==================== TESTIMONIALS (CRUD) ====================
@admin_bp.route('/testimonials', methods=['GET', 'POST'])
@login_required
def manage_testimonials():
    message = None
    error = None
    
    if request.method == 'POST':
        testimonial_id = request.form.get('testimonial_id')
        name = request.form.get('name')
        quote = request.form.get('quote')
        
        data = {
            'name': name,
            'quote': quote,
            'is_approved': True
        }
        
        if testimonial_id:
            supabase_update('testimonials', int(testimonial_id), data)
            message = "Testimonial updated!"
        else:
            supabase_insert('testimonials', data)
            message = "Testimonial added!"
    
    testimonials = supabase_get('testimonials', {'order': 'created_at.desc'})
    return render_template('admin/testimonials.html', testimonials=testimonials, message=message, error=error)

@admin_bp.route('/testimonials/<int:id>/edit')
@login_required
def edit_testimonial(id):
    testimonial = supabase_get_one('testimonials', id)
    testimonials = supabase_get('testimonials', {'order': 'created_at.desc'})
    return render_template('admin/testimonials.html', testimonials=testimonials, edit_testimonial=testimonial)

@admin_bp.route('/testimonials/<int:id>/delete', methods=['POST'])
@login_required
def delete_testimonial(id):
    supabase_delete('testimonials', id)
    return redirect(url_for('admin.manage_testimonials'))

# ==================== EVENTS (CRUD) ====================
@admin_bp.route('/events', methods=['GET', 'POST'])
@login_required
def manage_events():
    message = None
    error = None
    
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        title = request.form.get('title')
        event_date = request.form.get('event_date')
        event_time = request.form.get('event_time')
        location = request.form.get('location')
        description = request.form.get('description')
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/events')
            image_url = result['url']
        
        data = {
            'title': title,
            'event_date': event_date,
            'event_time': event_time,
            'location': location,
            'description': description,
            'image_url': image_url
        }
        
        if event_id:
            supabase_update('events', int(event_id), data)
            message = "Event updated!"
        else:
            supabase_insert('events', data)
            message = "Event added!"
    
    events = supabase_get('events', {'order': 'event_date.asc'})
    return render_template('admin/events.html', events=events, message=message, error=error)

@admin_bp.route('/events/<int:event_id>/edit')
@login_required
def edit_event(event_id):
    event = supabase_get_one('events', event_id)
    events = supabase_get('events', {'order': 'event_date.asc'})
    return render_template('admin/events.html', events=events, edit_event=event)

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    supabase_delete('events', event_id)
    return redirect(url_for('admin.manage_events'))

# ==================== BLOG POSTS (CRUD) ====================
@admin_bp.route('/blog', methods=['GET', 'POST'])
@login_required
def manage_blog():
    message = None
    error = None
    
    if request.method == 'POST':
        post_id = request.form.get('post_id')
        title = request.form.get('title')
        slug = request.form.get('slug') or title.lower().replace(' ', '-')
        excerpt = request.form.get('excerpt')
        content = request.form.get('content')
        category = request.form.get('category', 'General')
        published = request.form.get('published') == 'on'
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            result = upload_image(image_file, folder='generation/blog')
            image_url = result['url']
        
        data = {
            'title': title,
            'slug': slug,
            'excerpt': excerpt,
            'content': content,
            'category': category,
            'published': published,
            'image_url': image_url
        }
        
        if post_id:
            supabase_update('blog_posts', int(post_id), data)
            message = "Post updated!"
        else:
            supabase_insert('blog_posts', data)
            message = "Post published!"
    
    posts = supabase_get('blog_posts', {'order': 'created_at.desc'})
    return render_template('admin/blog.html', posts=posts, message=message, error=error)

@admin_bp.route('/blog/<int:post_id>/edit')
@login_required
def edit_blog(post_id):
    post = supabase_get_one('blog_posts', post_id)
    posts = supabase_get('blog_posts', {'order': 'created_at.desc'})
    return render_template('admin/blog.html', posts=posts, edit_post=post)

@admin_bp.route('/blog/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_blog(post_id):
    supabase_delete('blog_posts', post_id)
    return redirect(url_for('admin.manage_blog'))

# ==================== NEWSLETTER ====================
@admin_bp.route('/newsletter', methods=['GET', 'POST'])
@login_required
def newsletter():
    message = None
    error = None
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        
        if subject and content:
            try:
                from brevo_client import send_newsletter_to_all
                result = send_newsletter_to_all(subject, content)
                if result:
                    message = "Newsletter sent successfully to all subscribers!"
                else:
                    error = "Failed to send. Check Brevo account limits."
            except Exception as e:
                error = f"Error: {str(e)}"
        else:
            error = "Subject and content are required."
    
    return render_template('admin/newsletter.html', message=message, error=error)

# ==================== CONTACT SUBMISSIONS ====================
@admin_bp.route('/messages')
@login_required
def messages():
    submissions = supabase_get('contact_submissions', {'order': 'created_at.desc'})
    return render_template('admin/messages.html', submissions=submissions)

@admin_bp.route('/messages/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    supabase_update('contact_submissions', id, {'is_read': True})
    return redirect(url_for('admin.messages'))

@admin_bp.route('/messages/<int:id>/delete', methods=['POST'])
@login_required
def delete_message(id):
    supabase_delete('contact_submissions', id)
    return redirect(url_for('admin.messages'))