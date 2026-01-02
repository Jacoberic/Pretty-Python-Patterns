
#*log_start is a function that sets the loguru log settings for a bunch of different trace levels.
#*The intent is that for every process, log_start(process_name) would be called at the start of it.

#*TRACE
#*I recently added this log level, I intend to use it for things like logging every ZMQ message sent, which is sometimes nice but is also often clutter.
#*I put this in it's own folder because it might end up with a bunch of files since it logs every.

#*DEBUG
#*This is the main log file I look at. I use logger.debug('text') when I want to log something but not print it.

#*INFO
#*This doesn't actually set up a file to save, but replaces the print function.
#*I always print with logger.info('text') now, because that prints and also saves it to the debug and trace log file.

#*ERROR
#*This only logs errors.
#*My try excepts basically always look like:
#try:
#  1/0
#except Exception:
#  logger.exception('Error')
#*Because that will log the full exception description and the variables.
#*Look at this, it's beautiful.
# 2025-06-10 12:48:10.804 | ERROR    | main                   20 | Error
# Traceback (most recent call last):

#   File "c:\Users\m87423.ceo\LocalDocuments\Email Example\main.py", line 18, in <module>
#     x/y
#     │ └ 0
#     └ 1

# ZeroDivisionError: division by zero

#*I chose a rotation of 8 MB because bigger than that VSCode has trouble handling. 


from loguru import logger

def log_start(process='main'):
    logger.remove()

    #*TRACE
    logger.add(
        f"logs/trace/{process} trace.log",
        level='TRACE',
        backtrace = False,
        enqueue = True,
        rotation = '8 MB',
        compression = 'zip',
        retention = '1 week',
        format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{module:<20}</cyan> <cyan>{line:>4}</cyan> | <level>{message}</level>"
    )

    #*DEBUG
    logger.add(
        f"logs/{process}.log",
        level='DEBUG',
        backtrace = False,
        enqueue = True,
        rotation = '8 MB',
        compression = 'zip',
        retention = '1 week',
        format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{module:<20}</cyan> <cyan>{line:>4}</cyan> | <level>{message}</level>"
    )

    #*INFO
    logger.add(
        lambda msg: print(msg, end=''),#The supplied formatted msg has \n already
        level='INFO',
        backtrace=False,
        diagnose=False,
        format="<green>{time:HH:mm}</green> | <level>{message}</level>"
    )

    #*ERROR
    logger.add(
        f"logs/errors/{process} errors.log",
        level='ERROR',
        backtrace = False,
        enqueue = True,
        rotation = '8 MB',
        compression = 'zip',
        retention = '1 week',
        format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{module:<20}</cyan> <cyan>{line:>4}</cyan> | <level>{message}</level>"
    )
    
    logger.info('')
    logger.info('________________________________________________________________________')
    logger.info(f'Start of {process} log')
