# use this file to generate crab submit config file
source /cvmfs/cms.cern.ch/common/crab-setup.sh
echo "365365" | voms-proxy-init -rfc -voms cms --valid 168:00
python crab.py --num-cores 1 --send-external -s FileBased --work-area crab_projects_mc --dryrun