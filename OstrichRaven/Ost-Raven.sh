#!/bin/bash

set -e
echo "Ost-Raven.sh"
# python3 create_lake_rvh.py
cp ./SE.rvp RavenInput/SE.rvp
cp ./SE.rvh RavenInput/SE.rvh
# cp ./SE.rvc RavenInput/SE.rvc
# cp ./Lakes.rvh RavenInput/Lakes.rvh

cd RavenInput

rm -r ./output
./Raven.exe SE -o output
cd ..

exit 0