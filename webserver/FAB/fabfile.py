from fabric.api import * #@UnusedWildImport
import fabric.contrib.files
import os

#env.hosts = ['192.241.154.128']
#env.user = 'opentrain'
env.hosts = ['ec2-50-16-67-1.compute-1.amazonaws.com']
env.user = 'ubuntu'
env.key_filename = os.path.expanduser('~/chat.pem')
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
    update_host()
    update_apt()
    update_pip()
    update_git()
    update_conf()
    db_first_time()
    
@task
def update_host():
    sudo('apt-get update')
    sudo('apt-get --yes -q upgrade')

@task
def update_apt(package=None):
    packages = ('git',
    			'nginx',
    			'postgresql-client',
    			'postgresql',
    			'supervisor',
                'python-pip',
                'libpq-dev',
                'python-dev'
    	)

    for p in packages:
        if not package or p == package:
            if p == 'nginx':
                sudo('apt-get install -q --yes --upgrade python-software-properties')
                sudo('add-apt-repository --yes ppa:nginx/stable')
                sudo('apt-get update')
            print 'Installing package ' + p
            sudo('apt-get install -q --yes --upgrade %s' % (p))

def get_basedir(dir):
    dir = dir.rstrip('/')
    return dir.rpartition('/')[0]

@task
def update_git():
    basedir = get_basedir(env.repo_dir)
    run('mkdir -p %s' % (basedir))
    clone = not fabric.contrib.files.exists(env.repo_dir)
    if clone:
	   with cd(basedir): 
	       run('git clone %s' % (env.repo))
    else:
        with cd(env.repo_dir):
           run('git pull')
           
@task
def update_pip():
    sudo('pip install --upgrade pip')
    sudo('pip install setuptools --no-use-wheel --upgrade')
    put('files/requirements.txt','/tmp/requirements.txt')
    sudo('pip install -r /tmp/requirements.txt')
    
@task
def update_conf():
    
    ctx = get_ctx()
    
    run('mkdir -p log')
    run('mkdir -p bin')
    
    # collect static
    with cd(env.django_base_dir):
        run('python manage.py collectstatic --noinput')
    
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
    with cd(env.django_base_dir):
        run('python manage.py sqlcreate --router=default| sudo -u postgres psql')
        run('python manage.py syncdb --noinput')
        
@task
def db_reset():
    with cd(env.django_base_dir):
        run('echo "DROP DATABASE opentrain;" | sudo -u postgres psql')
        run('python manage.py sqlcreate --router=default| grep -v "CREATE USER" | sudo -u postgres psql')
        run('python manage.py syncdb --noinput')
        
@task
def reload_gunicorn():
    run('kill -HUP `cat %(HOME)s/opentrain.id`' % get_ctx())


@task
def download_db():
    with cd(env.django_base_dir):
        run('./backup.py')
        import os
        localfile = '/tmp/backup.gz'
        remotefile = '/tmp/backup.gz'
        if os.path.exists(localfile):
            os.remove(localfile)    
        get(remotefile,localfile)
        os.system('cd ../opentrain ; ./restore.py')
    
    
        
      



    
    


