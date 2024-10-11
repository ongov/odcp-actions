import os
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import sys

# Main script logic
def main():
    # Retrieve parameters from environment variables
    service_account_json = os.getenv('INPUT_SERVICE_ACCOUNT')
    aab_file_path = os.getenv('INPUT_BUNDLE')
    package_name = os.getenv('INPUT_PACKAGE_NAME')
    timeout = int(os.getenv('INPUT_TIMEOUT', 300))  # Default timeout to 120 seconds if not provided

    # Check if required environment variables are present
    if not service_account_json or not aab_file_path or not package_name:
        print("Error: Missing required environment variables.")
        sys.exit(1)

    # Validate JSON input for service account
    try:
        service_account_info = json.loads(service_account_json)
    except json.JSONDecodeError:
        print("Error: Invalid service account JSON")
        sys.exit(1)

    print("Starting Google Play AAB upload script...")

    # Step 1: Authenticate using the service account
    print("Authenticating using service account credentials...")
    try:
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/androidpublisher']
        )
        print("Authentication successful.")
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        sys.exit(1)

    # Step 2: Build the Google Play API service
    print("Building Google Play API client...")
    try:
        service = build('androidpublisher', 'v3', credentials=credentials)
        print("Google Play API client built successfully.")
    except Exception as e:
        print(f"Failed to build Google Play API client: {e}")
        sys.exit(1)

    # Step 3: Start a new edit transaction
    print("Starting a new edit transaction...")
    try:
        edit_request = service.edits().insert(body={}, packageName=package_name)
        edit_response = edit_request.execute()
        edit_id = edit_response['id']
        print(f"Edit transaction started successfully. Edit ID: {edit_id}")
    except Exception as e:
        print(f"Failed to start edit transaction: {e}")
        sys.exit(1)

    # Step 4: Upload the AAB file
    print(f"Uploading AAB file from {aab_file_path} as draft...")
    try:
        media = MediaFileUpload(aab_file_path, mimetype='application/octet-stream')
        aab_upload_request = service.edits().bundles().upload(
            editId=edit_id,
            packageName=package_name,
            media_body=media
        )
        aab_upload_response = aab_upload_request.execute()
        version_code = aab_upload_response['versionCode']
        print(f"AAB uploaded successfully. Version code: {version_code}")
    except Exception as e:
        print(f"Failed to upload AAB: {e}")
        sys.exit(1)

    # Step 5: Assign the AAB to the internal track as a draft
    print("Assigning AAB to the internal track as draft...")
    try:
        track_request = service.edits().tracks().update(
            editId=edit_id,
            track='internal',
            packageName=package_name,
            body={'releases': [{
                'name': 'Internal Test Release',
                'versionCodes': [version_code],
                'status': 'draft'  # Set the status to draft
            }]}
        )
        track_response = track_request.execute()
        print("AAB assigned to internal track successfully.")
    except Exception as e:
        print(f"Failed to assign AAB to internal track: {e}")
        sys.exit(1)

    # Step 6: Commit the transaction
    print("Committing the transaction...")
    try:
        commit_request = service.edits().commit(
            editId=edit_id,
            packageName=package_name
        )
        commit_response = commit_request.execute()
        print("Transaction committed successfully.")
    except Exception as e:
        print(f"Failed to commit the transaction: {e}")
        sys.exit(1)

    print("AAB upload and track assignment completed successfully.")

# Run the main function
if __name__ == '__main__':
    main()