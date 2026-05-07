import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def upload_image(file, folder="generation", public_id=None):
    """Upload an image to Cloudinary. 'file' can be a path, URL, or file object."""
    options = {
        'folder': folder,
        'resource_type': 'image',
        'transformation': [
            {'quality': 'auto', 'fetch_format': 'auto'}
        ]
    }
    if public_id:
        options['public_id'] = public_id

    result = cloudinary.uploader.upload(file, **options)
    return {
        'url': result['secure_url'],
        'public_id': result['public_id'],
        'width': result['width'],
        'height': result['height']
    }

def upload_audio(file, folder="generation/sermons", public_id=None):
    """Upload an MP3 sermon to Cloudinary."""
    options = {
        'folder': folder,
        'resource_type': 'video',  # Cloudinary treats audio as video type
        'format': 'mp3'
    }
    if public_id:
        options['public_id'] = public_id

    result = cloudinary.uploader.upload(file, **options)
    return {
        'url': result['secure_url'],
        'public_id': result['public_id'],
        'duration': result.get('duration', 0)
    }

def delete_upload(public_id, resource_type='image'):
    """Delete a file from Cloudinary by public_id."""
    result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
    return result.get('result') == 'ok'

def get_optimized_url(public_id, width=400, height=400, crop='fill'):
    """Generate an optimized image URL with transformations."""
    url = cloudinary.CloudinaryImage(public_id).build_url(
        width=width,
        height=height,
        crop=crop,
        gravity='face',
        quality='auto',
        fetch_format='auto'
    )
    return url