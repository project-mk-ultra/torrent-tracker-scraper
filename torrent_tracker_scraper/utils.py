class Utils:
    @staticmethod
    def is_40_char_long(s):
        """
        Checks if the infohash is 20 bytes long, confirming its truly of SHA-1 nature
        :param s:
        :return: True if infohash is valid, False otherwise
        """
        if len(s) == 40:
            return True
        return False
