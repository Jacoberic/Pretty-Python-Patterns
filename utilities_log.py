from pathlib import Path

from loguru import logger

def log_start(device='main'):
    logger.remove()

    logger.add(
        lambda msg: print(msg, end=''),#The supplied formatted msg has \n already
        backtrace=False,
        diagnose=False,
        level='INFO',
        format="<green>{time:HH:mm}</green> | <level>{message}</level>"
    )

    logger.add(
        f"logs/{device} debug.log",
        backtrace = False,
        enqueue = False,
        rotation = 'daily',
        compression = 'zip',
        format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{module:<20}</cyan> <cyan>{line:>4}</cyan> | <level>{message}</level>"
    )

    logger.add(
        f"logs/{device} info.log",
        level='INFO',
        backtrace = False,
        enqueue = False,
        rotation = 'daily',
        compression = 'zip',
        format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{module:<20}</cyan> <cyan>{line:>4}</cyan> | <level>{message}</level>"
    )

    logger.add(
        f"logs/{device} errors.log",
        level='ERROR',
        backtrace = False,
        enqueue = False,
        rotation = 'weekly',
        compression = 'zip',
        format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{module:<20}</cyan> <cyan>{line:>4}</cyan> | <level>{message}</level>"
    )
    
    logger.info('________________________________________________________________________')
    logger.info(f'Start of {device} log')

    if device == 'main':
        folder = Path('logs')
        Path(folder / 'archive').mkdir(exist_ok=True)
        for file in folder.glob('*.zip'):
            file.rename(folder / 'archive' / file.name)