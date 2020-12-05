from environs import Env

env = Env()

scp_host = env.str("DINO_SCP_HOST", "0.0.0.0")
scp_port = env.int("DINO_SCP_PORT", 5252)
scp_ae_title = env.str("DINO_SCP_AET", "DINO")

debug = env.bool("DINO_DEBUG", True)
