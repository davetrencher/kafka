import krpc
import os

class KrpcHelper:

    BASE_DIR = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__),".."),".."))

    LOG_DIR = os.path.join(BASE_DIR,'logs')

    conn = krpc.connect(name="Local")

    ut = conn.add_stream(getattr, conn.space_center, 'ut')

