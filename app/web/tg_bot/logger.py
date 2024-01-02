from json_logger_stdout import JSONLoggerStdout
import socket

logger = JSONLoggerStdout(
    container_id=socket.gethostname(),
    container_name="BOT"
)