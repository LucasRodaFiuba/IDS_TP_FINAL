from flask import Flask
#agregar importaciones para los blueprints u otras cosas importantes

app =Flask(__name__)

#agregar blueprints
#...

if __name__ == '__main__':
    app.run(debug=True, port=5000)