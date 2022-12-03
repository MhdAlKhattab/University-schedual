from datetime import time
from Constant import Constant

# Stores data about professor
class Professor:
    # Initializes professor data
    def __init__(self, id, name, availableTime, isProf):
        self.Id = id
        self.Name = name
        self.isProf = isProf
        self.availableTime = availableTime
        self.CourseClasses = []

        for _, value in self.availableTime.items():
            if len(value) == 0:
                continue
            for i in range(len(value)):
                try:
                    Constant.TEMP_LIST_HOURS.index(value[i])
                except:
                    t = time.fromisoformat(value[i])
                    h, m = (0, -30) if t.minute == 30 else (1, 30)
                    x = 1 if i != 0 else 0
                    value[i] = time(t.hour - h + x, t.minute + m).strftime("%H:%M")
        

    """
        availableTime is dictionary
        ex :
        {
            'day' : [starttime : string , endtime: string]   OR   [] : (always),
            ...
        }
    """

    def inAvailable(self, day, startTime, endTime):
        try:
            if len(self.availableTime[day]) == 0:
                return True

            timePro1 = self.availableTime[day][0]
            timePro2 = self.availableTime[day][1]

            if startTime >= timePro1 and endTime <= timePro2:
                return True
            return False
        except:
            return False

    
    # Bind professor to course
    def addCourseClass(self, courseClass):
        self.CourseClasses.append(courseClass)

    # Compares ID's of two objects which represent professors
    def __eq__(self, rhs):
        return self.Id == rhs.Id
