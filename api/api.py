import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def start():
    return('ok')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT'))
