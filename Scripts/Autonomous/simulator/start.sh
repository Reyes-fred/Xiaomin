set -x
echo
echo "Red balloon simulator"
echo

export path=/home/alfredo/Desktop/Xiaomin/Scripts/Autonomous/scripts
export qground=/home/alfredo/Downloads/
export sour=/home/alfredo/Desktop/Xiaomin/Setup/

workon cv 

#Execute source
cd $sour
source config.sh

#Execute mavlink
cd $path
./linux_run_strategy.sh &
#Wait until mavproxy launch

#Execute QGroundControl
cd $qground
sleep 10
./QGroundControl.AppImage &

sleep 10
#Execute Python Ballon
cd $path
python balloon_strategy.py &
sleep 10
