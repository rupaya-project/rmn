import logging
import sys

from clint import resources
from slugify import slugify
import docker

from rupayamn import display
from rupayamn.elements.network import Network
from rupayamn.elements.service import Service
from rupayamn.elements.volume import Volume
from rupayamn.environments import environments

logger = logging.getLogger('rupayamn')
resources.init('rupaya', 'rupayamn')


class Configuration:
    """docstring for Configuration."""

    def __init__(self, name: str = None, net: str = None,
                 pkey: str = None, start: bool = False,
                 docker_url: str = None, api: bool = False) -> None:
        self.networks = {}
        self.services = {}
        self.volumes = {}
        self.name = name
        self.net = net
        self.pkey = pkey or ''
        self.force_recreate = False
        if not docker_url:
            self.client = docker.from_env()
        else:
            self.client = docker.DockerClient(base_url=docker_url)
        self.api = 'True' if api else 'False'
        try:
            self.client.ping()
        except Exception as e:
            logger.error(e)
            display.error_docker()
            sys.exit('\n')
        if resources.user.read('name'):
            self._load()
        elif start:
            self._write()
        else:
            display.error_start_not_initialized()
            sys.exit('\n')
        self._compose()

    def _load(self) -> None:
        if self.name or self.net or self.pkey:
            display.warning_ignoring_start_options(resources.user.read('name'))
        self.name = resources.user.read('name')
        self.net = resources.user.read('net')
        self.api = resources.user.read('api')

    def _write(self) -> None:
        if not self.name:
            display.error_start_option_required('--name')
            sys.exit('\n')
        elif not self.net:
            display.error_start_option_required('--net')
            sys.exit('\n')
        elif not self.pkey:
            display.error_start_option_required('--pkey')
            sys.exit('\n')
        self._validate()
        resources.user.write('name', self.name)
        resources.user.write('net', self.net)
        resources.user.write('api', self.api)

    def _compose(self) -> None:
        self.networks['rupayamn'] = Network(
            name='{}_rupayamn'.format(self.name),
            client=self.client
        )
        self.volumes['chaindata'] = Volume(
            name='{}_chaindata'.format(self.name),
            client=self.client
        )
        if self.net == 'mainnet':
            tag = 'stable'
        elif self.net == 'testnet':
            tag = 'testnet'
        else:
            tag = 'mainnet'
        if self.api == 'True':  # this is dirty, should be refactored
            rupaya_ports = {'10707/udp': 10707, '10707/tcp': 10707,
                            '7050/tcp': 7050, '8050/tcp': 8050}
        else:
            rupaya_ports = {'10707/udp': 10707, '10707/tcp': 10707}
        self.services['rupaya'] = Service(
            name='{}_rupaya'.format(self.name),
            image='rupaya/node:{}'.format('latest'),
            network=self.networks['rupayamn'].name,
            environment={
                'IDENTITY': '{}'.format(self.name),
                'PRIVATE_KEY': '{}'.format(self.pkey)
            },
            volumes={
                self.volumes['chaindata'].name: {
                    'bind': '/rupaya', 'mode': 'rw'
                }
            },
            ports=rupaya_ports,
            client=self.client
        )
        for container, variables in environments[self.net].items():
            for variable, value in variables.items():
                self.services[container].add_environment(
                    name=variable,
                    value=value
                )

    def _validate(self) -> None:
        self.name = slugify(self.name)
        if len(self.name) < 5 or len(self.name) > 30:
            display.error_validation_option('--name', '5 to 30 characters '
                                            'slug')
            sys.exit('\n')
        if len(self.pkey) != 64:
            display.error_validation_option('--pkey', '64 characters hex '
                                            'string')
            sys.exit('\n')
        try:
            bytes.fromhex(self.pkey)
        except ValueError:
            display.error_validation_option('--pkey', '64 characters hex '
                                            'string')
            sys.exit('\n')

    def remove(self) -> None:
        resources.user.delete('name')
        resources.user.delete('net')
