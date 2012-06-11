from fabric.api import *

def deploy():
    with cd(env.project_path):
        run('git pull')
        run('git submodule update --init')

        with cd('pportal'):
            run('python manage.py syncdb')
            run('python manage.py collectstatic --noinput')

    sudo('service %s restart' % env.appserver_task)
    sudo('service %s restart' % env.xforms_backend_task)


def integration():
    env.user = 'root'
    env.hosts = ['jikan.eclinicalhosting.com']
    env.project_path = '/opt/portal/oc-patient-portal'
    env.appserver_task = 'pportal'
    env.xforms_backend_task = 'xformengine'

def staging():
    pass

def prod():
    pass
