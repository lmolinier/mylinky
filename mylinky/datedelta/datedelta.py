import datetime


class datedelta:
    __slots__ = '_months', '_timedelta'

    def __new__(cls, months=0, days=0, seconds=0, microseconds=0,
                milliseconds=0, minutes=0, hours=0, weeks=0, years=0):

        self = object.__new__(cls)
        self._timedelta = datetime.timedelta(days, seconds, microseconds, milliseconds, minutes, hours, weeks)
        if not isinstance(months, int):
            raise TypeError('months must be an integer')
        self._months = months + 12 * years
        return self

    @classmethod
    def from_timedelta(cls, td):
        return datedelta(0, 0, td.days, td.seconds, td.microseconds)

    def __repr__(self):
        args = []
        if self._months:
            args.append("months=%d" % self._months)
        if self._days:
            args.append("days=%d" % self._timedelta.days)
        if self._seconds:
            args.append("seconds=%d" % self._timedelta.seconds)
        if self._microseconds:
            args.append("microseconds=%d" % self._timedelta.microseconds)
        if not args:
            args.append('0')
        return "%s.%s(%s)" % (self.__class__.__module__,
                              self.__class__.__qualname__,
                              ', '.join(args))

    def __str__(self):
        mm, ss = divmod(self._timedelta.seconds, 60)
        hh, mm = divmod(mm, 60)
        s = "%d:%02d:%02d" % (hh, mm, ss)

        def plural(n):
            return n, abs(n) != 1 and "s" or ""

        if self._timedelta.days:
            s = ("%d day%s, " % plural(self._timedelta.days)) + s
        if self._months:
            s = ("%d month%s, " % plural(self._months)) + s
        if self._timedelta.microseconds:
            s = s + ".%06d" % self._timedelta.microseconds
        return s

    # Read-only field accessors
    @property
    def months(self):
        """months"""
        return self._months

    def __add__(self, other):
        if isinstance(other, datetime.timedelta):
            other = datedelta.from_timedelta(other)
        if isinstance(other, datedelta):
            # for CPython compatibility, we cannot use
            # our __class__ here, but need a real timedelta
            return datedelta(self._months + other._months,
                             self._days + other._days,
                             self._seconds + other._seconds,
                             self._microseconds + other._microseconds)
        if isinstance(other, datetime.datetime):
            other += self._timedelta
            if self._months > 0:
                year = self._months//12 + other.year
                if self._months%12 + other.month > 12:
                    year += 1 
                    month = self._months%12 - (12-other.month)
                else:
                    month = self._months%12 + other.month
                return other.replace(year=year, month=month)
            elif self._months < 0:
                year = other.year - abs(self._months)//12
                if other.month - abs(self._months)%12 < 1:
                    year -= 1 
                    month = 12 - (abs(self._months)%12 - other.month)
                else:
                    month = other.month - abs(self._months)%12
                return other.replace(year=year, month=month)
            return other
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other):
        return -self + other

    def __rsub__(self, other):
        if isinstance(other, datetime.datetime):
            return -self + other
        return NotImplemented

    def __neg__(self):
        n = datedelta(months=-self._months)
        n._timedelta = -self._timedelta
        return n

    def __pos__(self):
        return self

    def __abs__(self):
        if self._months < 0 and self._timedelta<0:
            return -self
        else:
            return self

    def __mul__(self, other):
        if isinstance(other, int):
            return datedelta(self._months * other,
                             self._timedelta.days * other,
                             self._timedelta.seconds * other,
                             self._timedelta.microseconds * other)
        return NotImplemented

    __rmul__ = __mul__