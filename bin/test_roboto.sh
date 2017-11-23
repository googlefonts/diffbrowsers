BEFORE_DIR=$1
AFTER_DIR=$2
OUT_DIR=$3

set -e 

after_fonts=$(ls $AFTER_DIR/*.ttf);

for after_font in $after_fonts
do
    filename=$(basename $after_font);
    before_font=$BEFORE_DIR/$filename;
    python ./bin/test_roboto_hinted_src.py $before_font $after_font $OUT_DIR
done