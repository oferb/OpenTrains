from fabric.api import * #@UnusedWildImport
import fabric.contrib.files

env.hosts = ['192.241.154.128']
env.user = 'opentrain'
env.password = 'opentrain'


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
            print 'Installing package ' + package
            sudo('apt-get install -q --yes --upgrade %s' % (p))

@task
def update_git():
    run('mkdir -p work')
    clone = not fabric.contrib.files.exists('~/work/OpenTrains')
    if clone:
	   with cd('work'):
	       run('git clone https://github.com/oferb/OpenTrains.git')
    else:
        with cd('work/OpenTrains'):
           run('git pull')
           
@task
def update_pip():
    sudo('pip install --upgrade pip')
    sudo('pip install setuptools --no-use-wheel --upgrade')
    sudo('pip install -r ~/work/OpenTrains/requirements.txt')
    
                 





