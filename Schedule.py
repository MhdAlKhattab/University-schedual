from math import fabs
from Constant import Constant
from Reservation import Reservation
from collections import defaultdict, deque
from random import randrange


# Schedule chromosome
class Schedule:
    # Initializes chromosomes with configuration block (setup of chromosome)
    def __init__(self, configuration):
        self._configuration = configuration
        # Fitness value of chromosome
        self._fitness = 0

        # Time-space slots, one entry represent one hour in one classroom
        slots_length = (
            Constant.DAYS_NUM * Constant.DAY_HOURS * self._configuration.numberOfRooms
        )
        self._slots = [[] for _ in range(slots_length)]

        # Class table for chromosome
        # Used to determine first time-space slot used by class
        self._classes = defaultdict(Reservation)

        # Flags of class requirements satisfaction
        self._criteria = (self._configuration.numberOfCourseClasses * 6) * [False]

        self._diversity = 0.0
        self._rank = 0

    def copy(self, c, setup_only):
        if not setup_only:
            self._configuration = c.configuration
            # copy code
            self._slots, self._classes = c.slots, c.classes

            # copy flags of class requirements
            self._criteria = c.criteria

            # copy fitness
            self._fitness = c.fitness
            return self

        return Schedule(c.configuration)

    # Makes new chromosome with same setup but with randomly chosen code
    def makeNewFromPrototype(self):
        # make new chromosome, copy chromosome setup
        new_chromosome = self.copy(self, True)
        new_chromosome_slots, new_chromosome_classes = (
            new_chromosome._slots,
            new_chromosome._classes,
        )

        # place classes at random position
        classes = self._configuration.courseClasses
        nr = self._configuration.numberOfRooms
        DAYS_NUM, DAY_HOURS = Constant.DAYS_NUM, Constant.DAY_HOURS
        for c in classes:
            # determine random position of class
            dur = c.Duration
            day, time = c.randDayTime()

            room = randrange(32768) % nr
            reservation = Reservation(nr, day, time, room)
            reservation_index = hash(reservation)

            # fill time-space slots, for each hour of class
            for i in range(reservation_index, reservation_index + dur):
                new_chromosome_slots[i].append(c)

            # insert in class table of chromosome
            new_chromosome_classes[c] = reservation
        new_chromosome.calculateFitness("makeNewFromPrototype")
        return new_chromosome

    # Performs crossover operation using to chromosomes and returns pointer to offspring
    def crossover(self, parent, numberOfCrossoverPoints, crossoverProbability):
        # check probability of crossover operation
        if randrange(32768) % 100 > crossoverProbability:
            # no crossover, just copy first parent
            return self.copy(self, False)

        # new chromosome object, copy chromosome setup
        n = self.copy(self, True)
        n_classes, n_slots = n._classes, n._slots

        classes = self._classes
        # number of classes
        size = len(classes)

        cp = size * [False]

        # determine crossover point (randomly)
        for i in range(numberOfCrossoverPoints, 0, -1):
            check_point = False
            while not check_point:
                p = randrange(32768) % size
                if not cp[p]:
                    cp[p] = check_point = True

        # make new code by combining parent codes
        first = randrange(2) == 0

        for i in range(size):
            if first:
                course_class = self._configuration.courseClasses[i]
                dur = course_class.Duration
                reservation = classes[course_class]
                reservation_index = hash(reservation)
                # insert class from first parent into new chromosome's class table
                n_classes[course_class] = reservation
                # all time-space slots of class are copied

                try:
                    for j in range(reservation_index, reservation_index + dur):
                        n_slots[j].append(course_class)
                except:
                    print("length slot = ", len(n_slots))
                    print(
                        "reservation_index, reservation_index + dur ",
                        reservation_index,
                        reservation_index + dur,
                    )
                    exit()
            else:
                course_class = self._configuration.courseClasses[i]
                dur = course_class.Duration
                reservation = parent._classes[course_class]
                reservation_index = hash(reservation)
                # insert class from second parent into new chromosome's class table
                n_classes[course_class] = reservation

                # all time-space slots of class are copied
                try:
                    for j in range(reservation_index, reservation_index + dur):
                        n_slots[j].append(course_class)
                except:
                    print("length slot = ", len(n_slots))
                    print(
                        "reservation_index, reservation_index + dur ",
                        reservation_index,
                        reservation_index + dur,
                    )
                    exit()
            # crossover point
            if cp[i]:
                # change source chromosome
                first = not first

        n.calculateFitness("crossover")

        # return smart pointer to offspring
        return n

    # Performs mutation on chromosome
    def mutation(self, mutationSize, mutationProbability):
        # check probability of mutation operation
        if randrange(32768) % 100 > mutationProbability:
            return

        classes = self._classes
        # number of classes
        numberOfClasses = len(classes)
        course_classes = tuple(classes.keys())
        configuration = self._configuration
        slots = self._slots
        nr = configuration.numberOfRooms

        DAY_HOURS = Constant.DAY_HOURS
        DAYS_NUM = Constant.DAYS_NUM
        # move selected number of classes at random position
        for i in range(mutationSize, 0, -1):
            # select ranom chromosome for movement
            mpos = randrange(32768) % numberOfClasses

            # current time-space slot used by class
            cc1 = course_classes[mpos]
            reservation1 = classes[cc1]
            reservation1_index = hash(reservation1)

            # determine position of class randomly
            dur = cc1.Duration
            day, time = cc1.randDayTime()

            room = randrange(32768) % nr
            reservation2 = Reservation(nr, day, time, room)
            reservation2_index = hash(reservation2)

            # move all time-space slots
            for j in range(dur):
                # remove class hour from current time-space slot
                cl = slots[reservation1_index + j]
                clTuple = tuple(cl)
                for cc in clTuple:
                    cl.remove(cc)

                # move class hour to new time-space slot
                slots[reservation2_index + j].append(cc1)

            # change entry of class table to point to new time-space slots
            classes[cc1] = reservation2
        self.calculateFitness("mutation")

    # Calculates fitness value of chromosome
    def calculateFitness(self, Form):
        # chromosome's score
        sumScore = 0
        score = 0
        softScore = 0

        criteria, configuration = self._criteria, self._configuration
        items, slots = self._classes.items(), self._slots
        numberOfRooms = configuration.numberOfRooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_HOURS, Constant.DAYS_NUM
        daySize = DAY_HOURS * numberOfRooms

        ci = 0
        getRoomById = configuration.getRoomById

        # check criteria and calculate scores for each class in schedule
        for cc, reservation in items:
            score = 0
            softScore = 0
            # coordinate of time-space slot
            day, time, room = reservation.Day, reservation.Time, reservation.Room
            dur = cc.Duration

            # check for room overlapping of classes
            reservation_index = hash(reservation)
            cls = slots[reservation_index : reservation_index + dur]
            ro = any(True for slot in cls if len(slot) > 1)

            # on room overlapping
            score = score if ro else score + 1

            criteria[ci + 0] = not ro

            r = getRoomById(room)
            # does current room have enough seats
            criteria[ci + 1] = r.NumberOfSeats >= cc.NumberOfSeats
            score = score + 1 if criteria[ci + 1] else score

            # does current room have computers if they are required
            criteria[ci + 2] = ((not cc.LabRequired) or r.Lab) and (
                cc.LabRequired or not (r.Lab)
            )
            score = score + 1 if criteria[ci + 2] else score
            po = go = False

            # check overlapping of classes for professors and student groups
            t = day * daySize + time
            professorOverlaps, groupsOverlap = cc.professorOverlaps, cc.groupsOverlap
            try:
                for k in range(numberOfRooms, 0, -1):
                    # for each hour of class
                    for i in range(t, t + dur):
                        cl = slots[i]
                        for cc1 in cl:
                            if cc != cc1:
                                # professor overlaps?
                                if not po and professorOverlaps(cc1):
                                    po = True
                                # student group overlaps?
                                if not go and groupsOverlap(cc1):
                                    go = True
                                # both type of overlapping? no need to check more
                                if po and go:
                                    raise Exception("no need to check more")

                    t += DAY_HOURS
            except Exception:
                pass

            # professors have no overlapping classes?
            score = score if po else score + 1

            criteria[ci + 3] = not po

            # student groups has no overlapping classes?
            score = score if go else score + 1

            criteria[ci + 4] = not go

            # Time Professor Is Available ?

            # alpha for soft rule
            alpha = [
                1.0,  # alpha for make course in time of prof
                0.5,  # alpha for cancle spacing between courses
                0.8,  # alpha for make cousre earlier
                1.7,  # alpha for make prof's course in fewer day
            ]

            profScore = 0
            to = False
            lenProfTheoretical = 0
            for prof in cc.Professors:
                if prof.isProf:
                    lenProfTheoretical += 1
                    if prof.inAvailable(
                        Constant.WEAK_DAYS[day],
                        Constant.TEMP_LIST_HOURS[time],
                        Constant.TEMP_LIST_HOURS[time + dur],
                    ):
                        profScore += 1
                    else:
                        to = True
                else:
                    try:
                        if prof.inAvailable(
                            Constant.WEAK_DAYS[day],
                            Constant.TEMP_LIST_HOURS[time],
                            Constant.TEMP_LIST_HOURS[time + dur],
                        ):
                            softScore += alpha[0]
                    except:
                        from time import sleep

                        sleep(1)
                        print(
                            "second id course = ",
                            cc.Id,
                            "day = ",
                            day,
                            "time of course = ",
                            time,
                            ", duration = ",
                            cc.Duration,
                            " ,length of PERIODS = ",
                            len(Constant.PERIODS),
                        )
                        for index, period in enumerate(Constant.TEMP_LIST_HOURS):
                            print(f"TEMP_LIST_HOURS {period} its index {index}")
                        print("available time for cours class is ", cc.availableTime)
                        print("available time for prof is ", prof.availableTime)
                        exit()

            if cc.LabRequired:
                score += 1
            else:
                profScore /= lenProfTheoretical
                score += profScore

            criteria[ci + 5] = not to

            # second soft rule
            try:
                if reservation_index % DAY_HOURS == 0:
                    softScore += alpha[1]
                else:
                    if len(slots[reservation_index - 1]) != 0:
                        softScore += alpha[1]
            except:
                pass

            # third soft rule
            try:
                if reservation_index % DAY_HOURS == 0:
                    softScore += alpha[2]
                    raise

                totalSlot = 0  # num of total slots from begin of day to time of course
                nonEmptySLot = (
                    0  # num of non empty slots from begin of day to time of course
                )

                for index in range(
                    day * numberOfRooms * DAY_HOURS + room * DAY_HOURS,
                    reservation_index,
                ):
                    totalSlot += 1
                    if len(slots[index]) != 0:
                        nonEmptySLot += 1
                softScore += alpha[2] * nonEmptySLot / totalSlot
            except:
                pass

            # fourth soft rule
            minFewerDayScore = 10
            for prof in cc.Professors:
                lenProfCourse = len(prof.CourseClasses)
                sumDistance = 0
                for profCourse in prof.CourseClasses:
                    profReservation = self._classes[profCourse]
                    if cc == profCourse:
                        sumDistance += 1
                    elif day != profReservation.Day:
                        sumDistance += 0
                    else:
                        sumDistance += (
                            1 - (abs(time - profReservation.Time) - 1) / DAY_HOURS
                        )
                minFewerDayScore = min(minFewerDayScore, sumDistance / lenProfCourse)

            softScore += alpha[3] * minFewerDayScore

            softScore /= 4.1 * configuration.numberOfCourseClasses
            score += softScore

            sumScore += score
            ci += 6

        # calculate fitness value based on score
        self._fitness = sumScore / (configuration.numberOfCourseClasses * 7)

    # Calculates fitness value of chromosome
    def calculateFitness2(self, From):
        # chromosome's score
        sumScore = 0
        score = 0
        softScore = 0

        criteria, configuration = self._criteria, self._configuration
        items, slots = self._classes.items(), self._slots
        numberOfRooms = configuration.numberOfRooms
        DAY_HOURS, DAYS_NUM = Constant.DAY_HOURS, Constant.DAYS_NUM
        daySize = DAY_HOURS * numberOfRooms

        ci = 0
        getRoomById = configuration.getRoomById

        # check criteria and calculate scores for each class in schedule
        for cc, reservation in items:
            score = 0
            softScore = 0.7

            # coordinate of time-space slot
            day, time, room = reservation.Day, reservation.Time, reservation.Room
            dur = cc.Duration
            """if dur == 3 and time == 6:
                print(
                    "fittness first ",
                    "From ",
                    From,
                    "id course = ",
                    cc.Id,
                    "day = ",
                    day,
                    "time of course = ",
                    reservation.Time,
                    ", duration = ",
                    cc.Duration,
                    " ,length of PERIODS = ",
                    len(Constant.PERIODS),
                )"""
            # check for room overlapping of classes
            reservation_index = hash(reservation)
            cls = slots[reservation_index : reservation_index + dur]
            ro = any(True for slot in cls if len(slot) > 1)

            # on room overlapping
            score = score if ro else score + 1

            criteria[ci + 0] = not ro

            r = getRoomById(room)
            # does current room have enough seats
            criteria[ci + 1] = r.NumberOfSeats >= cc.NumberOfSeats
            score = score + 1 if criteria[ci + 1] else score

            # does current room have computers if they are required
            criteria[ci + 2] = (not cc.LabRequired) or (cc.LabRequired and r.Lab)
            score = score + 1 if criteria[ci + 2] else score
            po = go = False

            # check overlapping of classes for professors and student groups
            t = day * daySize + time
            professorOverlaps, groupsOverlap = cc.professorOverlaps, cc.groupsOverlap
            try:
                for k in range(numberOfRooms, 0, -1):
                    # for each hour of class
                    for i in range(t, t + dur):
                        cl = slots[i]
                        for cc1 in cl:
                            if cc != cc1:
                                # professor overlaps?
                                if not po and professorOverlaps(cc1):
                                    po = True
                                # student group overlaps?
                                if not go and groupsOverlap(cc1):
                                    go = True
                                # both type of overlapping? no need to check more
                                if po and go:
                                    raise Exception("no need to check more")

                    t += DAY_HOURS
            except Exception:
                pass

            # professors have no overlapping classes?
            score = score if po else score + 1

            criteria[ci + 3] = not po

            # student groups has no overlapping classes?
            score = score if go else score + 1

            criteria[ci + 4] = not go

            # Time Professor Is Available ?
            profScore = 0
            to = False
            lenProfTheoretical = 0
            for prof in cc.Professors:
                if prof.isProf:
                    lenProfTheoretical += 1
                    if prof.inAvailable(
                        Constant.WEAK_DAYS[day],
                        Constant.TEMP_LIST_HOURS[time],
                        Constant.TEMP_LIST_HOURS[time + dur],
                    ):
                        profScore += 1
                    else:
                        to = True
                else:
                    try:
                        if prof.inAvailable(
                            Constant.WEAK_DAYS[day],
                            Constant.TEMP_LIST_HOURS[time],
                            Constant.TEMP_LIST_HOURS[time + dur],
                        ):
                            softScore += 1.3
                    except:
                        from time import sleep

                        sleep(1)
                        print(
                            "second id course = ",
                            cc.Id,
                            "day = ",
                            day,
                            "time of course = ",
                            time,
                            ", duration = ",
                            cc.Duration,
                            " ,length of PERIODS = ",
                            len(Constant.PERIODS),
                        )
                        for index, period in enumerate(Constant.TEMP_LIST_HOURS):
                            print(f"TEMP_LIST_HOURS {period} its index {index}")
                        print("available time for cours class is ", cc.availableTime)
                        print("available time for prof is ", prof.availableTime)
                        exit()

            if cc.LabRequired:
                score += 1
            else:
                profScore /= lenProfTheoretical
                score += profScore

            criteria[ci + 5] = not to

            softScore /= 2.1 * configuration.numberOfCourseClasses
            score += softScore

            sumScore += score
            ci += 6

        # calculate fitness value based on score
        self._fitness = sumScore / (configuration.numberOfCourseClasses * 7)

    # Returns fitness value of chromosome
    @property
    def fitness(self):
        return self._fitness

    @property
    def configuration(self):
        return self._configuration

    @property
    # Returns reference to table of classes
    def classes(self):
        return self._classes

    @property
    # Returns array of flags of class requirements satisfaction
    def criteria(self):
        return self._criteria

    @property
    # Return reference to array of time-space slots
    def slots(self):
        return self._slots

    @property
    def diversity(self):
        return self._diversity

    @diversity.setter
    def diversity(self, new_diversity):
        self._diversity = new_diversity

    @property
    def rank(self):
        return self._rank

    @rank.setter
    def rank(self, new_rank):
        self._rank = new_rank

    def __hash__(self) -> int:
        prime = 31
        result = 1
        classes = self._classes
        for cc in classes.keys():
            reservation = classes[cc]
            result = prime * result + (0 if reservation is None else hash(reservation))
        return result

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        classes, otherClasses = self._classes, other.classes
        for cc in classes.keys():
            if classes[cc] != otherClasses[cc]:
                return False

    def __ne__(self, other):
        return not self.__eq__(other)
