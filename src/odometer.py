import math


def fdigit(odigit):
    """
    Convert an odometer digit [1-9A-Z] to an unsigned fixnum digit (0...34)
    :param odigit: an odometer digit, a character [1-9A-Z]
    :return: an unsigned integer in the range 0...34
    """
    return '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'.index(odigit)
    pass


def odigit(fdigit):
    """
    Convert an unsigned fixnum digit (0...34) to an odometer digit [1-9A-Z]
    :param fdigit: an unsigned integer in the range 0...34
    :return: an odometer digit, a character [1-9A-Z]
    """
    return '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[fdigit]
    pass


def odometer_count_below_length(length):
    """Count how many odometer numbers can be expressed with fewer than length digits"""
    base = 35
    power = 1
    answer = 0
    for x in xrange(length):
        power *= base
        answer += power
    return answer


# I don't understand what this is doing or why it's doing it
def odometer_as_base35(onumber):
    """Convert an odometer number into a base 35 number"""
    base = 35
    power = 1
    answer = 0
    for ndx in xrange(len(onumber)):
        answer += power * fdigit(onumber[ndx])
        power *= base
    return answer


def number_of_odometer_digits(fnumber):
    """Count how many odometer digits are needed to represent fnumber"""
    answer = 0
    while odometer_count_below_length(answer) <= fnumber:
        answer += 1
    return answer


def base35_as_odometer(base35_number, length):
    """Return a string that represents base35_number in base 35 with odometer digits"""
    base = 35
    answer = ['' for x in range(length)]
    power = base ** (length - 1)
    temp = base35_number
    for ndx in range(length):
        fdigit = math.floor(temp / power)
        answer[ndx] = odigit(fdigit)
        temp = temp - fdigit * power
        power = power / base
    return ''.join(answer)


# Odometer to Fixnum
def odometer_to_fixnum(onumber):
    count_below = odometer_count_below_length(len(onumber))
    answer = count_below + odometer_as_base35(onumber)
    return answer


# Fixnum to Odometer
def fixnum_to_odometer(fnumber):
    ndigits = number_of_odometer_digits(fnumber)
    count_below = odometer_count_below_length(ndigits)
    answer = base35_as_odometer((fnumber - count_below), ndigits)
    return answer