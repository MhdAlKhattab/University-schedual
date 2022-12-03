from Constant import Constant


class CourseClass:
    # ID counter used to assign IDs automatically
    _next_class_id = 0

    # Initializes class object
    def __init__(self, professors, course, requires_lab, duration, groups, section):
        self.Id = CourseClass._next_class_id
        CourseClass._next_class_id += 1
        # Return pointer to professors who teache
        self.Professors = professors
        # Return pointer to dict of intersection professors times
        self.availableTime = self.Intersection(professors)
        # Return pointer to course to which class belongs
        self.Course = course
        # Returns number of seats (students) required in room
        self.NumberOfSeats = 0
        # Returns section of class
        self.Section = section
        # Returns TRUE if class requires computers in room.
        self.LabRequired = requires_lab
        # Returns duration of class in hours
        self.Duration = duration
        # Returns reference to list of student groups who attend class
        self.Groups = groups

        # bind professors to class
        for professor in self.Professors:
            professor.addCourseClass(self)

        # bind student groups to class
        for grp in self.Groups:  # self.groups:
            grp.addClass(self)
            self.NumberOfSeats += grp.NumberOfStudents

    # Returns TRUE if another class has one or overlapping student groups.
    def groupsOverlap(self, c):
        return any(True for grp in self.Groups if grp in c.Groups)

    # Returns TRUE if another class has same professor.
    def professorOverlaps(self, c):
        return any(True for prof in self.Professors if prof in c.Professors)

    def Intersection(self, profs):
        intersection = {}

        if len(profs) == 1:
            return profs[0].availableTime

        for day in profs[0].availableTime:
            b = True
            times = []  # list of list of two element(starttime , endtime) or []
            for d in profs:
                if not day in d.availableTime:
                    b = False
                    break
                times.append(d.availableTime[day])
            if b:
                x = self.timeInter(times)
                if x[1] != False:
                    intersection[day] = x[0]

        return intersection

    def timeInter(self, times):  # times = [["hh:mm", "hh:mm"], [], ...]
        starttime = Constant.TEMP_LIST_HOURS[0]
        endtime = Constant.TEMP_LIST_HOURS[-1]

        for time in times:
            if len(time) == 0:
                continue
            if time[0] > starttime:
                starttime = time[0]
            if time[1] < endtime:
                if time[1] <= starttime:
                    return [], False

                endtime = time[1]

        return (
            ([starttime, endtime], True)
            if starttime != Constant.TEMP_LIST_HOURS[0]
            or endtime != Constant.TEMP_LIST_HOURS[-1]
            else ([], True)
        )

    def randDayTime(self):
        from random import choice, randrange

        dur = self.Duration
        iterat = 0
        while True:

            day, t = choice(list(self.availableTime.items()))
            # print(day, t)
            if len(t) == 0:
                x = (Constant.indexDay(day), randrange(0, Constant.DAY_HOURS - dur + 1))
                # if dur == 3 and x[1] == 6:
                #     print(
                #         f"randDay Time :\n\ttime from 0 -> {Constant.DAY_HOURS - dur + 1} time = {x[1]}"
                #     )
                #     input("press .....")
                return x
            else:  # 09:30 -> 13:00
                index_t1 = Constant.TEMP_LIST_HOURS.index(t[0])
                index_t2 = Constant.TEMP_LIST_HOURS.index(t[1])
                try:
                    x = (
                        Constant.indexDay(day),
                        randrange(index_t1, index_t2 - dur + 1),
                    )
                    # if dur == 3 and x[1] == 6:
                    #     print(
                    #         f"randDay Time :\n\ttime from {index_t1} -> {index_t2 - dur + 1} time = {x[1]}"
                    #     )
                    #     input("press .....")
                    return x
                except:
                    iterat += 1
                    if iterat == 10:
                        x = (
                            Constant.indexDay(day),
                            randrange(0, Constant.DAY_HOURS - dur + 1),
                        )
                        # if dur == 3 and x[1] == 6:
                        #     print(
                        #         f"randDay Time after while:\n\ttime from 0 -> {Constant.DAY_HOURS - dur + 1} time = {x[1]}"
                        #     )
                        #     input("press .....")
                        return x

    def __hash__(self):
        return hash(self.Id)

    def __eq__(self, other):
        return self.Id == other.Id

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    # Restarts ID assigments
    @staticmethod
    def restartIDs() -> None:
        CourseClass._next_class_id = 0
