class Color:
    _black = '\u001b[30m'
    _black_lt = '\u001b[30;1m'
    _red = '\u001b[31m'
    _red_lt = '\u001b[31;1m'
    _green = '\u001b[32m'
    _green_lt = '\u001b[32;1m'
    _yellow = '\u001b[33m'
    _yellow_lt = '\u001b[33;1m'
    _blue = '\u001b[34m'
    _blue_lt = '\u001b[34;1m'
    _magenta = '\u001b[35m'
    _magenta_lt = '\u001b[35;1m'
    _cyan = '\u001b[36m'
    _cyan_lt = '\u001b[36;1m'
    _white = '\u001b[37m'
    _white_lt = '\u001b[37;1m'
    _reset = '\u001b[0m'

    @staticmethod
    def no_color():
        Color._black = ''
        Color._black_lt = ''
        Color._red = ''
        Color._red_lt = ''
        Color._green = ''
        Color._green_lt = ''
        Color._yellow = ''
        Color._yellow_lt = ''
        Color._blue = ''
        Color._blue_lt = ''
        Color._magenta = ''
        Color._magenta_lt = ''
        Color._cyan = ''
        Color._cyan_lt = ''
        Color._white = ''
        Color._white_lt = ''
        Color._reset = ''

    @staticmethod
    def white_lt(text):
        return '{}{}{}'.format(Color._white_lt, text, Color._reset)

    @staticmethod
    def red(text):
        return '{}{}{}'.format(Color._red, text, Color._reset)

    @staticmethod
    def red_lt(text):
        return '{}{}{}'.format(Color._red_lt, text, Color._reset)

    @staticmethod
    def green(text):
        return '{}{}{}'.format(Color._green, text, Color._reset)

    @staticmethod
    def yellow(text):
        return '{}{}{}'.format(Color._yellow, text, Color._reset)

    @staticmethod
    def blue(text):
        return '{}{}{}'.format(Color._blue, text, Color._reset)

    @staticmethod
    def blue_lt(text):
        return '{}{}{}'.format(Color._blue_lt, text, Color._reset)