FROM python:3.6.3

RUN pip install wget  # Lighter weight than the binary

# This gives us a layer with most dependencies cached.
RUN python -m wget https://raw.githubusercontent.com/refinery-platform/heatmap-scatter-dash/v0.1.0/context/requirements.txt
RUN pip install -r requirements.txt

# Now only the dependencies which have changed need to be downloaded.
COPY . .
RUN pip install -r requirements.txt

VOLUME data  # Can be mounted to pass in data, but not required.
CMD ["python", "app_runner_refinery.py", "--html_error", "--input", "/data/input.json"]
EXPOSE 80