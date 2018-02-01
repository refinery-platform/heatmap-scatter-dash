FROM python:3.6.3

RUN pip install wget  # Lighter weight than the binary

RUN pip install pipenv

# This gives us a layer with most dependencies cached.
# TODO: install from pipenv
RUN python -m wget https://raw.githubusercontent.com/mccalluc/heatmap-scatter-dash/v0.0.12/context/requirements.txtpip install pipenv
RUN pip install -r requirements.txt

# Now only the dependencies which have changed need to be downloaded.
COPY . .
RUN pip install -r requirements.txt

VOLUME data

CMD ["python", "app_runner_refinery.py", "--input", "/data/input.json"]
