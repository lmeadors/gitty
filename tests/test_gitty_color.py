from unittest import TestCase

from gitty import Color


class TestColor(TestCase):
    def test_color_methods(self):
        reset = Color.colors['reset']

        for color in Color.colors:
            self.assertEqual('{}test{}'.format(Color.colors[color], reset), getattr(Color, color)('test'))

    def test_disable_colors(self):
        Color.disable_color()
        self.assertEqual('test', Color.red_lt('test'))
