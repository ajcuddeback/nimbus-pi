import logging

class Logger:
    _instance = None

    def __new__(cls, location, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._init_logger(location)
        return cls._instance

    def _init_logger(self, location):
        self.location = location

        self.log = logging.getLogger(self.location)
        self.log.setLevel(logging.INFO)

        if not self.log.handlers:
            console_handler = logging.StreamHandler()
            file_handler = logging.FileHandler('main.log')

            formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', 
                                          datefmt='%m/%d/%Y %I:%M:%S %p')

            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            file_handler.setLevel(logging.ERROR)
            file_handler.setFormatter(formatter)

            self.log.addHandler(file_handler)
            self.log.addHandler(console_handler)


