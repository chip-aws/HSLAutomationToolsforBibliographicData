## ML tools for UNC Health Science Library


### What's included
* Unsupervised clustering
* RIS to CSV tools
* CSV to RIS tools
* Supervised clustering
* User Authentication (future)
* User Roles (future)
* User Profiles (future)
* API
* Email
* Unit Testing

##### Initialize a virtualenv
```
$ python3 -m venv venv
$ source env/bin/activate
```

##### Install the dependencies

```
$ pip install -r requirements.txt
```

##### Config Variables

```
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
DOWNLOAD_FOLDER = os.path.join(basedir, 'results')
```


##### Run Server

```
./run_flask.sh
```

Folder Structure Conventions
============================

> Folder structure options and naming conventions for our project

:point_right: Once our project is getting bigger we might want to use a better codebase structure. The structure presented below it might be a good choice:

<br />

```bash
< PROJECT ROOT >
   |
   |-- app/
   |    |
   |    | -- config.py                     # App Configuration
   |    | -- models.py                     # Database Tables 
   |    | -- forms.py                      # App Forms: login, registration
   |    | -- util.py                       # Helpers to manipulate date, files  
   |    | -- views.py                      # App Routing
   |    | -- __init__.py                   # Bundle all above sections and expose the Flask APP 
   |    |
   |    |-- static/
   |    |    |-- <css, JS, images>         # CSS files, Javascripts files
   |    |
   |    |-- templates/
   |    |    |
   |    |    |-- includes/                 # Page chunks, components
   |    |    |    |
   |    |    |    |-- navigation.html      # Top bar
   |    |    |    |-- sidebar.html         # Left sidebar
   |    |    |    |-- scripts.html         # JS scripts common to all pages
   |    |    |    |-- footer.html          # The common footer
   |    |    |
   |    |    |-- layouts/                  # App Layouts (the master pages)
   |    |    |    |
   |    |    |    |-- base.html            # Used by common pages like index, UI
   |    |    |
   |    |    |-- accounts/                 # Auth Pages (login, register)
   |    |    |    |
   |    |    |    |-- login.html           # Use layout `base-fullscreen.html`
   |    |    |    |-- register.html        # Use layout `base-fullscreen.html`  
   |    |    |
   |    |  index.html                      # The default page
   |    |  page-404.html                   # Error 404 page (page not found)
   |    |  page-500.html                   # Error 500 page (server error)
   |    |    *.html                        # All other pages provided by the UI Kit
   |
   |-- requirements.txt                    # Application Dependencies
   |
   |-- run.py                              # Start the app in development and production
   |
   |-- ************************************************************************
```

<br />

> Relevant Files and folders

- `run.py` - is the entry point called to start the app
- `app/__init__.py` - bundle all app sections: configuration, forms, database connection
- App modules: `views` (routing), `config`, `forms`, `util`
- App static assets and template folders:
    - `static`: the place where JS,Images and CSS files are saved
    - `templates`: pages and components to be used 

<br />

> To visualize samples app that uses this structure please visit the [Sample Apps](#sample-apps) section.

<br />

<p align="right"><a href="#topics"> :point_up_2: Return to top</a></p>

<br />

