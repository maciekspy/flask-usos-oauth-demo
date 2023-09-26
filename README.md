# Flask + USOS PW OAuth 1.0 Demo
Simple flask app demo for authenticating with Warsaw University of Technology USOS API,
but it also should work with other USOS instances after changing URLs to the proper one.

### How to run
- Create Python virtual environment:\
`python -m venv venv`
- Activate virtual environment:\
`source venv/bin/activate` or `venv\Scripts\activate`
- Install all the dependencies:\
`pip install -r requirements.txt`
- Copy `.env.template` file to `.env` and setup all variables.\
  To get the USOS PW API key, go to https://apps.usos.pw.edu.pl/developers/ and fill out the form.
- Start the application:\
`flask run`
- Open http://localhost:5000 in your browser and try to log in using your USOS credentials!\
  The first time, you will be redirected to the USOS system to log in and grant the app access to your data.
  If you agree, the app will create a new user, save your basic data into DB and log you into the app.

### Accessing USOS user data
Currently, the application is asking for granting permissions to two additional scopes: email and studies,
but it can be easily changed in the code. Default one gives you only access to the user ID, first name and last name.\
More about USOS API scopes: https://apps.usos.pw.edu.pl/developers/api/authorization/#scopes \
Then, more user data can be obtained using a user access token and requesting in from, e.g. [services/users/user module](https://usosapps.uw.edu.pl/developers/api/services/users/#user).
See `request_user_data` function in `app.py` for example.

### References
- https://usosapps.uw.edu.pl/developers/api/authorization/
- https://www.usos.edu.pl/sites/default/files/en-eunis-2012-vilareal.pdf
- https://apps.usos.pw.edu.pl/apps/
- https://docs.authlib.org/
- https://flask.palletsprojects.com/en/2.3.x/
