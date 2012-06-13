#! /bin/bash
### BEGIN INIT INFO
# Provides:          blitterbike
# Required-Start:    $local_fs $remote_fs $network $syslog
# Required-Stop:     $local_fs $remote_fs $network $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start/stop BlitterBike server
### END INIT INFO

logger "blitterd: Start script executed"

pushd `dirname $0` > /dev/null
BLITTERBIKEPATH=`pwd -P`
popd > /dev/null

export PYTHONPATH="$BLITTERBIKEPATH:$PYTHONPATH"
export BLITTERBIKEPATH="$BLITTERBIKEPATH"

case "$1" in
  start)
    logger "blitterd: Starting"
    echo "Starting blitterd..."
    /usr/local/bin/twistd -y "$BLITTERBIKEPATH/blitterd.tac" -l "$BLITTERBIKEPATH/blitterd.log" --pidfile "$BLITTERBIKEPATH/blitterd.pid"
    ;;
  stop)
    logger "blitterd: Stopping"
    echo "Stopping blitterd..."
    kill `cat "$BLITTERBIKEPATH/blitterd.pid"`
    ;;
  *)
    logger "blitterd: Invalid usage"
    echo "Usage: blitterbike {start|stop}"
    exit 1
    ;;
esac

exit 0
