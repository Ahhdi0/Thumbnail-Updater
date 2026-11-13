import os
import random
import io
import google.auth
from google.cloud import storage
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials

# Environment variables you will set in Cloud Functions
BUCKET_NAME = os.environ.get("BUCKET_NAME")
VIDEO_ID = os.environ.get("VIDEO_ID")
REFRESH_TOKEN = os.environ.get("YT_REFRESH_TOKEN")
CLIENT_ID = os.environ.get("YT_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YT_CLIENT_SECRET")

STATE_FILE_NAME = "history.txt"

def get_history(bucket):
    """Retrieve the recent selection history from GCS state file."""
    blob = bucket.blob(STATE_FILE_NAME)
    if blob.exists():
        try:
            content = blob.download_as_text().strip()
            if content:
                return [int(x) for x in content.split(",") if x.isdigit()]
        except Exception:
            return []
    return []

def save_history(bucket, history_list):
    """Save the updated selection history to GCS state file."""
    blob = bucket.blob(STATE_FILE_NAME)
    blob.upload_from_string(",".join(map(str, history_list)))

def rotate_youtube_metadata(request):
    try:
        # 1. Initialize GCS client and bucket
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        
        # Retrieve recent history to prevent repetition in the last two runs
        recent_history = get_history(bucket)

        # Define sets (1 to 5) and percentage-based weights
        sets = [1, 2, 3, 4, 5]
        weights = [0.30, 0.30, 0.30, 0.05, 0.05]

        # Filter out sets present in the recent history
        available_items = [
            (s, w) for s, w in zip(sets, weights) 
            if s not in recent_history
        ]
        
        available_sets = [item[0] for item in available_items]
        available_weights = [item[1] for item in available_items]

        # Pick the next set using weighted random choice
        set_index = random.choices(available_sets, weights=available_weights, k=1)[0]

        # Update history (keep most recent first, max length 2)
        recent_history.insert(0, set_index)
        recent_history = recent_history[:2]

        # Save the updated history back to GCS for the next run
        save_history(bucket, recent_history)

        image_filename = f"set_{set_index}.png"
        text_filename = f"set_{set_index}.txt"

        # 2. Pull assets from GCS
        # Get Title
        text_blob = bucket.blob(text_filename)
        new_title = text_blob.download_as_text().strip()

        # Get Image Bytes
        image_blob = bucket.blob(image_filename)
        image_bytes = image_blob.download_as_bytes()

        # 3. Authenticate with YouTube Data API v3 using OAuth Credentials
        creds = Credentials(
            token=None,
            refresh_token=REFRESH_TOKEN,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token"
        )

        youtube = build("youtube", "v3", credentials=creds)

        # 4. Update Video Title
        video_response = youtube.videos().list(
            part="snippet",
            id=VIDEO_ID
        ).execute()

        if not video_response.get("items"):
            return f"Video ID {VIDEO_ID} not found.", 404

        snippet = video_response["items"][0]["snippet"]
        snippet["title"] = new_title

        youtube.videos().update(
            part="snippet",
            body={
                "id": VIDEO_ID,
                "snippet": snippet
            }
        ).execute()

        # 5. Update Video Thumbnail
        media = MediaIoBaseUpload(io.BytesIO(image_bytes), mimetype="image/png", resumable=True)
        youtube.thumbnails().set(
            videoId=VIDEO_ID,
            media_body=media
        ).execute()

        success_msg = f"Successfully updated video to Set {set_index}! Title: '{new_title}'"
        print(success_msg)
        return success_msg, 200

    except Exception as e:
        import traceback
        error_msg = f"ERROR: Failed to update metadata: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return error_msg, 500