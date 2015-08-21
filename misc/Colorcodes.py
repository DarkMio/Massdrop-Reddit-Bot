"""All kinds of color codes to colorize console output.
"""


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30,38):
            s1 = ''
            for bg in range(40,48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print(s1)
        print('\n')

if __name__ == '__main__':
    print_format_table()
    import ctypes

    # Constants from the Windows API
    STD_OUTPUT_HANDLE = -11
    FOREGROUND_RED    = 0x0004 # text color contains red.

    def get_csbi_attributes(handle):
        # Based on IPython's winconsole.py, written by Alexander Belchenko
        import struct
        csbi = ctypes.create_string_buffer(22)
        res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, csbi)

        (bufx, bufy, curx, cury, wattr,
        left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        return wattr


    handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    reset = get_csbi_attributes(handle)

    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, FOREGROUND_RED)
    print("Cherry on top")
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, reset)