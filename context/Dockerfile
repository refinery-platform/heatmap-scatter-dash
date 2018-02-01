FROM python:3.6.3

RUN pip install pipenv wget  # Python wget is more light-weight than the binary.

# This gives us a layer with most dependencies cached.
RUN python -m wget https://raw.githubusercontent.com/refinery-platform/heatmap-scatter-dash/v0.0.15/context/Pipfile.lock
RUN pipenv install

# Now only the dependencies which have changed need to be downloaded.
COPY . .
RUN pipenv install

VOLUME data

CMD ["python", "app_runner_refinery.py", "--input", "/data/input.json"]
