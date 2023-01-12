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
   |    |-- main/
   |    |    |-- __init__.py               # Bundle all above sections and expose the Flask APP 
   |    |    |-- errors.py                 #     
   |    |    |-- forms.py                  # App Forms: login, registration
   |    |    |-- views.py                  # App Routing
   |    |   
   |    |-- static/
   |    |    |-- <css, JS, images>         # CSS files, Javascripts files
   |    |    |-- favicon.ico               # project icon
   |    |
   |    |-- templates/
   |    |    |
   |    |    |--index.html                      # The default page
   |    |    |--page-403.html                   # Error 403 page (refuses to authorize it)  
   |    |    |--page-404.html                   # Error 404 page (page not found)
   |    |    |--page-500.html                   # Error 500 page (server error)
   |    |    |--stopwords.txt                   # stopwords collection
   |    |    |--*.html                          # All other pages provided by the UI Kit
   |    |   
   |    |-- __init__.py                    # Bundle all above sections and expose the Flask APP
   |    |-- ml.py                          # machine learning core algorithm file, including k-mean, NMF, asemble algo...
   |    |-- ris.py                         # ris -> CSV and CSV -> ris algorithm
   |    |-- email.py                       # email config file
   |    |-- models.py                      # converting a post to a JSON serializable dictionary
   |    |   
   |-- migrations/                         # contains the database migration scripts  
   |    |   
   |-- requirements/  
   |    |-- docker.txt                     # Docker Env Dependencies, under Python 3.8 version
   |    |-- requirements.txt               # Server Application Dependencies(Not Docker Env)
   |    |   
   |-- results/                            # Application running results files for download link, like csv and ris files
   |-- tests/                              # Unit tests are written in a tests package, for further improvement, don't use it currently
   |-- uploads/                            # save all uploaded pre-analysing files, like csv, ris...
   |
   |-- Dockerfile.txt                      # Docker can build images automatically by reading the instructions from a Dockerfile
   |-- flask.py                            # defines the Flask application instance, tasks that help manage the application
   |-- run_flask.sh                        # Docker Container startup script
   |
   |-- ************************************************************************   
  
```

<br />

> Relevant Files and folders

- `run_flask.sh` - is the entry point called to start the app
- `app/__init__.py` - bundle all app sections: configuration, forms, database connection
- App modules: `views` (routing), `config`, `forms`, `util`
- App static assets and template folders:
    - `static`: the place where JS,Images and CSS files are saved
    - `templates`: pages and components to be used 

<br />



<br />

