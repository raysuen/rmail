#!/bin/bash 

git add *
git commit -m "`/Users/raysuen/raysuen/bin/rdate.py -f "%Y%m%d"` raysuen"
git push -u origin "master"
