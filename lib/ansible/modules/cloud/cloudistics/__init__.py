# Get the source and set it up correctly
# git clone git@github.com:<your repo location>/ansible.git --recursive
# cd ansible
# git remote add upstream https://github.com/ansible/ansible

# ## Setup your virtual env and activate it
# 9343  source hacking/env-setup
# pip install -r ./requirements.txt

# Install the requirements that are needed and then test cloudistics
# ansible-test units --tox --python 2.7 --requirements cloudistics

# This should work but does not for me for some reason
# ansible-test sanity --test validate-modules lib/ansible/modules/cloud/cloudistics/cl_app.py

# Test the module against a live system
# hacking/test-module -m lib/ansible/modules/cloud/cloudistics/cl_app.py -I
# ansible_python_interpreter=`which python` -a "name='xx 1' state=absent" -c

# hacking/test-module -m lib/ansible/modules/cloud/cloudistics/cl_app.py -I
# ansible_python_interpreter=`which python`
# -a "name='xx' state=present template_name='World Community Grid'
# category_name=Default data_center_name=DC2
# migration_zone_name=MZ1 flash_pool_name=SP1 network_names=[Vnet1]"








# hacking/test-module -m lib/ansible/modules/cloud/cloudistics/cl_app_action.py -I
# ansible_python_interpreter=`which python` -a "name='xx 1' action=stop"