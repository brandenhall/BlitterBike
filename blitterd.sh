#! /bin/sh
### BEGIN INIT INFO
# Provides:          blitterbike
# Required-Start:    $local_fs $remote_fs $network $syslog
# Required-Stop:     $local_fs $remote_fs $network $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start/stop BlitterBike server
### END INIT INFO

logger "blitterd: Start script executed"
BLITTER_BIKE_PATH="/home/bhall/dev"
export PYTHONPATH="$BLITTER_BIKE_PATH:$PYTHONPATH"

case "$1" in
  start)
    logger "blitterd: Starting"
    echo "Starting blitterd..."
    twistd -y "$BLITTER_BIKE_PATH/blitterd.tac" -l "$BLITTER_BIKE_PATH/blitterd.log" --pidfile "$BLITTER_BIKE_PATH/blitterd.pid"
    ;;
  stop)
    logger "blitterd: Stopping"
    echo "Stopping blitterd..."
    kill `cat "$BLITTER_BIKE_PATH/blitterd.pid"`
    ;;
  *)
    logger "blitterd: Invalid usage"
    echo "Usage: blitterbike {start|stop}"
    exit 1
    ;;
esac

exit 0
