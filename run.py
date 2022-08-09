from scanaudit import create_app
import logging, logging.handlers


logging.basicConfig(format='%(asctime)s %(message)s',filename='error.log',level=logging.WARN)


app = create_app()

if __name__ == '__main__':
    app.run(port=3002, debug=True)