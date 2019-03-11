this is a demo workspace for dealing with imports /directory structure in 2to3:

each .py file prints out:
    __name__
    __package__
    sys.path

    these outputs can be seen as:
        py2log.txt (run with python27)
        py3log.txt (run with python36)

major difference:

    in modA when trying to import modB functions:
        [fails] from modB import hello2
        [works] from .modB import hello

    this is because subA/ is a "package" and modA is a "module"
    within that package. As such it needs to use .module to refer
    to a sister module.

setup:

root/
    main.py
    subA/
        __init__.py
        modA.py
        modB.py

modA imports from modB
main imports from modA and modB


