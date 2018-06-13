# util.py
import string


class Utils:
    @staticmethod
    def is_hex(s):
        hex_digits = set(string.hexdigits)
        # if s is long, then it is faster to check against a set
        return all(c in hex_digits for c in s)

    @staticmethod
    def is_40_char_long(s):
        if len(s) == 40:
            return True
        else:
            return False