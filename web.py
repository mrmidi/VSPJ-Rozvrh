# import bottle

from bottle import route, run, template, static_file, request, response, redirect, error, abort, get, post, put, delete



@route('/')
def index():
    return template('index')

# start the server
run(host='localhost', port=8080, debug=True)
