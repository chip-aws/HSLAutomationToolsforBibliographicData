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
