import argparse
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time

# Function to parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Upload an AAB file to Google Play.')

    # Define the arguments
    parser.add_argument('--service-account', required=True, type=str,
                        help='Service account JSON credentials as a string.')
    parser.add_argument('--bundle', required=True, type=str,
                        help='Path to the AAB file to upload.')
    parser.add_argument('--package-name', required=True, type=str,
                        help='Package name of the Android app.')
    parser.add_argument('--timeout', required=False, type=int, default=120,
                        help='Timeout in seconds for HTTP requests (default is 120 seconds).')

    return parser.parse_args()

# Main script logic
def main():
    # Parse the command line arguments
    args = parse_args()

    # Extract command-line arguments
    service_account_info = json.loads(args.service_account)
    aab_file_path = args.bundle
    package_name = args.package_name
    timeout = args.timeout

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