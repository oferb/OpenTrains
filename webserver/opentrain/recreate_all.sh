set -e
eval `python opentrain/print_settings.py -env`
if [ -z $DATA_DIR ] ; then
    echo 'NO DATA_DIR'
    exit 255
fi

echo "DATA_DIR = $DATA_DIR"
mkdir -p $DATA_DIR
chmod -R a+w $DATA_DIR
rm -f $DATA_DIR/db.sqlite3
python manage.py syncdb --noinput



