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
    get_site_settings,
    get_ministries  
)
from cloudinary_client import upload_image, upload_audio

load_dotenv()

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'generation2026')

# ==================== TOAST HELPER ====================
def add_toast(response, message, type='success'):
    """Add toast message to response via cookie"""
    response.set_cookie('toast_message', message, max_age=5, path='/')
    response.set_cookie('toast_type', type, max_age=5, path='/')
    return response

def redirect_with_toast(endpoint, message, type='success', **kwargs):
    """Redirect with toast message cookie"""
    response = redirect(url_for(endpoint, **kwargs))
    response.set_cookie('toast_message', message, max_age=5, path='/')
    response.set_cookie('toast_type', type, max_age=5, path='/')
    return response

# ==================== LOGIN DECORATOR ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """Restrict access to specific roles. 'admin' can access everything."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return redirect(url_for('admin.login'))
            
            user = session.get('admin_user', {})
            user_roles = user.get('roles', [])
            
            # Admin role can access everything
            if 'admin' in user_roles:
                return f(*args, **kwargs)
            
            # Check if any of the user's roles match allowed roles
            for role in user_roles:
                if role in allowed_roles:
                    return f(*args, **kwargs)
            
            return redirect(url_for('admin.dashboard'))
        return decorated_function
    return decorator

# ==================== LOGIN ====================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Check against database
        users = supabase_get('admin_users', {'username': f'eq.{username}', 'is_active': 'eq.true'})
        
        if users and users[0]['password'] == password:
            user = users[0]
            
            # Parse roles from plain text field
            roles_str = user.get('roles', '')
            if roles_str:
                roles = [r.strip() for r in roles_str.split(',') if r.strip()]
            else:
                roles = [user.get('role', 'user')]
            
            session['admin_logged_in'] = True
            session['admin_user'] = {
                'id': user['id'],
                'username': user['username'],
                'display_name': user['display_name'],
                'role': roles[0] if roles else 'user',
                'roles': roles,
                'department': user.get('department', '')
            }
            return redirect_with_toast('admin.dashboard', f'Welcome back, {user["display_name"]}!', 'success')
        else:
            error = 'Invalid username or password.'
    
    return render_template('admin/login.html', error=error)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    response = redirect(url_for('admin.login'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return add_toast(response, 'You have been logged out.', 'info')

# ==================== DASHBOARD ====================
@admin_bp.route('/')
@login_required
def dashboard():
    # Check for toast cookies and display them
    toast_message = request.cookies.get('toast_message')
    toast_type = request.cookies.get('toast_type', 'success')
    return render_template('admin/dashboard.html', toast_message=toast_message, toast_type=toast_type)

# ==================== SITE SETTINGS ====================
@admin_bp.route('/settings', methods=['GET', 'POST'])
@role_required('admin')
def settings():
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
            'mandate': request.form.get('mandate'),
            'motto': request.form.get('motto'),
            'year_theme': request.form.get('year_theme'),
            'hero_tagline': request.form.get('hero_tagline'),
            'church_address': request.form.get('church_address'),
            'church_phone': request.form.get('church_phone'),
            'church_email': request.form.get('church_email'),
            'about_intro': request.form.get('about_intro'),
            'about_description': request.form.get('about_description'),
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
        
        return redirect_with_toast('admin.dashboard', 'Site settings saved successfully!', 'success')
    
    current_settings = get_site_settings()
    return render_template('admin/settings.html', settings=current_settings, error=error)

# ==================== PRAYER RHYTHMS ====================
@admin_bp.route('/prayer-rhythms', methods=['GET', 'POST'])
@role_required('admin')
def manage_prayer_rhythms():
    if request.method == 'POST':
        supabase_insert('prayer_rhythms', {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'icon': request.form.get('icon', 'fa-pray'),
            'schedule': request.form.get('schedule'),
            'display_order': int(request.form.get('display_order', 0))
        })
        return redirect_with_toast('admin.dashboard', 'Prayer rhythm added successfully!', 'success')
    
    rhythms = supabase_get('prayer_rhythms', {'order': 'display_order.asc'})
    return render_template('admin/prayer-rhythms.html', rhythms=rhythms)

@admin_bp.route('/prayer-rhythms/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_prayer_rhythm(id):
    supabase_delete('prayer_rhythms', id)
    return redirect_with_toast('admin.dashboard', 'Prayer rhythm deleted successfully.', 'success')

# ==================== FAMILY GROUPS ====================
@admin_bp.route('/family-groups', methods=['GET', 'POST'])
@role_required('admin')
def manage_family_groups():
    if request.method == 'POST':
        supabase_insert('family_groups', {
            'name': request.form.get('name'),
            'city': request.form.get('city'),
            'leader': request.form.get('leader'),
            'meeting_time': request.form.get('meeting_time'),
            'description': request.form.get('description'),
            'contact_email': request.form.get('contact_email')
        })
        return redirect_with_toast('admin.dashboard', 'Family group added successfully!', 'success')
    
    groups = supabase_get('family_groups', {'order': 'city.asc'})
    return render_template('admin/family-groups-manage.html', groups=groups)

@admin_bp.route('/family-groups/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_family_group(id):
    supabase_delete('family_groups', id)
    return redirect_with_toast('admin.dashboard', 'Family group deleted successfully.', 'success')

# ==================== MARKETPLACE ====================

@admin_bp.route('/marketplace', methods=['GET', 'POST'])
@role_required('admin')
def manage_marketplace():
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            try:
                result = upload_image(image_file, folder='generation/marketplace')
                image_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        
        data = {
            'title': request.form.get('title'),
            'category': request.form.get('category'),
            'description': request.form.get('description'),
            'price': request.form.get('price'),
            'seller_name': request.form.get('seller_name'),
            'seller_contact': request.form.get('seller_contact'),
            'image_url': image_url
        }
        
        if item_id:
            supabase_update('marketplace_items', int(item_id), data)
            return redirect_with_toast('admin.dashboard', 'Marketplace item updated!', 'success')
        else:
            supabase_insert('marketplace_items', data)
            return redirect_with_toast('admin.dashboard', 'Marketplace item added!', 'success')
    
    items = supabase_get('marketplace_items', {'order': 'created_at.desc'})
    return render_template('admin/marketplace-manage.html', items=items)

@admin_bp.route('/marketplace/<int:id>/edit')
@login_required
def edit_marketplace(id):
    item = supabase_get_one('marketplace_items', id)
    items = supabase_get('marketplace_items', {'order': 'created_at.desc'})
    return render_template('admin/marketplace-manage.html', items=items, edit_item=item)

@admin_bp.route('/marketplace/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_marketplace_item(id):
    supabase_delete('marketplace_items', id)
    return redirect_with_toast('admin.dashboard', 'Marketplace item deleted.', 'success')

# ==================== RETREATS ====================
@admin_bp.route('/retreats', methods=['GET', 'POST'])
@role_required('admin')
def manage_retreats():
    if request.method == 'POST':
        image_url = ''
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            try:
                result = upload_image(image_file, folder='generation/retreats')
                image_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        
        supabase_insert('retreats', {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'location': request.form.get('location'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'image_url': image_url,
            'is_upcoming': request.form.get('is_upcoming') == 'true'
        })
        return redirect_with_toast('admin.dashboard', 'Retreat added successfully!', 'success')
    
    retreats = supabase_get('retreats', {'order': 'start_date.desc'})
    return render_template('admin/retreats-manage.html', retreats=retreats)

@admin_bp.route('/retreats/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_retreat(id):
    supabase_delete('retreats', id)
    return redirect_with_toast('admin.dashboard', 'Retreat deleted.', 'success')

# ==================== SERMONS (CRUD) ====================
@admin_bp.route('/sermons', methods=['GET', 'POST'])
@role_required('admin', 'sermons')
def manage_sermons():
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
            try:
                result = upload_audio(audio_file, folder='generation/sermons')
                audio_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Audio upload failed: {str(e)}', 'error')
        
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
            
            # Send notification for new sermons
            try:
                from brevo_client import send_new_sermon_notification
                send_new_sermon_notification(title, speaker or 'The Generation Family', audio_url, description or '')
            except Exception as e:
                print(f"Sermon notification failed: {e}")
        
        return redirect_with_toast('admin.dashboard', message, 'success')
    
    sermons = supabase_get('sermons', {'order': 'date.desc'})
    return render_template('admin/sermons.html', sermons=sermons)

@admin_bp.route('/sermons/<int:sermon_id>/delete', methods=['POST'])
@login_required
def delete_sermon(sermon_id):
    supabase_delete('sermons', sermon_id)
    return redirect_with_toast('admin.dashboard', 'Sermon deleted.', 'success')

# ==================== LEADERSHIP (CRUD) ====================
@admin_bp.route('/leadership', methods=['GET', 'POST'])
@role_required('admin', 'leadership')
def manage_leadership():
    if request.method == 'POST':
        leader_id = request.form.get('leader_id')
        name = request.form.get('name')
        title = request.form.get('title')
        bio = request.form.get('bio')
        display_order = request.form.get('display_order', 0)
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            try:
                result = upload_image(image_file, folder='generation/leadership')
                image_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        
        data = {
            'name': name,
            'title': title,
            'bio': bio,
            'display_order': int(display_order),
            'image_url': image_url
        }
        
        if leader_id:
            supabase_update('leadership', int(leader_id), data)
            return redirect_with_toast('admin.dashboard', 'Leader updated!', 'success')
        else:
            supabase_insert('leadership', data)
            return redirect_with_toast('admin.dashboard', 'Leader added!', 'success')
    
    leaders = supabase_get('leadership', {'order': 'display_order.asc'})
    return render_template('admin/leadership.html', leaders=leaders)

@admin_bp.route('/leadership/<int:leader_id>/delete', methods=['POST'])
@login_required
def delete_leader(leader_id):
    supabase_delete('leadership', leader_id)
    return redirect_with_toast('admin.dashboard', 'Leader removed.', 'success')

# ==================== MINISTRIES (CRUD) ====================
@admin_bp.route('/ministries', methods=['GET', 'POST'])
@role_required('admin', 'ministries')
def manage_ministries():
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
            try:
                result = upload_image(image_file, folder='generation/ministries')
                image_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        
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
            return redirect_with_toast('admin.dashboard', 'Ministry updated!', 'success')
        else:
            supabase_insert('ministries', data)
            return redirect_with_toast('admin.dashboard', 'Ministry added!', 'success')
    
    ministries = supabase_get('ministries', {'order': 'display_order.asc'})
    return render_template('admin/ministries.html', ministries=ministries)

@admin_bp.route('/ministries/<int:ministry_id>/delete', methods=['POST'])
@login_required
def delete_ministry(ministry_id):
    supabase_delete('ministries', ministry_id)
    return redirect_with_toast('admin.dashboard', 'Ministry deleted.', 'success')

# ==================== TESTIMONIALS (CRUD) ====================
@admin_bp.route('/testimonials', methods=['GET', 'POST'])
@role_required('admin', 'testimonials')
def manage_testimonials():
    if request.method == 'POST':
        testimonial_id = request.form.get('testimonial_id')
        name = request.form.get('name')
        quote = request.form.get('quote')
        image_url = request.form.get('existing_image_url') or ''
        
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            try:
                result = upload_image(image_file, folder='generation/testimonials')
                image_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        
        data = {
            'name': name,
            'quote': quote,
            'image_url': image_url,
            'is_approved': True
        }
        
        if testimonial_id:
            supabase_update('testimonials', int(testimonial_id), data)
            return redirect_with_toast('admin.dashboard', 'Testimonial updated!', 'success')
        else:
            supabase_insert('testimonials', data)
            return redirect_with_toast('admin.dashboard', 'Testimonial added!', 'success')
    
    testimonials = supabase_get('testimonials', {'order': 'created_at.desc'})
    return render_template('admin/testimonials.html', testimonials=testimonials)

@admin_bp.route('/testimonials/<int:id>/delete', methods=['POST'])
@login_required
def delete_testimonial(id):
    supabase_delete('testimonials', id)
    return redirect_with_toast('admin.dashboard', 'Testimonial deleted.', 'success')

# ==================== EVENTS (CRUD) ====================
@admin_bp.route('/events', methods=['GET', 'POST'])
@role_required('admin', 'events')
def manage_events():
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
            try:
                result = upload_image(image_file, folder='generation/events')
                image_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        
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
            return redirect_with_toast('admin.dashboard', 'Event updated!', 'success')
        else:
            supabase_insert('events', data)
            return redirect_with_toast('admin.dashboard', 'Event added!', 'success')
    
    events = supabase_get('events', {'order': 'event_date.asc'})
    return render_template('admin/events.html', events=events)

@admin_bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    supabase_delete('events', event_id)
    return redirect_with_toast('admin.dashboard', 'Event deleted.', 'success')

# ==================== BLOG POSTS (CRUD) ====================
@admin_bp.route('/blog', methods=['GET', 'POST'])
@role_required('admin', 'blog')
def manage_blog():
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
            try:
                result = upload_image(image_file, folder='generation/blog')
                image_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        
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
            return redirect_with_toast('admin.dashboard', 'Blog post updated!', 'success')
        else:
            supabase_insert('blog_posts', data)
            return redirect_with_toast('admin.dashboard', 'Blog post published!', 'success')
    
    posts = supabase_get('blog_posts', {'order': 'created_at.desc'})
    return render_template('admin/blog.html', posts=posts)

@admin_bp.route('/blog/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_blog(post_id):
    supabase_delete('blog_posts', post_id)
    return redirect_with_toast('admin.dashboard', 'Blog post deleted.', 'success')

# ==================== NEWSLETTER ====================
@admin_bp.route('/newsletter', methods=['GET', 'POST'])
@role_required('admin')
def newsletter():
    if request.method == 'POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        
        if subject and content:
            try:
                from brevo_client import send_newsletter_to_all
                result = send_newsletter_to_all(subject, content)
                if result:
                    return redirect_with_toast('admin.dashboard', 'Newsletter sent to all subscribers!', 'success')
                else:
                    return redirect_with_toast('admin.dashboard', 'Failed to send. Check Brevo account limits.', 'error')
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Error: {str(e)}', 'error')
        else:
            return redirect_with_toast('admin.dashboard', 'Subject and content are required.', 'error')
    
    return render_template('admin/newsletter.html')

# ==================== CONTACT SUBMISSIONS ====================
@admin_bp.route('/messages')
@role_required('admin')
def messages():
    submissions = supabase_get('contact_submissions', {'order': 'created_at.desc'})
    return render_template('admin/messages.html', submissions=submissions)

@admin_bp.route('/messages/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    supabase_update('contact_submissions', id, {'is_read': True})
    return redirect_with_toast('admin.dashboard', 'Message marked as read.', 'success')

@admin_bp.route('/messages/<int:id>/delete', methods=['POST'])
@login_required
def delete_message(id):
    supabase_delete('contact_submissions', id)
    return redirect_with_toast('admin.dashboard', 'Message deleted.', 'success')

# ==================== HERO IMAGES ====================
@admin_bp.route('/hero', methods=['GET', 'POST'])
@role_required('admin')
def manage_hero():
    if request.method == 'POST':
        image_file = request.files.get('hero_image')
        if image_file and image_file.filename:
            try:
                result = upload_image(image_file, folder='generation/hero')
                supabase_insert('hero_images', {
                    'image_url': result['url'],
                    'public_id': result['public_id'],
                    'is_active': True
                })
                return redirect_with_toast('admin.dashboard', 'Hero image added!', 'success')
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        else:
            return redirect_with_toast('admin.dashboard', 'Please select an image.', 'error')
    
    hero_images = supabase_get('hero_images', {'order': 'created_at.desc'})
    return render_template('admin/hero.html', hero_images=hero_images)

@admin_bp.route('/hero/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_hero_image(id):
    supabase_delete('hero_images', id)
    return redirect_with_toast('admin.dashboard', 'Hero image deleted.', 'success')

# ==================== CREATIVES MANAGEMENT ====================
@admin_bp.route('/creatives', methods=['GET', 'POST'])
@role_required('admin', 'creatives')
def manage_creatives():
    if request.method == 'POST':
        section = request.form.get('section')
        title = request.form.get('title')
        description = request.form.get('description')
        content_url = request.form.get('content_url') or ''
        
        upload_file = request.files.get('content_file')
        if upload_file and upload_file.filename:
            try:
                result = upload_image(upload_file, folder=f'generation/creatives/{section}')
                content_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        
        supabase_insert('creatives', {
            'section': section,
            'title': title,
            'description': description,
            'content_url': content_url
        })
        return redirect_with_toast('admin.dashboard', 'Creative content added!', 'success')
    
    creatives = supabase_get('creatives', {'order': 'created_at.desc'})
    return render_template('admin/creatives.html', creatives=creatives)

@admin_bp.route('/creatives/<int:id>/delete', methods=['POST'])
@role_required('admin', 'creatives')
def delete_creative(id):
    supabase_delete('creatives', id)
    return redirect_with_toast('admin.dashboard', 'Creative content deleted.', 'success')

# ==================== SECTION IMAGES ====================
# ==================== SECTION IMAGES ====================
@admin_bp.route('/section-images', methods=['GET', 'POST'])
@role_required('admin')
def manage_section_images():
    if request.method == 'POST':
        section = request.form.get('section')
        image_file = request.files.get('image')
        
        if not section:
            return redirect_with_toast('admin.dashboard', 'Section name is required.', 'error')
        
        if not image_file or not image_file.filename:
            return redirect_with_toast('admin.dashboard', 'Please select an image file.', 'error')
        
        try:
            result = upload_image(image_file, folder='generation/sections')
            image_url = result['url']
            
            existing = supabase_get('section_images', {'section_name': f'eq.{section}'})
            if existing:
                supabase_update('section_images', existing[0]['id'], {'image_url': image_url})
                message = f'Image for "{section}" updated successfully!'
            else:
                supabase_insert('section_images', {'section_name': section, 'image_url': image_url})
                message = f'Image for "{section}" added successfully!'
            
            return redirect_with_toast('admin.dashboard', message, 'success')
            
        except ValueError as e:
            return redirect_with_toast('admin.dashboard', f'Invalid file: {str(e)}', 'error')
        except Exception as e:
            return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
    
    # GET request - show the form page
    images = supabase_get('section_images')
    return render_template('admin/section-images.html', images=images)

@admin_bp.route('/section-images/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_section_image(id):
    try:
        supabase_delete('section_images', id)
        return redirect_with_toast('admin.dashboard', 'Section image deleted successfully.', 'success')
    except Exception as e:
        return redirect_with_toast('admin.dashboard', f'Delete failed: {str(e)}', 'error')
    
@admin_bp.route('/testimonials/<int:id>/edit')
@login_required
def edit_testimonial(id):
    testimonial = supabase_get_one('testimonials', id)
    testimonials = supabase_get('testimonials', {'order': 'created_at.desc'})
    return render_template('admin/testimonials.html', testimonials=testimonials, edit_testimonial=testimonial)

# ==================== MINISTRY CONTENT EDITOR ====================
@admin_bp.route('/ministry-content/<slug>', methods=['GET', 'POST'])
@login_required
def manage_ministry_content(slug):
    ministries = supabase_get('ministries', {'slug': f'eq.{slug}'})
    ministry = ministries[0] if ministries else None
    
    if not ministry:
        flash('Ministry not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    content = supabase_get('ministry_content', {'ministry_slug': f'eq.{slug}'})
    current_content = content[0]['content'] if content else ''
    attachments = supabase_get('ministry_attachments', {'ministry_slug': f'eq.{slug}', 'order': 'created_at.desc'})
    
    if request.method == 'POST':
        new_content = request.form.get('content', '')
        if content:
            supabase_update('ministry_content', content[0]['id'], {'content': new_content})
        else:
            supabase_insert('ministry_content', {'ministry_slug': slug, 'content': new_content})
        flash('Content updated!', 'success')
        return redirect(url_for('admin.manage_ministry_content', slug=slug))
    
    return render_template('admin/ministry-content.html', 
                         ministry=ministry, 
                         content=current_content,
                         attachments=attachments)
    
@admin_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image_endpoint():
    file = request.files.get('file')
    if file and file.filename:
        try:
            result = upload_image(file, folder='generation/content')
            return jsonify({'location': result['url']})
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return jsonify({'error': 'No file'}), 400

@admin_bp.route('/ministry-content/<slug>/upload-file', methods=['POST'])
@login_required
def upload_ministry_file(slug):
    file = request.files.get('file')
    file_name = request.form.get('file_name', 'File')
    
    if file and file.filename:
        try:
            # Determine file type
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if ext in ['mp3', 'wav', 'm4a', 'aac']:
                result = upload_audio(file, folder=f'generation/ministries/{slug}')
                file_type = 'audio'
            elif ext in ['pdf']:
                result = upload_image(file, folder=f'generation/ministries/{slug}')
                file_type = 'pdf'
            elif ext in ['doc', 'docx']:
                result = upload_image(file, folder=f'generation/ministries/{slug}')
                file_type = 'document'
            else:
                result = upload_image(file, folder=f'generation/ministries/{slug}')
                file_type = 'image' if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp'] else 'other'
            
            supabase_insert('ministry_attachments', {
                'ministry_slug': slug,
                'file_name': file_name,
                'file_url': result['url'],
                'file_type': file_type
            })
            flash('File uploaded!', 'success')
        except Exception as e:
            flash(f'Upload failed: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_ministry_content', slug=slug))

@admin_bp.route('/ministry-content/<slug>/delete-file/<int:file_id>', methods=['POST'])
@login_required
def delete_ministry_file(slug, file_id):
    supabase_delete('ministry_attachments', file_id)
    flash('File removed.', 'success')
    return redirect(url_for('admin.manage_ministry_content', slug=slug))

# ==================== STORY SECTIONS ====================
@admin_bp.route('/story-sections', methods=['GET', 'POST'])
@role_required('admin')
def manage_story():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        display_order = request.form.get('display_order', 0)
        supabase_insert('story_sections', {
            'title': title,
            'content': content,
            'display_order': int(display_order)
        })
        return redirect_with_toast('admin.dashboard', 'Story section added!', 'success')
    
    sections = supabase_get('story_sections', {'order': 'display_order.asc'})
    return render_template('admin/story-sections.html', sections=sections)

@admin_bp.route('/story-sections/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_story(id):
    supabase_delete('story_sections', id)
    return redirect_with_toast('admin.dashboard', 'Story section deleted.', 'success')

# ==================== GIVING INFO ====================
@admin_bp.route('/giving-info', methods=['GET', 'POST'])
@role_required('admin')
def manage_giving():
    if request.method == 'POST':
        method = request.form.get('method')
        details = request.form.get('details')
        icon = request.form.get('icon', 'fa-hand-holding-heart')
        display_order = request.form.get('display_order', 0)
        supabase_insert('giving_info', {
            'method': method,
            'details': details,
            'icon': icon,
            'display_order': int(display_order)
        })
        return redirect_with_toast('admin.dashboard', 'Giving method added!', 'success')
    
    methods = supabase_get('giving_info', {'order': 'display_order.asc'})
    return render_template('admin/giving-info.html', methods=methods)

@admin_bp.route('/giving-info/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_giving(id):
    supabase_delete('giving_info', id)
    return redirect_with_toast('admin.dashboard', 'Giving method deleted.', 'success')

# ==================== FAQS ====================
@admin_bp.route('/faqs-manage', methods=['GET', 'POST'])
@role_required('admin')
def manage_faqs():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        display_order = request.form.get('display_order', 0)
        supabase_insert('faqs', {
            'question': question,
            'answer': answer,
            'display_order': int(display_order)
        })
        return redirect_with_toast('admin.dashboard', 'FAQ added!', 'success')
    
    faqs = supabase_get('faqs', {'order': 'display_order.asc'})
    return render_template('admin/faqs-manage.html', faqs=faqs)

@admin_bp.route('/faqs-manage/<int:id>/delete', methods=['POST'])
@role_required('admin')
def delete_faq(id):
    supabase_delete('faqs', id)
    return redirect_with_toast('admin.dashboard', 'FAQ deleted.', 'success')

# ==================== MEDIA MANAGEMENT ====================
@admin_bp.route('/media', methods=['GET', 'POST'])
@role_required('admin', 'media')
def manage_media():
    if request.method == 'POST':
        media_type = request.form.get('media_type')
        title = request.form.get('title')
        description = request.form.get('description')
        media_url = request.form.get('media_url') or ''
        
        upload_file = request.files.get('media_file')
        if upload_file and upload_file.filename:
            try:
                if media_type == 'audio':
                    result = upload_audio(upload_file, folder='generation/media/audio')
                else:
                    result = upload_image(upload_file, folder='generation/media/images')
                media_url = result['url']
            except Exception as e:
                return redirect_with_toast('admin.dashboard', f'Upload failed: {str(e)}', 'error')
        
        supabase_insert('media', {
            'media_type': media_type,
            'title': title,
            'description': description,
            'media_url': media_url
        })
        return redirect_with_toast('admin.dashboard', 'Media added!', 'success')
    
    media_items = supabase_get('media', {'order': 'created_at.desc'})
    return render_template('admin/media.html', media_items=media_items)

@admin_bp.route('/media/<int:id>/delete', methods=['POST'])
@role_required('admin', 'media')
def delete_media(id):
    supabase_delete('media', id)
    return redirect_with_toast('admin.dashboard', 'Media deleted.', 'success')

# ==================== USER MANAGEMENT ====================
@admin_bp.route('/users', methods=['GET', 'POST'])
@role_required('admin')
def manage_users():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            display_name = request.form.get('display_name')
            department = request.form.get('department', '')
            roles = request.form.getlist('roles')
            roles_string = ','.join(roles) if roles else 'user'
            primary_role = roles[0] if roles else 'user'
            
            supabase_insert('admin_users', {
                'username': username,
                'password': password,
                'display_name': display_name,
                'role': primary_role,
                'roles': roles_string,
                'department': department,
                'is_active': True
            })
            return redirect_with_toast('admin.dashboard', f'User {display_name} added!', 'success')
        
        elif action == 'toggle':
            user_id = request.form.get('user_id')
            user = supabase_get_one('admin_users', int(user_id))
            if user:
                supabase_update('admin_users', int(user_id), {'is_active': not user['is_active']})
                status = 'disabled' if user['is_active'] else 'enabled'
                return redirect_with_toast('admin.dashboard', f'User {status}.', 'success')
        
        elif action == 'delete':
            user_id = request.form.get('user_id')
            current_user_id = session.get('admin_user', {}).get('id')
            
            if int(user_id) == current_user_id:
                return redirect_with_toast('admin.dashboard', 'You cannot delete your own account.', 'error')
            
            supabase_delete('admin_users', int(user_id))
            return redirect_with_toast('admin.dashboard', 'User removed.', 'success')
    
    users = supabase_get('admin_users', {'order': 'created_at.asc'})
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/edit', methods=['POST'])
@role_required('admin')
def edit_user(user_id):
    password = request.form.get('password')
    if password:
        supabase_update('admin_users', user_id, {'password': password})
        return redirect_with_toast('admin.dashboard', 'Password updated.', 'success')
    return redirect_with_toast('admin.dashboard', 'No password provided.', 'error')