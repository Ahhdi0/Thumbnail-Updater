# Privacy Policy for YouTube Thumbnail Updater

**Last Updated:** 11/13/26

## 1. Overview
YouTube Thumbnail Updater is an automated utility designed to update YouTube video titles and thumbnails on a scheduled basis. This Privacy Policy explains how the Application accesses, uses, and protects user data obtained through Google APIs.

## 2. Information We Access
When authorized via Google OAuth 2.0, the Application requests access to the following YouTube account data:
* **YouTube Account & Video Management (`youtube.force-ssl` / `youtube`):** Used strictly to read video metadata and upload/update video thumbnails and titles for the authorized channel.

## 3. How We Use Your Information
The accessed data is used exclusively to:
* Authenticate with the YouTube Data API v3 on behalf of the authorized account owner.
* Automatically update designated video titles and thumbnails using assets stored in the owner's private Google Cloud Storage bucket.

## 4. Data Storage and Security
* **No External Data Collection:** The Application does not collect, store, or transmit personal user data, video analytics, or channel information to any third-party servers or external databases.
* **Credential Protection:** OAuth refresh tokens and client credentials are stored securely within private Google Cloud Function environment variables and are never exposed publicly.

## 5. Data Sharing and Disclosure
We do not sell, trade, rent, or share any user data or Google API access tokens with third parties.

## 6. Revoking Access
You can revoke the Application's access to your YouTube account at any time by visiting your [Google Account Permissions](https://myaccount.google.com/permissions) page and removing access for this project.

## 7. Contact Information
If you have any questions about this Privacy Policy, please contact:
* **Developer:** Ahhdi0 (GitHub)
