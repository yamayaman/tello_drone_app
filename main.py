import logging
import sys

import controllers.server

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


if __name__ == '__main__':
    controllers.server.run()