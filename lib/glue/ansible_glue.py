
from ansible import playbook
from ansible.inventory import Host, Inventory, Group, InventoryScript
import ansible.callbacks as callbacks
import sys
import os


def run_ansible_in_python(task):
    stats = callbacks.AggregateStats()
    ## everything between this comment
    ## and the "end" should hopefully not be necessary
    ## after Ansible 1.4.6 or 1.5 is released, since there
    ## will be an implicit sys.executable interpreter for the localhost
    ## host. This will almost certainly need tweaking anyway for dynamic inventory
    ## in ec2. I'm not sure yet how this would work.
    localhost = Host('localhost')
    localhost.set_variable('ansible_python_interpreter', sys.executable)
    all_group = Group('all')
    all_group.add_host(localhost)
    inventory = Inventory(None)
    inventory.add_group(all_group)
    os.putenv('EC2_INI_PATH', 'lib/glue/ec2-external.ini')
    ec2_inventory = InventoryScript(filename='lib/glue/ec2.py')
    inventory.parser = ec2_inventory
    [inventory.add_group(group) for group in ec2_inventory.groups.values()]
    ## end

    pb = playbook.PlayBook(playbook=task.inputs[0].abspath(),
                           inventory=inventory,
                           stats=stats,
                           callbacks=callbacks.PlaybookCallbacks(verbose=3),
                           runner_callbacks=callbacks.PlaybookRunnerCallbacks(stats, verbose=3)
                           )
    pb.run()


def run_ansible_in_shell(task):
    # "localhost ansible_python_intepreter='+ sys.executable + ',"
    # for now this won't work...
    task.exec_command('ansible-playbook -i  '
                      + task.inputs[0].abspath(),
                      stdout=sys.stdout, stderr=sys.stderr)