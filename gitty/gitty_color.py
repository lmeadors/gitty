import inspect


class Color:

    # define the colors dictionary, but leave it empty for now...
    colors = {}

    @staticmethod
    def enable_color():
        Color.colors = {
            'black': '\u001b[30m',
            'black_lt': '\u001b[30;1m',
            'red': '\u001b[31m',
            'red_lt': '\u001b[31;1m',
            'green': '\u001b[32m',
            'green_lt': '\u001b[32;1m',
            'yellow': '\u001b[33m',
            'yellow_lt': '\u001b[33;1m',
            'blue': '\u001b[34m',
            'blue_lt': '\u001b[34;1m',
            'magenta': '\u001b[35m',
            'magenta_lt': '\u001b[35;1m',
            'cyan': '\u001b[36m',
            'cyan_lt': '\u001b[36;1m',
            'white': '\u001b[37m',
            'white_lt': '\u001b[37;1m',
            'reset': '\u001b[0m',
        }

    @staticmethod
    def disable_color():
        Color.colors = {}

    @staticmethod
    def color(text, some_color):
        return '{}{}{}'.format(Color.colors.get(some_color, ''), text, Color.colors.get('reset', ''))

    @staticmethod
    def reset(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def white(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def white_lt(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def black(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def black_lt(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def red(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def red_lt(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def green(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def green_lt(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def yellow(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def yellow_lt(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def magenta(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def magenta_lt(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def blue(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def blue_lt(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def cyan(text):
        return Color.color(text, inspect.stack()[0][3])

    @staticmethod
    def cyan_lt(text):
        return Color.color(text, inspect.stack()[0][3])


Color.enable_color()
