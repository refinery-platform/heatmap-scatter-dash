FROM python:3.6.3

RUN pip install wget  # Lighter weight than the binary

# This gives us a layer with most dependencies cached.
RUN python -m wget https://raw.githubusercontent.com/refinery-platform/heatmap-scatter-dash/v0.1.0/context/requirements.txt
RUN pip install -r requirements.txt

# Now only the dependencies which have changed need to be downloaded.
COPY . .
RUN pip install -r requirements.txt

# The /data directory can be mounted to pass inputs, but not required:
# If not present, falls back to INPUT_JSON and INPUT_JSON_URL.
VOLUME data
CMD ["python", "app_runner_refinery.py", "--input", "/data/input.json"]
EXPOSE 80