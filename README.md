Necassary Dependencies:<br>
```
from flask import Flask, render_template, request, redirect, url_for
import util
import os
import glob
from os.path import join, dirname, realpath
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table,Column,Integer,String
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper
```
```
The database will be created when you run the below commands
```

To start website locally:

1. Clone repo/pull changes down

2. Start python virtual environment (or create one):

```
sudo apt-get install python3-venv
```

```
python3 -m venv virtual
```

```
source virtual/bin/activate
```

3. Install Flask in virtual environment

```
pip3 install flask
```

4. Run command:
```
python3 main.py
```

5. Go to link shown in terminal (127.0.0.1:5000)

Team Member Names/Emails:
1. Storm Davis 
2. Avery Cripe
3. Maryam Navaei
