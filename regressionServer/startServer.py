import os, sys, inspect
project_root_dir = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])+'../../')
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)
print(project_root_dir)

from simpleQuantRegressionServer import SimpleQuantRegressionServer

def main():
    server = SimpleQuantRegressionServer()
    server.start()


if __name__ == '__main__':
    main()
