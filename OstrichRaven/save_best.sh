#!/bin/bash

set -e

echo "saving input files for the best solution found ..."

if [ ! -e best ] ; then
    mkdir -p best/RavenInput
fi

cp -Rf ./RavenInput/SE.rv*                  ./best/RavenInput/
cp -Rf ./RavenInput/Lakes.rvh               ./best/RavenInput/
cp -Rf ./RavenInput/channel_properties.rvp  ./best/RavenInput/
cp -Rf ./RavenInput/SubBasinProperties.rvh  ./best/RavenInput/
cp -Rf ./RavenInput/output                  ./best/RavenInput/
cp -Rf ./RavenInput/Raven.exe               ./best/RavenInput/
exit 0