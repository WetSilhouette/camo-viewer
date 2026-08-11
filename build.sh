#!/bin/bash

MOD_NAME="silhouette.camoViewer"
d=false

while getopts "v:d" flag
do
    case "${flag}" in
        v) v=${OPTARG};;
        d) d=true;;
    esac
done


rm -rf ./build
mkdir ./build
cp -r ./res ./build

# Build AS3
MXMLC=/Users/silhouette/projects/wotmods/flex-sdk/sdk/bin/mxmlc
cd ./as3
rm -f ./bin/*.swf
$MXMLC -load-config+=build-config.xml --output=bin/silhouette.camoViewer.CamoViewerTestWindow.swf src/camoViewer/CamoViewerTestWindow.as
$MXMLC -load-config+=build-config.xml --output=bin/silhouette.camoViewer.CamoGridWindow.swf src/camoViewer/CamoGridWindow.as
cd ../

mkdir -p ./build/res/gui/flash
find ./as3/bin -name "*.swf" -exec cp {} ./build/res/gui/flash/ \;

# Set version
configPath="./build/res/scripts/client/gui/mods/camoViewer/CamoViewer.py"
perl -i -pe "s/{{VERSION}}/$v/g" "$configPath"

# Set debug mode
utilsPath="./build/res/scripts/client/gui/mods/camoViewer/CamoViewer.py"
if [ "$d" = true ]; then
    echo "Building DEBUG version."
    perl -i -pe "s/'{{DEBUG_MODE}}'/True/g" "$utilsPath"
else
    echo "Building RELEASE version."
    perl -i -pe "s/'{{DEBUG_MODE}}'/False/g" "$utilsPath"
fi

python2 -m compileall ./build

meta=$(<meta.xml)
meta="${meta/\{\{VERSION\}\}/$v}"

cd ./build
echo "$meta" > ./meta.xml

folder=$MOD_NAME"_$v.wotmod"

rm -rf $folder

zip -dvr -0 -X $folder res -i "*.pyc"
zip -vr -0 -X $folder meta.xml
zip -dvr -0 -X $folder res -i "*.dds"
zip -dvr -0 -X $folder res -i "*.xml"
zip -dvr -0 -X $folder res -i "*.html"
zip -dvr -0 -X $folder res -i "*.css"
zip -dvr -0 -X $folder res -i "*.js"
zip -dvr -0 -X $folder res -i "*.swf"

cd ../
cp ./build/$folder $folder
rm -rf ./build

cp $folder $MOD_NAME"_$v.mtmod"
