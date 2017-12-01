FROM python:3.6.3

RUN pip install wget  # Lighter weight than the binary

# This gives us a layer with most dependencies cached.
RUN python -m wget https://raw.githubusercontent.com/mccalluc/heatmap-scatter-dash/master/context/requirements.txt
RUN pip install -r requirements.txt

# Now only the dependencies which have changed need to be downloaded.
COPY . .
RUN pip install -r requirements.txt

VOLUME data

CMD ["python", "app/app_runner.py", "--demo", "3,100,10", "--port", "80", "--debug"]
# TODO: Read the input data instead of running demo
