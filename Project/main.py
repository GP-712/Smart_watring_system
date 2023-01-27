import subprocess

path = r"/Project"
tasks = ['mqttListener.py', 'website.py','backupLocaly.py']
task_processes = [
    subprocess.Popen(r'python \%s' % (task), shell=True)
    for task
    in tasks
]
for task in task_processes:
    task.wait()