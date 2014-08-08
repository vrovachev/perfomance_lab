import os
from oslo.config import cfg


def register_opt_group(conf, opt_group, options):
    conf.register_group(opt_group)
    for opt in options:
        conf.register_opt(opt, group=opt_group.name)

compute_group = cfg.OptGroup(name='compute',
                             title='Compute Service Options')

ComputeGroup = [
    cfg.StrOpt('catalog_type',
               default='compute',
               help="Catalog type of the Compute service."),
]


identity_group = cfg.OptGroup(name='identity',
                              title="Keystone Configuration Options")

IdentityGroup = [
    cfg.StrOpt('catalog_type',
               default='identity',
               help="Catalog type of the Identity service."),
    cfg.BoolOpt('disable_ssl_certificate_validation',
                default=False,
                help="Set to True if using self-signed SSL certificates."),
    cfg.StrOpt('uri',
               default='http://localhost:5000/v2.0/',
               help="Full URI of the OpenStack Identity API (Keystone), v2"),
    cfg.StrOpt('url',
               default='http://localhost:5000/v2.0/',
               help="Dashboard Openstack url, v2"),
    cfg.StrOpt('ubuntu_url',
               default='http://localhost:5000/v2.0/',
               help="Dashboard Openstack url, v2"),
    cfg.StrOpt('uri_v3',
               help='Full URI of the OpenStack Identity API (Keystone), v3'),
    cfg.StrOpt('strategy',
               default='keystone',
               help="Which auth method does the environment use? "
                    "(basic|keystone)"),
    cfg.StrOpt('region',
               default='RegionOne',
               help="The identity region name to use."),
    cfg.StrOpt('admin_username',
               default='admin',
               help="Administrative Username to use for"
                    "Keystone API requests."),
    cfg.StrOpt('admin_tenant_name',
               default='admin',
               help="Administrative Tenant name to use for Keystone API "
                    "requests."),
    cfg.StrOpt('admin_password',
               default='admin',
               help="API key to use when authenticating as admin.",
               secret=True),
]

other_group = cfg.OptGroup(name='other',
                           title="Other Configuration Options")

OtherGroup = [
    cfg.StrOpt('image_id',
               default=''),
    cfg.StrOpt('flavor_id',
               default=''),
    cfg.StrOpt('net_provider',
               default='neutron'),
    cfg.StrOpt('private_net',
               default='net04')
]


def register_opts():
    register_opt_group(cfg.CONF, compute_group, ComputeGroup)
    register_opt_group(cfg.CONF, identity_group, IdentityGroup)
    register_opt_group(cfg.CONF, other_group, OtherGroup)


class Config(object):
    """Provides OpenStack configuration information."""

    def _set_attrs(self):
        self.compute = cfg.CONF.compute
        self.identity = cfg.CONF.identity
        self.other = cfg.CONF.other

    def __init__(self):
        config_file='{path}/{name}'.format(path=os.getcwd(),
                                           name="config.conf")
        if not os.path.isfile(config_file):
            config_files = []
        else:
            config_files = [config_file]
        cfg.CONF([], project='perfomance', default_config_files=config_files)
        register_opts()
        self._set_attrs()

CONF = Config()