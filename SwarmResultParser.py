class ResultData(object):
    __slots__ = ['__timestamp', '__type', '__data', '__opcode']

    def __init__(self, ts, thetype, data, opcode=-1):
        self.__timestamp = ts
        self.__type = thetype
        self.__data = data
        self.__opcode = opcode

    def timestamp(self):
        return self.__timestamp

    def type(self):
        return self.__type

    def data(self):
        return self.__data

    def opcode(self):
        return self.__opcode


class SwarmResultParser(object):
    def __init__(self):
        pass

    def parse_result(self, result):
        ret = []
        it = iter(result)
        #for (ts, line) in it:
        for (line) in it:
            data = []
            # handle multiline results
            if line.startswith('#'):
                length = int(line[1:4])
                for i in range(length):
                    data.append(next(it))
                ret.append(ResultData(0, "multiline", data))
                continue

            # handle single line result
            if line.startswith('='):
                data.append(line[1:])
                ret.append(ResultData(0, "simple", data))
                continue

            # handle notifications
            if line.startswith('*'):
                parts = line[1:].split(':')
                if len(parts) < 2:
                    continue
                data.append(parts[1])
                ret.append(ResultData(0, parts[0], data))
                continue

            # handle sniffer response
            if line.startswith('<'):
                data.append(line)
                ret.append(ResultData(0, "sniffer", data))

            data.append(line)
            ret.append(ResultData(0, "unknown", data))
        return ret
