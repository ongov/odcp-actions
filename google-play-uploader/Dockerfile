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
COPY upload.py .

# Run the script with the passed arguments
ENTRYPOINT ["python3", "upload.py"]

# Pass inputs from action.yml to the Python script as command-line arguments
CMD ["--service-account", "${{ inputs.service-account }}", "--bundle", "${{ inputs.bundle }}", "--package-name", "${{ inputs.package-name }}", "--timeout", "${{ inputs.timeout }}"]