from ansible_task_executor import AnsibleTaskExecutor


class VM(object):

    def __init__(self, host_ip, host_user, host_pass, name, vcpus=1, memory=2048, disk=20, os_type="centos7",
                 vnc_pass="12345678"):
        self.host_ip = host_ip
        self.host_user = host_user
        self.host_pass = host_pass
        self.name = name
        self.vcpus = vcpus
        self.memory = memory
        self.disk = disk
        self.os_type = os_type
        self.vnc_pass = vnc_pass
        self.address = None
        self.status = None
        self.ansible_inventory = "{} ansible_ssh_user={} ansible_ssh_pass={}".format(host_ip, host_user, host_pass)
        self.executor = AnsibleTaskExecutor()

    def get_info(self):
        """
            Get VM latest information
        :return:
            vm name, address, status
        """
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['address', 'status'])
        if result_code:
            raise Exception(callback.get_all_result())

        for event in callback.host_ok:
            if event['task'] == "Check vm existence" and event['host'] == self.host_ip:
                if not event['result']['stdout']: raise Exception("VM {} not exist".format(self.name))
            elif event['task'] == "Get vm IP address" and event['host'] == self.host_ip:
                self.address = event['result']['stdout']
            elif event['task'] == "Get vm status" and event['host'] == self.host_ip:
                self.status = event['result']['stdout']
            else:
                pass

        return self.name, self.status, self.address

    def create(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name, "vcpus": self.vcpus,
                                                                  "memory": self.memory, "disk": self.disk,
                                                                  "os_type": self.os_type, "vnc_pass": self.vnc_pass},
                                                      tags=['create'])
        if result_code:
            raise Exception(callback.get_all_result())

    def start(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['start'])
        if result_code:
            raise Exception(callback.get_all_result())

    def shutdown(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['shutdown'])
        if result_code:
            raise Exception(callback.get_all_result())

    def reboot(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['reboot'])
        if result_code:
            raise Exception(callback.get_all_result())

    def delete(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['delete'])
        if result_code:
            raise Exception(callback.get_all_result())
