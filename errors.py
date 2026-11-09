
class BumleBusinessError(Exception):
    """Basisklasse for alle forventede fejl i programmet."""


class LogFileError(BumleBusinessError):
    """Fejl ved indlæsning af logfilen (manglende fil, tom fil, rettigheder)."""


class ParseError(BumleBusinessError):
    """Fejl ved parsning af en loglinje, der ikke kan tolkes."""


class DataError(BumleBusinessError):
    """Fejl ved ugyldige eller manglende data i en record."""
