#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import json

try:
    import cloudistics
    from cloudistics import ActionsManager, ApplicationsManager, exceptions

    HAS_CL = True
except ImportError:
    HAS_CL = False

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cloudistics import cloudistics_full_argument_spec
from ansible.module_utils.cloudistics import cloudistics_lookup_by_name
from ansible.module_utils.cloudistics import cloudistics_wait_for_action

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}

DOCUMENTATION = '''
---
module: cl_app
short_description: Create/Delete Applications from Cloudistics
extends_documentation_fragment: cloudistics
version_added: "2.4"
author: "Joe Cavanaugh (@juniorfoo)"
description:
   - Create or Remove applications from Cloudistics.
options:
  description:
    description:
      - Description of the application
    required: false
    default: null
  vcpus:
    description:
      - Count of vcpus to be assigned to the new application
    required: false
    default: null
  memory:
    description:
      - Amount of memory to be assigned to the new application
    required: false
    default: null    
  tags:
    description:
      - Tag or list of tags to be provided to the application
    required: false
    default: null
  template_name:
    description:
      - Name of the template to create the application with
    required: false
    default: true
  category_name:
    description:
      - Name of the category to create this application with
    required: false
    default: false
  data_center_name:
    description:
      - Name of the data center to create this application into
    required: false
    default: false
  migration_zone_name:
    description:
      - Name of the migration zone to create this application with
    required: false
    default: true
  flash_pool_name:
    description:
      - Name of the flash pool to create this application with
    required: true
    default: null
  network_names:
    description:
      - Network or list of networks to be provided to the application
    required: true
    default: null
  state:
    description:
      - Should the resource be present or absent.
    required: true
    default: 'present'
    choices: ['present', 'absent']

requirements:
    - "python >= 2.6"
    - "cloudistics >= 0.0.1"
author: "Joe Cavanaugh (@juniorfoo)"
'''

EXAMPLES = '''
- name: Build application
  hosts: localhost
  gather_facts: False
  tasks:
  - name: Build instance request
    cl_app:
      name: xx
      description: xx
      vcpus: 1
      memory: 1073741824
      template_name: World Community Grid
      category_name: Default
      data_center_name: DC2
      migration_zone_name: MZ1
      flash_pool_name: SP1
      network_names: Vnet1
      tag_names: 
        - TT1
        - TT2    
      wait: False
      state: present

- name: Build additional instances
  hosts: localhost
  gather_facts: False
  tasks:
  - name: Build instances request
    cl_app:
      name: "{{ item.name }}"
      description: "{{ item.description }}"
      vcpus: "{{ item.vcpu }}"
      memory: "{{ item.memory }}"
      template_name: "{{ item.template_name }}"
      category_name: "{{ item.category_name }}"
      data_center_name: "{{ item.data_center_name }}"
      migration_zone_name: "{{ item.migration_zone_name }}"
      flash_pool_name: "{{ item.flash_pool_name }}"
      network_names: "{{ item.network_names }}"
      tag_names: "{{ item.tag_names }}"
      wait: "{{ item.wait }}"
    with_items:
      - name: xx1
        description: xx
        vcpus: 1
        memory: 1073741824
        template_name: World Community Grid
        category_name: Default
        data_center_name: DC2
        migration_zone_name: MZ1
        flash_pool_name: SP1
        network_names: Vnet1
        tag_names:
          - TT1
          - TT2    
        wait: True
      - name: xx2
        description: xx
        vcpus: 1
        memory: 1073741824
        template_name: World Community Grid
        category_name: Default
        data_center_name: DC2
        migration_zone_name: MZ1
        flash_pool_name: SP1
        network_names: Vnet1
        tag_names:
          - TT1
          - TT2    
        wait: True
      - name: xx3
        description: xx
        vcpus: 1
        memory: 1073741824
        template_name: World Community Grid
        category_name: Default
        data_center_name: DC2
        migration_zone_name: MZ1
        flash_pool_name: SP1
        network_names: Vnet1
        tag_names:
          - TT1
          - TT2    
        wait: True

- name: Cancel instances
  hosts: localhost
  gather_facts: False
  tasks:
  - name: Cancel by name
    cl_app:
      state: absent
      name: xx1
'''

STATES = ['present', 'absent']
CPU_SIZES = [1, 2, 4, 8, 16, 32, 56]
MEMORY_SIZES = [1024, 2048, 4096, 6144, 8192, 12288, 16384, 32768, 49152, 65536, 131072, 247808]


def wait_for_running(manager, wait_time, uuid):
    instance = None

    try:
        completed = manager.wait_for_running(uuid, wait_time, 2)
        if completed:
            instance = manager.get_instance(uuid)
    except exceptions.CloudisticsAPIError:
        completed = False

    return completed, instance


def main():
    argument_spec = cloudistics_full_argument_spec(
        state=dict(required='present', choices=STATES),
        description=dict(),
        vcpus=dict(aliases=['cpus', 'vcpu', 'cpu']),
        memory=dict(),
        template_name=dict(),
        category_name=dict(),
        data_center_name=dict(),
        migration_zone_name=dict(),
        flash_pool_name=dict(),
        network_names=dict(type='list'),
        tag_names=dict(type='list'),
    )

    a_module = AnsibleModule(
        argument_spec=argument_spec,

        # mutually_exclusive=(
        #     ['template_name', 'template_uuid'],
        # ),

        required_if=(
            [
                ['state', 'absent', ['name']],
                ['state', 'present', ['name', 'template_name', 'category_name', 'data_center_name',
                                      'migration_zone_name', 'flash_pool_name', 'network_names']],
            ]
        ),

        # required_together=(
        #     ['a', 'b', 'b'],
        # ),

        supports_check_mode=True
    )

    name = a_module.params['name']
    state = a_module.params['state']
    wait = a_module.params['wait']
    wait_timeout = a_module.params['wait_timeout']

    changed = False
    completed = False
    status = None

    if not HAS_CL:
        a_module.fail_json(msg='Cloudistics python library required for this module')

    try:
        act_mgr = ActionsManager(cloudistics.client())
        app_mgr = ApplicationsManager(cloudistics.client())
        instance = cloudistics_lookup_by_name(app_mgr, name)

        if a_module.check_mode:
            if state == 'absent':
                a_module.exit_json(instance=instance, changed=(instance is not None))
            elif state == 'present':
                a_module.exit_json(instance=instance, changed=(instance is None))

        if state == 'absent' and instance:
            res_action = app_mgr.delete_instance(instance['uuid'])
            if res_action:
                if wait:
                    (completed, status) = cloudistics_wait_for_action(act_mgr,
                                                                      wait_timeout,
                                                                      res_action)
                instance = cloudistics_lookup_by_name(app_mgr, name)
                changed = True

        elif state == 'present' and not instance:
            # tags = a_module.params.get('tags')
            # if isinstance(tags, list):
            #     tags = ','.join(map(str, tags))

            res_action = app_mgr.create_instance(
                name=a_module.params.get('name'),
                description=a_module.params.get('description'),
                vcpus=a_module.params.get('vcpus'),
                memory=a_module.params.get('memory'),
                template_name=a_module.params.get('template_name'),
                category_name=a_module.params.get('category_name'),
                data_center_name=a_module.params.get('data_center_name'),
                migration_zone_name=a_module.params.get('migration_zone_name'),
                flash_pool_name=a_module.params.get('flash_pool_name'),
                network_names=a_module.params.get('network_names'),
                tag_names=a_module.params.get('tag_names'),
            )
            if res_action:
                if wait:
                    (completed, status) = cloudistics_wait_for_action(act_mgr,
                                                                      wait_timeout,
                                                                      res_action)
                instance = cloudistics_lookup_by_name(app_mgr, name)
                changed = True

        a_module.exit_json(changed=changed,
                           completed=completed,
                           instance=json.loads(json.dumps(instance, default=lambda o: o.__dict__)),
                           status=status)
    except exceptions.CloudisticsAPIError as e:
        a_module.fail_json(msg=e.message)

    # except TypeError as e:
    #     a_module.fail_json(msg=str(e))

    except ValueError as e:
        a_module.fail_json(msg=str(e))


if __name__ == '__main__':
    main()
