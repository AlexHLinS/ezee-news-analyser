import logging
import sys

logging.addLevelName(logging.DEBUG, "\033[1;34m{}\033[1;0m".format(logging.getLevelName(logging.DEBUG)))
logging.addLevelName(logging.INFO, "\033[1;32m{}\033[1;0m".format(logging.getLevelName(logging.INFO)))
logging.addLevelName(logging.WARNING, "\033[1;33m{}\033[1;0m".format(logging.getLevelName(logging.WARNING)))
logging.addLevelName(logging.ERROR, "\033[1;31m{}\033[1;0m".format(logging.getLevelName(logging.ERROR)))
logging.addLevelName(logging.CRITICAL, "\033[1;41m{}\033[1;0m".format(logging.getLevelName(logging.CRITICAL)))


class CustomLoggerAdapter(logging.LoggerAdapter):
    """
    Адаптер для для ведения логов
    """

    def __init__(self, logger, extra=None):
        """
        Переопределяет метод __init__ объекта logging.LoggerAdapter

        Параметры:
            extra (dict): Постоянная часть сообщения при вызове logger.info, logger.error итд
            logger (dict): Логгер, на основе которого будет создаваться адаптер
        """
        if extra is None:
            extra = {}

        super(CustomLoggerAdapter, self).__init__(logger=logger, extra=extra)

    def process(self, msg, kwargs):
        """
        Переопределяет метод process объекта logging.LoggerAdapter

        Параметры:
            msg (str): Сообщение, которое передается при вызове logger.info, logger.error итд
            kwargs (dict): Набор параметров, которые передаются при вызове logger.info, logger.error итд

        Примечание: возвращаем пустой kwargs, т.к. при вызове _log никаких доп. аргументов не передаем
        """
        # Необходимые параметры (выводятся всегда, задаются через аргумент extra при создании экземпляра класса)

        if type(self.extra) == dict:
            base_strings = [f'"{bs}": {self.extra.get(f"{bs}")}' for bs in self.extra]
        else:
            base_strings = []

        # Дополнительные параметры (если передаются kwargs в logger.info, logger.error итд)
        additional_strings = [f'"{key}": {item}' for key, item in kwargs.items()]

        # Итоговая строка для вывода вместо %(message)s
        final_string = ', '.join([f'"message": {msg}'] + base_strings + additional_strings)

        return final_string, {}


def get_root_logger(log_format, log_level, log_path):
    logger = logging.getLogger('backend')
    formatter = logging.Formatter(log_format)
    logger.setLevel(log_level)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger