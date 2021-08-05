import re


class ValidationUtility(object):
    """A utility class to provide fields validation logic."""

    @staticmethod
    def validateWebsite(value):
        regex = re.compile(
            r"^((?:http|ftp)s?://)?"  # http:// or https:// or ftp:// or ftps://, optional
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        print(re.match(regex, value))
        return bool(re.match(regex, value))
