class Constant:
    DAYS_NUM = 0
    WEAK_DAYS = ()
    DAY_HOURS = 0
    FIRST_HOUR = 0
    TEMP_LIST_HOURS = ()  # every hours hh:mm from start to end hour
    # for help to know index period depend on prof time
    YEAR_NUM = 0
    SPECIALIZATIONs = ()
    SPECIALIZATION_NUM = 0
    SECTION_NUM = {}

    @staticmethod
    def init(dictConfig):
        from datetime import time

        for key in dictConfig:
            if key == "weakDays":
                Constant.WEAK_DAYS = tuple(dictConfig[key])
                Constant.DAYS_NUM = len(Constant.WEAK_DAYS)
            elif key == "dayHours":
                Constant.DAY_HOURS = dictConfig[key]
            elif key == "startHour":
                Constant.FIRST_HOUR = dictConfig[key]
            elif key == "yearNum":
                Constant.YEAR_NUM = dictConfig[key]
            elif key == "specializations":
                Constant.SPECIALIZATIONS = tuple(dictConfig[key])
                Constant.SPECIALIZATION_NUM = len(dictConfig[key])
            elif key == "sectoinNum":
                Constant.SECTION_NUM = dictConfig[key]

        Constant.TEMP_LIST_HOURS, Constant.PERIODS = Constant.generateHOURS_Periods()

    @staticmethod
    def generateHOURS_Periods():
        from datetime import time

        t = time.fromisoformat(Constant.FIRST_HOUR)
        temp = []
        for i in range(Constant.DAY_HOURS + 1):
            temp.append(str(time(t.hour + i, t.minute))[:5])

        PERIODS = [""]
        for i in range(Constant.DAY_HOURS):
            PERIODS.append(temp[i] + " - " + temp[i + 1])

        return tuple(temp), tuple(PERIODS)

    @staticmethod
    def indexDay(day):
        return Constant.WEAK_DAYS.index(day)
