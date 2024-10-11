FROM google/cloud-sdk
RUN apt-get update && \
    apt-get install -y \
    curl \
    nano \
    wget \
    unzip \
    gradle \
    nodejs

RUN pip install --no-cache google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client httplib2

WORKDIR /app

# Copy the Python script into the container
COPY upload.py /app/upload.py

# Run the script with the passed arguments
ENTRYPOINT ["python3", "/app/upload.py"]