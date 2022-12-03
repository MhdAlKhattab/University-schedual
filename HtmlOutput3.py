from Constant import Constant
from collections import defaultdict


class HtmlOutput:
    @staticmethod
    def init():
        HtmlOutput.ROOM_COLUMN_NUMBER = Constant.DAYS_NUM + 1
        HtmlOutput.ROOM_ROW_NUMBER = Constant.DAY_HOURS + 1
        HtmlOutput.COLOR1 = "#319378"
        HtmlOutput.COLOR2 = "#CE0000"
        HtmlOutput.CRITERIAS = ("R", "S", "L", "P", "G", "T")
        HtmlOutput.CRITERIAS_DESCR = (
            "Current room has {any}overlapping",
            "Current room has {any}enough seats",
            "Current room with {any}enough computers if they are required",
            "Professors have {any}overlapping classes",
            "Student groups has {any}overlapping classes",
            "Time Professor has {any}overlapping classes",
        )
        HtmlOutput.PERIODS = Constant.PERIODS
        HtmlOutput.WEEK_DAYS = Constant.WEAK_DAYS

    @staticmethod
    def getCourseClass(cc, RoomName, criterias, ci):
        COLOR1 = HtmlOutput.COLOR1
        COLOR2 = HtmlOutput.COLOR2
        CRITERIAS = HtmlOutput.CRITERIAS
        length_CRITERIAS = len(CRITERIAS)
        CRITERIAS_DESCR = HtmlOutput.CRITERIAS_DESCR

        sb = [
            cc.Course.Name,
            "<br />",
            "-".join(map(lambda prof: prof.Name, cc.Professors)),
            "<br />",
            RoomName,
            "<br />",

            "/".join(map(lambda grp: grp.Name, cc.Groups)),
            # "Section: " + cc.Section
            "<br />",
        ]
        if cc.LabRequired:
            sb.append("Lab<br />")

        for i in range(length_CRITERIAS):
            sb.append("<span style='color:")
            if criterias[ci + i]:
                sb.append(COLOR1)
                sb.append("' title='")
                sb.append(
                    CRITERIAS_DESCR[i].format(any="" if (i == 1 or i == 2) else "no ")
                )
            else:
                sb.append(COLOR2)
                sb.append("' title='")
                sb.append(
                    CRITERIAS_DESCR[i].format(any="not " if (i == 1 or i == 2) else "")
                )
            sb.append("'> ")
            sb.append(CRITERIAS[i])
            sb.append(" </span>")

        return sb

    @staticmethod
    def generateTimeTable(solution, slot_table):
        ci = 0

        time_table = defaultdict(list)
        items = solution.classes.items
        ROOM_COLUMN_NUMBER = HtmlOutput.ROOM_COLUMN_NUMBER
        getCourseClass = HtmlOutput.getCourseClass

        for cc, reservation in items():
            # coordinate of time-space slot
            dayId = reservation.Day + 1
            periodId = reservation.Time + 1
            roomId = reservation.Room
            dur = cc.Duration
            year = cc.Course.Year
            specialization = cc.Course.Specialization
            section = cc.Section
            sectionNum = Constant.SECTION_NUM[str(year)]
            if isinstance(sectionNum, list):
                sectionNum = 1
            
            if section == 0:
                for sec in range(1, sectionNum + 1):
                    indexId = (dayId - 1) * sectionNum + sec

                    key = (periodId, year, specialization)

                    if key in slot_table:
                        year_duration = slot_table[key]
                    else:
                        year_duration = (ROOM_COLUMN_NUMBER * sectionNum - sectionNum + 1) * [0]
                        slot_table[key] = year_duration

                    year_duration[indexId] = dur

                    for m in range(1, dur):
                        next_key = (periodId + m, year, specialization)
                        if next_key not in slot_table:
                            slot_table[next_key] = (ROOM_COLUMN_NUMBER * sectionNum - sectionNum + 1) * [0]
                        if slot_table[next_key][indexId] < 1:
                            slot_table[next_key][indexId] = -1


                    if key in time_table:
                        year_schedule = time_table[key]
                    else:
                        year_schedule = (ROOM_COLUMN_NUMBER * sectionNum - sectionNum + 1) * [None]
                        time_table[key] = year_schedule

                    year_schedule[indexId] = "".join(getCourseClass(cc, solution._configuration.getRoomById(roomId).Name, solution.criteria, ci))
                
            else:
                indexId = (dayId - 1) * sectionNum + section

                key = (periodId, year, specialization)

                if key in slot_table:
                    year_duration = slot_table[key]
                else:
                    year_duration = (ROOM_COLUMN_NUMBER * sectionNum - sectionNum + 1) * [0]
                    slot_table[key] = year_duration

                year_duration[indexId] = dur

                for m in range(1, dur):
                    next_key = (periodId + m, year, specialization)
                    if next_key not in slot_table:
                        slot_table[next_key] = (ROOM_COLUMN_NUMBER * sectionNum - sectionNum + 1) * [0]
                    if slot_table[next_key][indexId] < 1:
                        slot_table[next_key][indexId] = -1


                if key in time_table:
                    year_schedule = time_table[key]
                else:
                    year_schedule = (ROOM_COLUMN_NUMBER * sectionNum - sectionNum + 1) * [None]
                    time_table[key] = year_schedule

                year_schedule[indexId] = "".join(getCourseClass(cc, solution._configuration.getRoomById(roomId).Name, solution.criteria, ci))
            
            ci += 6

        return time_table

    @staticmethod
    def getHtmlCell(content, rowspan):
        if rowspan == 0:
            return "<td></td>"

        if content is None:
            return ""

        sb = []
        if rowspan > 1:
            sb.append("<td style='border: .1em solid black; padding: .25em' rowspan='")
            sb.append(rowspan)
            sb.append("'>")
        else:
            sb.append("<td style='border: .1em solid black; padding: .25em'>")

        sb.append(content)
        sb.append("</td>")
        return "".join(str(v) for v in sb)

    @staticmethod
    def getResult(solution):
        HtmlOutput.init()
        # configuration = solution.configuration
        # np = configuration.numberOfProfessors
        # getProfessorById = configuration.getProfessorById
        yearsNum = Constant.YEAR_NUM
        specNum = Constant.SPECIALIZATION_NUM
        sections = Constant.SECTION_NUM

        slot_table = defaultdict(list)
        time_table = HtmlOutput.generateTimeTable(
            solution, slot_table
        )  # Tuple[0] = time, Tuple[1] = year, Tuple[2] = specialization 
        if not slot_table or not time_table:
            return ""

        sb = []
        for year in range(1, yearsNum + 1):
            sectionNum = Constant.SECTION_NUM[str(year)]
            if isinstance(sectionNum, list):
                sectionNum = 1
                for spec in Constant.SPECIALIZATIONS:
                    for periodId in range(HtmlOutput.ROOM_ROW_NUMBER):
                        if periodId == 0:
                            sb.append("<div id='year_")
                            sb.append(year)
                            sb.append("_")
                            sb.append(spec)
                            sb.append("' style='padding: 0.5em'>\n")
                            sb.append("<table style='border-collapse: collapse; width: 95%'>\n")
                            sb.append(HtmlOutput.getTableHeader(year, spec, sectionNum))
                        else:
                            key = (periodId, year, spec)
                            year_duration = (
                                slot_table[key] if key in slot_table.keys() else None
                            )
                            year_schedule = (
                                time_table[key] if key in time_table.keys() else None
                            )
                            sb.append("<tr>")

                            for indexId in range(HtmlOutput.ROOM_COLUMN_NUMBER * sectionNum - sectionNum + 1):
                                if indexId == 0:
                                    sb.append(
                                        "<th style='border: .1em solid black; padding: .25em' scope='row' colspan='1'>"
                                    )
                                    sb.append(HtmlOutput.PERIODS[periodId])
                                    sb.append("</th>\n")
                                    continue

                                if year_schedule is None and year_duration is None:
                                    continue

                                content = (
                                    year_schedule[indexId] if year_schedule is not None else None
                                )
                                sb.append(HtmlOutput.getHtmlCell(content, year_duration[indexId]))
                            sb.append("</tr>\n")

                        if periodId == HtmlOutput.ROOM_ROW_NUMBER - 1:
                            sb.append("</table>\n</div>\n")
            else:
                for periodId in range(HtmlOutput.ROOM_ROW_NUMBER):
                    if periodId == 0:
                        sb.append("<div id='year_")
                        sb.append(year)
                        sb.append("' style='padding: 0.5em'>\n")
                        sb.append("<table style='border-collapse: collapse; width: 95%'>\n")
                        sb.append(HtmlOutput.getTableHeader(year, "", sectionNum))
                    else:
                        key = (periodId, year, "")
                        year_duration = (
                            slot_table[key] if key in slot_table.keys() else None
                        )
                        year_schedule = (
                            time_table[key] if key in time_table.keys() else None
                        )
                        sb.append("<tr>")

                        for indexId in range(HtmlOutput.ROOM_COLUMN_NUMBER * sectionNum - sectionNum + 1):
                            if indexId == 0:
                                sb.append(
                                    "<th style='border: .1em solid black; padding: .25em' scope='row' colspan='1'>"
                                )
                                sb.append(HtmlOutput.PERIODS[periodId])
                                sb.append("</th>\n")
                                continue

                            if year_schedule is None and year_duration is None:
                                continue

                            content = (
                                year_schedule[indexId] if year_schedule is not None else None
                            )
                            sb.append(HtmlOutput.getHtmlCell(content, year_duration[indexId]))
                        sb.append("</tr>\n")

                    if periodId == HtmlOutput.ROOM_ROW_NUMBER - 1:
                        sb.append("</table>\n</div>\n")
                    
        return "".join(str(v) for v in sb)

 

    @staticmethod
    def getTableHeader(year, spec, sectionNum):

        if spec == "":
            sb = [
                "<tr><th style='border: .1em solid black' scope='col' rowspan='2'>Year: ",
                year,
                "</th>\n",
            ]
        else:
            sb = [
                "<tr><th style='border: .1em solid black' scope='col' rowspan='2'>Year: ",
                year,
                ", Spec: ",
                spec,
                "</th>\n",
            ]
            
        for weekDay in HtmlOutput.WEEK_DAYS:
            sb.append(
                "<th style='border: .1em solid black; padding: .25em; width: 15%' scope='col' colspan='" + str(sectionNum) + "'>"
            )
            sb.append(weekDay)
            sb.append("</th>\n")
        sb.append("</tr>\n")
        sb.append("<tr>\n")

        if sectionNum > 1:
            for i in range(Constant.DAYS_NUM * sectionNum):
                sb.append("<th style='border: .1em solid black; padding: .25em'>Sec: ")
                sb.append(i % sectionNum + 1)
                sb.append("</th>\n")

        sb.append("</tr>\n")
        return "".join(str(v) for v in sb)
