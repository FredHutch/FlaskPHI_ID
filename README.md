# HDC Flask DeID
A Flask-based webservice for identification of PHI in clinical narratives

##Installation Requirements
You will need a Git Auth Token ( https://github.com/settings/tokens )stored in an environmental variable called 'HDCGITAUTHTOKEN'




## test strings

> curl -i -H "Content-Type: application/json" -X POST -d "{"""extract_text""":"""Mr. Edward Jones is a 75 yo Seattle native - follow up from visit on October 5th"""}" http://localhost:5000/medlp/annotate/phi

> curl -i -H "Content-Type: application/json" -X POST -d "{"""extract_text""":"""Mr. Edward Jones is a 75 yo Seattle native  - follow up from visit on October 5th"""}" http://localhost:5000/preprocess/
