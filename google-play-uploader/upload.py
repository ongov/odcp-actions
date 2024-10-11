import sys
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time

# Main script logic
def main():
    # Extract arguments from the command-line
    if len(sys.argv) < 4:
        print("Error: Missing required arguments.")
        print("Usage: python upload.py <service-account-file> <bundle> <package-name> [<timeout>]")
        exit(1)

    service_account_file_path = sys.argv[1]
    aab_file_path = sys.argv[2]
    package_name = sys.argv[3]
    timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 120  # Default timeout is 120 seconds if not provided

    # Validate the existence of the service account file
    if not service_account_file_path or not os.path.exists(service_account_file_path):
        print(f"Error: Service account file '{service_account_file_path}' not found.")
        exit(1)

    # Read service account JSON from the file
    try:
        with open(service_account_file_path, 'r') as f:
            service_account_info = json.load(f)
    except json.JSONDecodeError:
        print("Error: Invalid service account JSON")
        exit(1)
    except Exception as e:
        print(f"Error: Failed to read service account file: {e}")
        exit(1)

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
        exit(1)

    # Step 2: Build the Google Play API service
    print("Building Google Play API client...")
    try:
        service = build('androidpublisher', 'v3', credentials=credentials)
        print("Google Play API client built successfully.")
    except Exception as e:
        print(f"Failed to build Google Play API client: {e}")
        exit(1)

    # Step 3: Start a new edit transaction
    print("Starting a new edit transaction...")
    try:
        edit_request = service.edits().insert(body={}, packageName=package_name)
        edit_response = edit_request.execute()
        edit_id = edit_response['id']
        print(f"Edit transaction started successfully. Edit ID: {edit_id}")
    except Exception as e:
        print(f"Failed to start edit transaction: {e}")
        exit(1)

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
        exit(1)

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
        exit(1)

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
        exit(1)

    print("AAB upload and track assignment completed successfully.")

# Run the main function
if __name__ == '__main__':
    main()