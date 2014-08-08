import random
import time

import clients


def status_timeout(things, thing_id, expected_status):
    """
    Given a thing and an expected status, do a loop, sleeping
    for a configurable amount of time, checking for the
    expected status to show. At any time, if the returned
    status of the thing is ERROR, fail out.
    """
    def check_status():
        # python-novaclient has resources available to its client
        # that all implement a get() method taking an identifier
        # for the singular resource to retrieve.
        thing = things.get(thing_id)
        new_status = thing.status.lower()
        if new_status == 'error':
            raise Exception("Failed to get to expected status. "
                            "In error state.")
        elif new_status == expected_status.lower():
            return True  # All good.
    if not call_until_true(check_status, 200, 5):
        raise Exception("Timed out waiting to become %s" % expected_status)


def call_until_true(func, duration, sleep_for, arg=None):
    """
    Call the given function until it returns True (and return True) or
    until the specified duration (in seconds) elapses (and return
    False).

    :param func: A zero argument callable that returns True on success.
    :param duration: The number of seconds for which to attempt a
        successful call of the function.
    :param sleep_for: The number of seconds to sleep after an unsuccessful
                      invocation of the function.
    """
    now = time.time()
    timeout = now + duration
    while now < timeout:
        if arg:
            if func(arg):
                return True
        elif func():
            return True
        time.sleep(sleep_for)
        now = time.time()
    return False


def rand_name(name='ost1_test-'):
    return name + str(random.randint(1, 0x7fffffff))


class Methods(clients.Clients):

    def __init__(self):
        super(Methods, self).__init__()
        self.compute_client = self._get_compute_client()
        self.volume_client = self._get_volume_client()
        self.identity_client = self._get_identity_client()

    def _create_security_group(
            self, client, namestart='ost1_test-secgroup-smoke-netw'):
        # Create security group
        sg_name = rand_name(namestart)
        sg_desc = sg_name + " description"
        secgroup = client.security_groups.create(sg_name, sg_desc)

        # Add rules to the security group

        # These rules are intended to permit inbound ssh and icmp
        # traffic from all sources, so no group_id is provided.
        # Setting a group_id would only permit traffic from ports
        # belonging to the same security group.
        rulesets = [
            {
                # ssh
                'ip_protocol': 'tcp',
                'from_port': 22,
                'to_port': 22,
                'cidr': '0.0.0.0/0',
            },
            {
                # ping
                'ip_protocol': 'icmp',
                'from_port': -1,
                'to_port': -1,
                'cidr': '0.0.0.0/0',
            }
        ]
        for ruleset in rulesets:
                client.security_group_rules.create(secgroup.id, **ruleset)

        return secgroup

    def _create_volume(self, expected_state=None, **kwargs):
        kwargs.setdefault('display_name', rand_name('ostf-test-volume'))
        kwargs.setdefault('size', 1)
        volume = self.volume_client.volumes.create(**kwargs)
        if expected_state:
            def await_state():
                if self.volume_client.volumes.get(
                        volume.id).status == expected_state:
                    return True
            call_until_true(await_state, 50, 1)

        return volume

    def _create_server(self, name, security_groups=None,
                       flavor_id=None):
        base_image_id = self.config.other.image_id
        if not flavor_id:
            flavor_id = self.config.other.flavor_id
        if not security_groups:
            security_groups = [self._create_security_group(
                self.compute_client).name]
        if self.config.other.net_provider == 'neutron':
            network = [net.id for net in
                       self.compute_client.networks.list()
                       if net.label == self.config.other.private_net]

            if network:
                create_kwargs = {'nics': [{'net-id': network[0]}],
                                 'security_groups': security_groups}
            else:
                raise Exception('Private network was not created by default')
        else:
            create_kwargs = {'security_groups': security_groups}

        server = self.compute_client.servers.create(name, base_image_id,
                                                    flavor_id, **create_kwargs)
        status_timeout(self.compute_client.servers, server.id, 'ACTIVE')
        # The instance retrieved on creation is missing network
        # details, necessitating retrieval after it becomes active to
        # ensure correct details.
        server = self.compute_client.servers.get(server.id)
        return server
