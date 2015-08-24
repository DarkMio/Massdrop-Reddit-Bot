# coding=utf-8
import threading
import time


class MultiThreader(object):
    """Throw bound methods at it and it joins you threads together."""
    threads = list()         # Holds all threads together.

    def go(self, *args):
        for line in args:
            if len(line) == 1:
                thread = threading.Thread(target=line[0])
            else:
                thread = threading.Thread(target=line[0], args=[1])
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

    def join_threads(self):
        """
        Join threads in interruptable fashion.
        From http://stackoverflow.com/a/9790882/145400
        """
        for t in self.threads:
            while t.isAlive():
                t.join(5)

    @staticmethod
    def get_lock():
        """Returns a threading RLock object

        :return: threading.RLock()
        """
        return threading.RLock()

    @staticmethod
    def repeater(thread):
        """Test method for tinkering with threading."""
        global G
        while True:
            i = G
            print("Thread {}: i = {}".format(thread, i))
            G += 1
            time.sleep(5)


if __name__ == "__main__":
    global G
    G = 1
    threader = MultiThreader()
    threader.go([threader.repeater, 1], [threader.repeater, 2], [threader.repeater, 3])
    try:
        threader.join_threads()
    except KeyboardInterrupt as e:
        print("Exiting.")
