# Flask PHI ID
A Flask-based webservice for identification of PHI in clinical narratives

##Installation Requirements
You will need a Git Auth Token ( https://github.com/settings/tokens )stored in an environmental variable called 'HDCGITAUTHTOKEN'


## General Installation
venv venv
source venv/bin/activate.sh
python setup.py install
python flaskphiid/run.py -e 0.0.0.0 -p 5000 #run flask app at endpoint 0.0.0.0 on port 5000

## test strings

> curl -i -H "Content-Type: application/json" -X POST -d "{"""extract_text""":"""Mr. Edward Jones is a 75 yo Seattle native - follow up from visit on October 5th"""}" http://localhost:5000/compmed/phi

> curl -i -H "Content-Type: application/json" -X POST -d "{"""extract_text""":"""Mr. Edward Jones is a 75 yo Seattle native  - follow up from visit on October 5th"""}" http://localhost:5000/hutchner/
