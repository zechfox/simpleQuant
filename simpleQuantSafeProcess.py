import logging
from multiprocessing import Process
from logging.handlers import SocketHandler, DEFAULT_TCP_LOGGING_PORT


MyLogger = logging.getLogger(__name__)

class SimpleQuantSafeProcess(Process):

  def __init__(self, feedback_queue):
    Process.__init__(self)
    self.feedback_queue = feedback_queue
    rootlogger = logging.getLogger('')
    rootlogger.setLevel(logging.INFO)
    socketh = SocketHandler('localhost', DEFAULT_TCP_LOGGING_PORT)
    rootlogger.addHandler(socketh)


  def saferun(self):
    """Method to be run in sub-process; can be overridden in sub-class"""
    MyLogger.info("Process start!")
    if self._target:
        self._target(*self._args, **self._kwargs)

  def run(self):
    try:
        self.saferun()
    except Exception as e:
        MyLogger.error(e)
        raise e