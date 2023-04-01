#!/bin/bash

. /kb/deployment/user-env.sh

PATH=/root/miniconda/bin:$PATH

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests" 
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  cd /data
  curl -L https://www.dropbox.com/s/y57z4od54f4ewzc/fine_tuned_fliped_common_2048_two.pkl?dl=0 > fine_tuned_fliped_common_2048_two.pkl
  curl -L https://www.dropbox.com/s/15mpttx02yp0hq7/pretrained_model2.pkl?dl=0 > pretrained_model2.pkl 
 
  if [ -f fine_tuned_fliped_common_2048_two.pkl ] && [ -f pretrained_model2.pkl ]; then
  	touch __READY__
  else
    echo "Init failed"
  fi
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
