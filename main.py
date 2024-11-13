from service import OlaServis
from tuke_openlab import environment
import config
import logging
import sys


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    OlaServis(
        config.HOST,
        config.PORT,
        environment.simulation_env("os228mz"),
        environment.simulation_env("os228mz"),
    ).run()
