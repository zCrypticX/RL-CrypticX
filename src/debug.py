# Debugging Currently Doesn't Work At The Moment, But Don't Mind If You Can Fix It In A Pull Request...

import logging
logger = logging.getLogger(__name__)

def cryptic_debug(self, packet):
    logging.basicConfig(filename="RLCryptic.log", level=logging.INFO)
    logger.info("Starting Logging : CONSOLE")

    logger.info("{ Cryptic Simple Debugging } : ")
    logger.info("RL-CrypticBot Position Is At : ", packet.game_cars[self.index].physics.location)
    logger.info("Ball Position Is At : ", packet.game_ball.physics.location)

    logger.info("Finished Logging : CONSOLE")