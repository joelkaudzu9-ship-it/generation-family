from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from supabase_client import (
    get_leadership,
    get_ministries,
    get_sermons,
    get_testimonials,
    get_events,
    get_site_settings,
    get_blog_posts,
    get_prayer_rhythms,
    get_family_groups,
    get_marketplace_items,
    get_retreats,
    get_creatives,
    get_media,
    get_section_images,
    supabase_insert,
    supabase_get,
    get_story_sections,
    get_giving_info,
    get_faqs
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
    return {
        'settings': get_site_settings(),
        'section_images': get_section_images()
    }

@app.template_filter('linebreaks')
def linebreaks_filter(value):
    """Convert newlines to <br> tags, preserve paragraphs"""
    if not value:
        return ''
    # Split into paragraphs by double newlines
    paragraphs = value.split('\n\n')
    result = []
    for para in paragraphs:
        if para.strip():
            # Replace single newlines with <br> inside paragraph
            para = para.replace('\n', '<br>')
            result.append(f'<p>{para}</p>')
    return ''.join(result)

@app.route('/')
def home():
    settings = get_site_settings()
    leadership = get_leadership()
    ministries = get_ministries()
    testimonials = get_testimonials()
    hero_images = supabase_get('hero_images', {'is_active': 'eq.true', 'order': 'created_at.desc'})
    events = get_events()
    
    # Get the next upcoming event
    next_event = events[0] if events else None
    
    return render_template(
        'index.html',
        settings=settings,
        leadership=leadership,
        ministries=ministries,
        testimonials=testimonials,
        hero_images=hero_images,
        next_event=next_event
    )



@app.route('/podcast.xml')
def podcast_rss():
    sermons_list = get_sermons()
    settings = get_site_settings()
    
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
    <title>The Generation Family Sermons</title>
    <link>https://generation-family.onrender.com</link>
    <description>Life-changing messages from The Generation Family. A spiritual and growth family raising a generation rooted in faith.</description>
    <language>en</language>
    <itunes:author>The Generation Family</itunes:author>
    <itunes:owner>
    <itunes:email>joelkaudzu9@gmail.com</itunes:email>
    <itunes:name>The Generation Family</itunes:name>
    </itunes:owner>
    <itunes:summary>{settings.get('hero_tagline', 'A Spiritual & Growth Family')}</itunes:summary>
    <itunes:image href="{url_for('static', filename='images/og-image.jpg', _external=True)}"/>
    <itunes:category text="Religion &amp; Spirituality"/>
    <itunes:category text="Christianity"/>
    <itunes:explicit>no</itunes:explicit>
'''
    
    for sermon in sermons_list:
        if sermon.get('audio_url'):
            pub_date = sermon.get('date', '')
            rss += f'''
    <item>
        <title>{sermon.get('title', 'Sermon')}</title>
        <description>{sermon.get('description', '')}</description>
        <itunes:summary>{sermon.get('description', '')}</itunes:summary>
        <itunes:author>{sermon.get('speaker', 'The Generation Family')}</itunes:author>
        <enclosure url="{sermon.get('audio_url')}" length="0" type="audio/mpeg"/>
        <guid>{sermon.get('audio_url')}</guid>
        <pubDate>{pub_date}</pubDate>
    </item>'''
    
    rss += '''
</channel>
</rss>'''
    
    response = make_response(rss)
    response.headers['Content-Type'] = 'application/xml'
    return response

# ==================== ABOUT ====================
@app.route('/about')
def about():
    settings = get_site_settings()
    leadership = get_leadership()
    return render_template('about.html', settings=settings, leadership=leadership)

@app.route('/story')
def story():
    sections = get_story_sections()
    return render_template('story.html', story_sections=sections)

@app.route('/giving')
def giving():
    giving_methods = get_giving_info()
    return render_template('giving.html', giving_methods=giving_methods)

@app.route('/faqs')
def faqs():
    faqs = get_faqs()
    return render_template('faqs.html', faqs=faqs)

# ==================== MINISTRIES ====================
@app.route('/ministries')
def ministries():
    ministries = get_ministries()
    return render_template('ministries.html', ministries=ministries)


@app.route('/ministries/<slug>')
def ministry_detail(slug):
    from supabase_client import get_ministries, supabase_get
    
    ministries = get_ministries()
    ministry = next((m for m in ministries if m['slug'] == slug), None)
    
    if not ministry:
        return render_template('404.html'), 404
    
    # Get ministry content
    content_records = supabase_get('ministry_content', {'ministry_slug': f'eq.{slug}'})
    ministry_title = content_records[0]['title'] if content_records else None
    ministry_content = content_records[0]['content'] if content_records else None
    
    # Get attachments
    attachments = supabase_get('ministry_attachments', {'ministry_slug': f'eq.{slug}', 'order': 'created_at.desc'})
    
    return render_template('ministry-detail.html', 
                         ministry=ministry, 
                         ministry_title=ministry_title,
                         ministry_content=ministry_content,
                         attachments=attachments)


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



# ==================== PRAYER RHYTHMS ====================
@app.route('/prayer-rhythms')
def prayer_rhythms():
    rhythms = get_prayer_rhythms()
    return render_template('prayer-rhythms.html', rhythms=rhythms)

# ==================== FAMILY GROUPS ====================
@app.route('/family-groups')
def family_groups():
    groups = get_family_groups()
    return render_template('family-groups.html', groups=groups)

# ==================== MARKETPLACE ====================
@app.route('/marketplace')
def marketplace():
    items = get_marketplace_items()
    return render_template('marketplace.html', items=items)

# ==================== RETREATS ====================
@app.route('/retreats')
def retreats():
    retreats = get_retreats()
    return render_template('retreats.html', retreats=retreats)

# ==================== CREATIVES ====================
@app.route('/creatives')
def creatives():
    creatives = get_creatives()
    return render_template('creatives.html', creatives=creatives)

# ==================== RESOURCES ====================
@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/resources/canvas')
def resources_canvas():
    return render_template('canvas.html')

@app.route('/resources/tgf-music')
def tgf_music():
    music = get_creatives(section='music')
    return render_template('tgf-music.html', items=music)

@app.route('/resources/tgf-drama')
def tgf_drama():
    drama = get_creatives(section='drama')
    return render_template('tgf-drama.html', items=drama)

@app.route('/resources/tgf-poems')
def tgf_poems():
    poems = get_creatives(section='poems')
    return render_template('tgf-poems.html', items=poems)

@app.route('/resources/sermons-mp3')
def sermons_mp3():
    sermons_list = get_sermons()
    return render_template('sermons-mp3.html', sermons=sermons_list)

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/resources/media')
def resources_media():
    media_items = get_media()
    return render_template('media.html', media_items=media_items)

@app.route('/resources/apparel')
def apparel():
    apparel_items = get_marketplace_items()
    return render_template('apparel.html', items=apparel_items)

@app.route('/resources/books')
def books():
    books_items = get_marketplace_items()
    return render_template('books.html', items=books_items)

@app.route('/blog')
def blog():
    posts = get_blog_posts()
    return render_template('blog.html', posts=posts)

# ==================== BLOG ====================
@app.route('/blog/<slug>')
def blog_post(slug):
    posts = supabase_get('blog_posts', {'slug': f'eq.{slug}', 'published': 'eq.true'})
    post = posts[0] if posts else None
    if not post:
        return render_template('404.html'), 404
    recent_posts = supabase_get('blog_posts', {'published': 'eq.true', 'order': 'created_at.desc', 'limit': '3'})
    return render_template('blog-detail.html', post=post, recent_posts=recent_posts)


# ==================== TESTIMONIALS PAGE ====================
# PHASE 4: Added /testimonials route
@app.route('/testimonials')
def testimonies_page():
    testimonials = get_testimonials()
    return render_template('testimonials-page.html', testimonials=testimonials)


# ==================== LEADERSHIP PAGE ====================
# PHASE 4: Added /leadership route
@app.route('/leadership')
def leadership_page():
    leaders = get_leadership()
    return render_template('leadership-page.html', leaders=leaders)


# ==================== CONTACT ====================
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    settings = get_site_settings()
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        supabase_insert('contact_submissions', {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        })
        
        try:
            from brevo_client import send_contact_notification
            send_contact_notification(name, email, subject, message)
        except Exception as e:
            print(f"Brevo failed: {e}")
        
        return redirect(url_for('contact') + '?success=1')
    
    success = request.args.get('success') == '1'
    return render_template('contact.html', settings=settings, success=success)





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