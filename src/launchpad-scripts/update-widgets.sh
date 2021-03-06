#!/bin/bash
if [ -f /tmp/projects_ids ]; then 
    export PROJECTS_IDS=$(cat /tmp/projects_ids)
 fi

if [ "$PROJECTS_IDS" == "" ]; then 
    echo "PROJECTS_IDS is undefined. Please set a PROJECTS_IDS env variable corresponding to a list of launchpad projects separated by commas."
    exit 1
fi

BASEDIR=$(dirname $0)

for PROJECT_ID in $(echo $PROJECTS_IDS | tr ',' ' '); do
    export PROJECT_ID
    if [ ! -f /tmp/$PROJECT_ID.lock ]; then
        touch /tmp/$PROJECT_ID.lock
        $BASEDIR/series.py >> /tmp/output.log 2>&1 
        $BASEDIR/bugs.py >> /tmp/output.log 2>&1 
        $BASEDIR/milestones.py >> /tmp/output.log 2>&1 
        rm /tmp/$PROJECT_ID.lock
    fi
done
