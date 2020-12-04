from environs import Env

env = Env()

scp_host = env.str("SCP_HOST", "0.0.0.0")
scp_port = env.int("SCP_PORT", 5252)
scp_ae_title = env.str("SCP_AE_TITLE", "DINO")

debug = env.bool("DEBUG", True)
