#!/usr/bin/python2

from httplib2 import Http
from itertools import groupby, ifilterfalse, ifilter
from launchpadlib.launchpad import Launchpad
from os import environ
from sys import exit
from json import dumps as to_json

CACHE_DIR = "~/.launchpadlib/cache/"
LAUNCHPAD = Launchpad.login_anonymously('just testing', 'production', CACHE_DIR, version="devel")
H = Http(".cache")

try:
    PROJECT_ID = environ["PROJECT_ID"]
except KeyError:
    print "Please set the environment variable [PROJECT_ID]"
    exit(1)



def wishes_as_specs( tasks ): 
    class Spec():
        pass

    def to_spec( w ):
       s = Spec()
       s.is_complete = ( w.status == "Fix Committed" )
       # there is no importance set for wishes as "Importance" is used to
       # mark tasks as wishes... considering wishes as Medium
       s.priority = "Medium"
       s.milestone = w.milestone
       return s

    return map(to_spec, filter( lambda t:t.importance == "Wishlist", tasks))

PROJECT = LAUNCHPAD.projects[PROJECT_ID]
#ALL_TASKS = PROJECT.searchTasks()
#ALL_BUGS = filter( lambda t:t.importance != "Wishlist", ALL_TASKS )
#ALL_WISHES_AS_SPECS = wishes_as_specs( ALL_TASKS )
FOCUS_SERIES_NAME = PROJECT.development_focus.name

def milestones_tasks( milestones ):
    return reduce(lambda acc,curr:acc + list(PROJECT.searchTasks(milestone=curr)), milestones, [] )
    

for s in filter(lambda s:s.active, PROJECT.series):
    if any(s.releases): 
        last_release_version = s.releases[0].version
        last_release_date = s.releases[0].date_released.isoformat()
    else:
        last_release_version = ""
        last_release_date = ""

    active_milestones = filter(lambda m:m.release is None, s.active_milestones)

    if any(active_milestones):
        active_specs = filter(lambda s: s.milestone is not None and s.milestone in active_milestones, s.all_specifications)
        tasks = milestones_tasks( active_milestones )
        active_bugs = filter( lambda t:t.importance != "Wishlist", tasks )
        active_wishes = wishes_as_specs( tasks )

        active_specs = active_specs + active_wishes

        nb_of_complete_specs = len( filter( lambda s:s.is_complete, active_specs ))

        uncomplete_specs = filter( lambda s:not s.is_complete, active_specs )
        uncomplete_bugs = filter( lambda s:s.status != "Fix Committed", active_bugs )

        high_uncomplete_specs = filter( lambda s:s.priority == "Essential" or s.priority == "High", uncomplete_specs )
        high_uncomplete_bugs = filter( lambda b:b.importance == "High", uncomplete_bugs )
    
 
        if any(active_specs):
            active_progression = int((nb_of_complete_specs * 100) / len(active_specs))
        else:
            active_progression = 0

        json_payload = to_json({
            "focus": s.name == FOCUS_SERIES_NAME,
            "series-name": s.name, 
            "value": active_progression,
            "active-milestones-title": " > ".join(map(lambda m:m.name, active_milestones)),
            "remaining-bugs-total":len(uncomplete_bugs),
            "remaining-bugs-high":len(high_uncomplete_bugs),
            "remaining-specs-total":len(uncomplete_specs),
            "remaining-specs-high":len(high_uncomplete_specs),
            "last-release-version":last_release_version,
            "last-release-date":last_release_date,
            "auth_token":"YOUR_AUTH_TOKEN"
        })
    else:
        json_payload = to_json({
            "focus": s.name == FOCUS_SERIES_NAME,
            "series-name": s.name, 
            "value": "-",
            "active-milestones-title": "none",
            "remaining-bugs-total":"-",
            "remaining-bugs-high":"-",
            "remaining-specs-total":"-",
            "remaining-specs-high":"-",
            "last-release-version":last_release_version,
            "last-release-date":last_release_date,
            "auth_token":"YOUR_AUTH_TOKEN"
        })
    
    print json_payload
    H.request("http://localhost:3030/widgets/"+PROJECT_ID+"_series_"+s.name,"POST", body=json_payload)
    if s.name == FOCUS_SERIES_NAME:
        H.request("http://localhost:3030/widgets/"+PROJECT_ID+"_focus_series_"+s.name,"POST", body=json_payload)
   
