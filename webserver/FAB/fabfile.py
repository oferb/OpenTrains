from fabric.api import * #@UnusedWildImport
import fabric.contrib.files
import os

# Configuration for DigitalOcean
# You need to create the user manually
env.hosts = ['192.241.154.128']
env.user = 'opentrain'

# Ec2 configuration

env.django_base_dir = os.path.join('/home/%s/' % (env.user),'work/OpenTrains/webserver/opentrain')
env.repo = 'https://github.com/oferb/OpenTrains.git'
env.repo_dir = 'work/OpenTrains'  #dir after clone
env.dns = 'opentrain.hasadna.org.il'

def get_ctx():
    ctx = {
           'HOME' : '/home/' + env.user,
            'IP' : env.host,
            'USER' : env.user,
            'DJANGO_BASE_DIR' : env.django_base_dir,
            'DNS' : env.dns
            }
    return ctx


@task
def create_new():
    """ run all tasks to after new instance is created """
    update_host()
    update_apt()
    update_pip()
    update_git()
    update_conf()
    db_first_time()
    
@task
def update_host():
    """ general host update """
    sudo('apt-get update')
    sudo('apt-get --yes -q upgrade')

@task
def update_apt(package=None):
    """ updates/install all apt packages """
    packages = ('git',
    			'nginx',
    			'postgresql-client',
    			'postgresql',
    			'supervisor',
                'python-pip',
		'gfortran',
                'libpq-dev',
                'python-dev',
                'redis-server',
                'libfreetype6-dev'
    	)

    for p in packages:
        if not package or p == package:
            if p == 'nginx':
                sudo('apt-get install -q --yes --upgrade python-software-properties')
                sudo('add-apt-repository --yes ppa:nginx/stable')
                sudo('apt-get -q update')
            if p == 'redis-server':
                sudo('add-apt-repository --yes ppa:rwky/redis')
                sudo('apt-get -q update')
            print 'Installing package ' + p
            sudo('apt-get install -q --yes --upgrade %s' % (p))

def get_basedir(dir):
    dir = dir.rstrip('/')
    return dir.rpartition('/')[0]

@task
def update_git():
    """ clone/pull git repo """
    basedir = get_basedir(env.repo_dir)
    run('mkdir -p %s' % (basedir))
    clone = not fabric.contrib.files.exists(env.repo_dir)
    if clone:
	   with cd(basedir): 
	       run('git clone %s' % (env.repo))
    else:
        with cd(env.repo_dir):
           run('git pull')

    # collect static
    with cd(env.django_base_dir):
        run('python manage.py collectstatic --noinput')
    
    
           
@task
def update_pip():
    """ updates/install all pip packages """
    sudo('pip install --upgrade pip')
    sudo('pip install setuptools --no-use-wheel --upgrade')
    put('files/requirements.txt','/tmp/requirements.txt')
    sudo('pip install -r /tmp/requirements.txt')
    
@task
def update_conf():
    """ update conf file for supervisor/nginx """
    ctx = get_ctx()
    
    run('mkdir -p log')
    run('mkdir -p bin')
    
    # copy gunicorn script
    fabric.contrib.files.upload_template('files/run_gunicorn.sh',
                                         'bin',
                                         context=ctx
                                         )
    with cd('bin'):
        run('chmod +x run_gunicorn.sh')
        
    # NGINX
    fabric.contrib.files.upload_template('files/nginx/opentrain.conf',
                                         '/etc/nginx/sites-available/',
                                         context=ctx,
                                         use_sudo=True)
    sudo('rm -f /etc/nginx/sites-enabled/opentrain.conf')
    sudo('rm -f /etc/nginx/sites-enabled/default')
    sudo('ln -s /etc/nginx/sites-available/opentrain.conf /etc/nginx/sites-enabled/opentrain.conf')
    # This is an issue in DigitalOcean
    fabric.contrib.files.uncomment('/etc/nginx/nginx.conf','server_names_hash_bucket_size',use_sudo=True)
    sudo('service nginx reload')
    sudo('service nginx restart')

    # restart conf
    fabric.contrib.files.upload_template('files/supervisor/opentrain.conf',
                                         '/etc/supervisor/conf.d/',
                                         context=ctx,
                                         use_sudo=True)
    sudo('sudo supervisorctl reread')
    sudo('supervisorctl update')
    sudo('supervisorctl restart opentrain')


@task
def db_first_time():
    """ initialize Postgres DB """
    with cd(env.django_base_dir):
        run('python manage.py sqlcreate --router=default| sudo -u postgres psql')
        run('python manage.py syncdb --noinput')
        
@task
def db_reset():
    """ Reset (deletes and recreate) Postgres DB """
    with cd(env.django_base_dir):
        run('echo "DROP DATABASE opentrain;" | sudo -u postgres psql')
        run('python manage.py sqlcreate --router=default| grep -v "CREATE USER" | sudo -u postgres psql')
        run('python manage.py syncdb --noinput')
        
@task
def reload_gunicorn():
    """ reload the gunicorn process """
    run('kill -HUP `cat %(HOME)s/opentrain.id`' % get_ctx())


@task
def download_db():
    """ Opentrain only. backup db on remote server and donwload it locally """
    with cd(env.django_base_dir):
        run('./backup.py')
        import os
        localfile = '/tmp/backup.gz'
        remotefile = '/tmp/backup.gz'
        if os.path.exists(localfile):
            os.remove(localfile)    
        get(remotefile,localfile)
        os.system('cd ../opentrain ; ./restore.py')
    
    
        
@task
def analyze_reports():
    with cd(env.django_base_dir):
        run('./reanalyze.py')
        
        



    
    


