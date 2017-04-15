data=$1
directory=$2

cd $directory
mkdir split
mv $data split/$data
cd 'split'
split -l 50000 $data
rm $data
cd ..
