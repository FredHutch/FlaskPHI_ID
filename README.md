# HDC Flask DeID
A Flask-based webservice for PHI de-identification

##Installation Requirements
You will need a Git Auth Token ( https://github.com/settings/tokens )stored in an environmental variable called 'HDCGITAUTHTOKEN'




## test strings

> curl -i -H "Content-Type: application/json" -X POST -d "{"""extract_text""":"""cerealx 84 mg daily"""}" http://localhost:5000/medlp/annotate/phi

> curl -i -H "Content-Type: application/json" -X POST -d "{"""extract_text""":"""cerealx 84 mg daily"""}" http://localhost:5000/preprocess/