#! /bin/sh

netconvert --node-files=nodes.xml --edge-files=edges.xml --output-file=network.xml

sumo-gui -c sumocfg -g settings.xml
