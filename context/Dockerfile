FROM python:3.6.3

COPY . .

# TODO: Wget an unversioned copy, install from it, and then get the right version.
# The idea is that version bumps on one dependency shouldn't bust cache for everything.
RUN pip install -r requirements.txt

VOLUME data

CMD ["python", "app/app_runner.py"]
