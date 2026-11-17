
# Alle fejl som programmet selv regner med at kunne ramme, samles under
# BumleBusinessError. main.py fanger den og printer en kort fejlbesked i
# stedet for et traceback. Undtagelserne nedenfor gør det muligt at se,
# hvilken del af programmet der gik galt.


class BumleBusinessError(Exception):
    """Basisklasse for alle forventede fejl i programmet."""


# Logfilen kunne ikke læses (findes ikke, er tom, eller mangler rettigheder)
class LogFileError(BumleBusinessError):
    """Fejl ved indlæsning af logfilen (manglende fil, tom fil, rettigheder)."""


# En loglinje kunne ikke tolkes som et LogRecord
class ParseError(BumleBusinessError):
    """Fejl ved parsning af en loglinje, der ikke kan tolkes."""


# Et LogRecord indeholder ugyldige eller manglende data
class DataError(BumleBusinessError):
    """Fejl ved ugyldige eller manglende data i en record."""
