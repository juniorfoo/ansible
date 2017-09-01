## Setup

### Get the source and set it up correctly
```shell
$ git clone git@github.com:<your repo location>/ansible.git --recursive
$ cd ansible
$ git remote add upstream https://github.com/ansible/ansible
```

### Setup your virtual env and activate it
```shell
$ source hacking/env-setup
$ pip install -r ./requirements.txt
```

## Testing

### Hacking around (against a live system)

##### Delete an application
```shell
$ hacking/test-module -m lib/ansible/modules/cloud/cloudistics/cl_app.py -I 
$ ansible_python_interpreter=`which python` -a "name='xx 1' state=absent" -c
````

##### Stop an application
```shell
$ hacking/test-module -m lib/ansible/modules/cloud/cloudistics/cl_app_action.py -I
$ ansible_python_interpreter=`which python` -a "name='xx 1' action=stop"
```

### All Tests (With Docker)
* `ansible-test sanity --docker --python 2.7 cl_app`
* Note pylint-ansible-test fails on tests from aws might want to `--skip-test pylint-ansible-test`

### All Tests (Without Docker -- DOES NOT WORK ON MAC)
* `ansible-test sanity --python 2.7 cl_app`

### Compile Tests
* `ansible-test compile --python 2.7 cl_app`
* `ansible-test compile --python 2.7 cl_app_action`

### Doc Tests
* `ansible-test sanity --test ansible-doc --python 2.7 cl_app`
* `ansible-test sanity --test ansible-doc --python 2.7 cl_app_action`

### Pep8 Tests
* `ansible-test sanity --test ansible-doc --python 2.7 cl_app`
* `ansible-test sanity --test ansible-doc --python 2.7 cl_app_action`

### Integration Tests
* `ansible-test integration -v cloudistics`


