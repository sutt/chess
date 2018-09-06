import os
import flask

from flask import Flask
from flask import send_file
from flask import render_template
app = Flask(__name__)

from lib_stockfish import Stockfish

print os.name
print 'path:'
print os.getcwd()   #Why is this the same as where subprocess.Popen is happening?

B_HTML = True

#TODO - use python relative path for determining these?
STOCKFISH_PATH = "../Stockfish/bin/stockfish" #When calling from chess/stockfish/api/
# STOCKFISH_PATH = "../../stockfish/Stockfish/src/stockfish"  #When calling from chess/basic_engine/src/

interface = Stockfish(path = STOCKFISH_PATH)


@app.route('/')
def hello_flask():
    return 'Hello, Flask! <br> New Line?'

@app.route('/check_server_params/')
def check_server_params():
    ret = os.name
    ret += '|'
    ret += os.getcwd()
    return ret

@app.route('/check_server_is_up/')
def check_server_is_up():
    return 'ok'


@app.route('/new_game/')
def new_game():
    interface.__start_new_game()

@app.route('/get_position/')
def get_position(b_html = B_HTML):
    list_txt = interface.get_position()
    plain_txt = '\n'.join(list_txt)
    if b_html:
        html_txt = "<pre>"
        html_txt += plain_txt.replace("\n","<br>")
        html_txt += "</pre>"
        return html_txt
    return plain_txt

@app.route('/get_position_ascii/')
def get_position_ascii():
    return get_position(b_html=False)

@app.route('/set_position/<moves>')
def set_position(moves):
    list_moves = moves.split('-')   
    print list_moves
    interface.set_position(list_moves)
    return 'position set.'

@app.route('/best_move/<params>')
def get_best_move(params):
    best_move = interface.get_best_move()
    return best_move

# if __name__ == "__main__":
#     app.run()
# export FLASK_APP=flask-server.py
# flask run [--host=0.0.0.0 (this enables outside access)]