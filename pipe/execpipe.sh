#!/bin/bash

while true; do eval "$(cat /home/dimitar/wired-brain/pipe/mypipe)" &> /home/dimitar/wired-brain/pipe/output.txt; done
