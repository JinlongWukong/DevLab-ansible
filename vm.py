from ansible_task_executor import AnsibleTaskExecutor
import os

class VM(object):

    def __init__(self, host_ip, host_user, host_pass, name, port=22, hostname="", vcpus=1, memory=2048, disk=20,
                 os_type="centos7", vnc_pass="12345678", root_pass="12345678", addons=[]):
        self.host_ip = host_ip
        self.host_user = host_user
        self.host_pass = host_pass
        self.port = port
        self.name = name
        self.hostname = hostname
        self.vcpus = vcpus
        self.memory = memory
        self.disk = disk
        self.os_type = os_type
        self.root_pass = root_pass
        self.vnc_pass = vnc_pass
        self.vnc_port = None
        self.address = None
        self.status = None
        self.addons = addons
        self.proxy = os.getenv('https_proxy')
        self.ansible_inventory = "{} ansible_ssh_user={} ansible_ssh_pass={} ansible_port={}".format(host_ip, host_user,
                                                                                                  host_pass, port)
        self.executor = AnsibleTaskExecutor()

    def get_info(self):
        """
            Get VM latest information
        :return:
            vm name, address, status, vnc_port
        """
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['address', 'status', 'vnc'])
        if result_code:
            raise Exception(callback.get_failed_result())

        for event in callback.host_ok:
            if event['task'] == "Check vm existence" and event['host'] == self.host_ip:
                if not event['result']['stdout']: raise Exception("VM {} not exist".format(self.name))
            elif event['task'] == "Get vm IP address" and event['host'] == self.host_ip:
                self.address = event['result']['stdout']
            elif event['task'] == "Get vm status" and event['host'] == self.host_ip:
                self.status = event['result']['stdout']
            elif event['task'] == "Get vnc port" and event['host'] == self.host_ip:
                self.vnc_port = event['result']['stdout']
            else:
                pass

        return self.name, self.status, self.address, self.vnc_port

    def create(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name, "hostname": self.hostname,
                                                                  "vcpus": self.vcpus, "memory": self.memory,
                                                                  "disk": self.disk, "vnc_pass": self.vnc_pass,
                                                                  "os_type": self.os_type, "root_pass": self.root_pass},
                                                      tags=['create'])
        if result_code:
            raise Exception(callback.get_failed_result())

    def start(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['start'])
        if result_code:
            raise Exception(callback.get_failed_result())

    def shutdown(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['shutdown'])
        if result_code:
            raise Exception(callback.get_failed_result())

    def reboot(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['reboot'])
        if result_code:
            raise Exception(callback.get_failed_result())

    def delete(self):
        result_code, callback = self.executor.execute('libvirt-vm.yml', self.ansible_inventory,
                                                      extra_vars={"guest_name": self.name},
                                                      tags=['delete'])
        if result_code:
            raise Exception(callback.get_failed_result())

    def install_addons(self):
        result_code, callback = self.executor.execute('addons.yml', self.ansible_inventory,
                                                      extra_vars={"addons": self.addons,
                                                                  "https_proxy": self.proxy,
                                                                  "proxy_env": {'https_proxy': self.proxy}})
        if result_code:
            raise Exception(callback.get_failed_result())