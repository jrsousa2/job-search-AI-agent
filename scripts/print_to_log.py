# PRINTS TO EXTERNAL LOG FILE 
# OVERWITES THE FILE SO ONE KNOWS WHAT ATS URL ERRORS REMAIN
# args IS A TUPLE
def print_to_log(Arq, txt, *args):
    mode = "w" if not hasattr(print_to_log, "called") else "a"

    with open(Arq, mode, encoding="utf-8") as file:
        file.write(txt.format(*args))

    print_to_log.called = True   