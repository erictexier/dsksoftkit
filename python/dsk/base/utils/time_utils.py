import datetime
import time
import re
####################################
class TimeUtils(object):
    adotdigit = re.compile("\.[\d]*$")
    def __init__(self,tstamp):
        self.tstamp = tstamp

    @property
    def date(self):
        b = datetime.datetime.fromtimestamp(self.tstamp)
        return "%04d-%02d-%02d %02d:%02d:%02d" % (b.year,b.month,b.day,b.hour,b.minute,b.second)

    @property
    def day(self):
        b = datetime.datetime.fromtimestamp(self.tstamp)
        return "%04d-%02d-%02d" % (b.year,b.month,b.day)

    def add_days(self,days):
        """ days can be negative """
        oth = datetime.datetime.fromtimestamp(self.tstamp) + datetime.timedelta(days=days)
        return TimeUtils(time.mktime(oth.timetuple()))

    @property
    def time(self):
        b = datetime.datetime.fromtimestamp(self.tstamp)
        return "%02d:%02d:%02d" % (b.hour,b.minute,b.second)

    @staticmethod
    def compare(a,b):
        return cmp(a.tstamp,b.tstamp)

    @staticmethod
    def stringtodata(astr):
        try:
            date_object = datetime.datetime.strptime(astr,'%Y-%m-%d %H:%M:%S.%I%f')
            return date_object
        except:
            try:
                # try with if no dot
                m = TimeUtils.adotdigit.search(astr)
                if m:
                    astr = astr.replace(m.group(),"")
                    date_object = datetime.datetime.strptime(astr,'%Y-%m-%d %H:%M:%S')
                    return date_object
            except Exception as e:
                print((str(e)))
                pass
        return None

    @staticmethod
    def convert_date_and_time_to_float_time(adate="",atime=""):
        # adate must be a string formated as  year-mo-da as "2010-09-28"
        # atime format as "14:23:57"
        # support also the / format
        adate = adate.replace("/","-")
        if adate == "":
            sdate = list()
        else:
            sdate = adate.split("-")
        # if not specify, we fill out the blank with today's date
        if len(sdate)==0:
            now = datetime.datetime.today()
            sdate.append("%s" % now.year)
            sdate.append("%s" % now.month)
            sdate.append("%s" % now.day)

        elif len(sdate) == 1:
            now = datetime.datetime.today()
            sdate.append("%s" % now.month)
            sdate.append("%s" % now.day)

        elif len(sdate) == 2:
            now = datetime.datetime.today()
            sdate.append("%s" % now.day)

        if atime == "":
            stime = list()
        else:
            stime = atime.split(":")
        # if not specify, we fill out the blank with today's date
        if len(stime)==0:
            now = datetime.datetime.today()
            stime.append("%s" % now.hour)
            stime.append("%s" % now.minute)
            stime.append("%s" % now.second)

        elif len(stime) == 1:
            now = datetime.datetime.today()
            stime.append("%s" % now.minute)
            stime.append("%s" % now.second)

        elif len(stime) == 2:
            now = datetime.datetime.today()
            stime.append("%s" % now.second)

        assert len(sdate) == 3
        assert len(stime) == 3
        sdate = [int(x) for x in sdate]
        stime = [int(x) for x in stime]
        a = datetime.datetime(sdate[0],sdate[1],sdate[2],stime[0],stime[1],stime[2],0)
        a = time.mktime(a.timetuple())
        return a

    @staticmethod
    def prettydate(d, default="%b %d %Y %I:%M%p"):

        now = datetime.datetime.now()
        now = now.replace(tzinfo=None)
        d = d.replace(tzinfo=None)
        diff = now - d

        s = diff.seconds
        if diff.days > 2 or diff.days < 0:
            return d.strftime(default)
        elif diff.days == 1:
            return '1 day ago'
        elif diff.days > 1:
            return '%s days ago' % diff.days
        elif s <= 1:
            return 'just now'
        elif s < 60:
            return '%s sec ago' % s
        elif s < 120:
            return '1 min ago'
        elif s < 3600:
            return '%s min ago' % (s/60)
        elif s < 7200:
            return '1 hour ago'
        else:
            return '%s hours ago' % (s/3600)

class StopWatch(object):
    _start = 0.0
    _end = 0.0
    _running = False
    def start(self):
        _running = True
        self._start = time.time()
    def stop(self):
        self._end = time.time()
        _running = False
    def elapsed(self):
        return self._end - self._start

#  StopWatch test code
def main():
    myTimer = StopWatch()
    myTimer.start()
    for number in range(1,4):
        print(('doing something for...%i sec' % number))
        time.sleep(number)
    myTimer.stop()
    print(('time spent: %f seconds' % myTimer.elapsed()))


if __name__ == "__main__":
    main()
