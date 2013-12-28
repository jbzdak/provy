#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
This is the internal module responsible for running provy over the provyfile that was provided.

It's recommended not to tinker with this module, as it might prevent your provyfile from working.
'''
from copy import copy

from os.path import abspath, dirname, join

from fabric.context_managers import settings as _settings

from provy.core.utils import import_module, AskFor, provyfile_module_from
from provy.core.errors import ConfigurationError
from jinja2 import FileSystemLoader, ChoiceLoader

from .server import ProvyServer


def run(provfile_path, server_group_name, password, extra_options):
    module_name = provyfile_module_from(provfile_path)
    prov = import_module(module_name)
    servers = get_servers_for(prov, server_group_name)

    build_prompt_options(servers, extra_options)

    for server in servers:
        provision_server(server, provfile_path, prov)


def print_header(msg):
    print
    print "*" * len(msg)
    print msg
    print "*" * len(msg)


def provision_server(server, provfile_path, prov):
    context = {
        'abspath': dirname(abspath(provfile_path)),
        'path': dirname(provfile_path),
        'owner': server.username,
        'cleanup': [],
        'registered_loaders': [],
        '__provy': {
            'current_server': server
        }
    }

    aggregate_node_options(server, context)

    loader = ChoiceLoader([
        FileSystemLoader(join(context['abspath'], 'files'))
    ])
    context['loader'] = loader

    print_header("Provisioning %s..." % server.host_string)

    settings_dict = dict(host_string=server.host_string, password=server.password)
    if server.ssh_key is not None:
        settings_dict['key_filename'] = server.ssh_key

    with _settings(**settings_dict):
        context['host'] = server.address
        context['user'] = server.username
        role_instances = []

        try:
            for role in server.roles:
                context['role'] = role
                instance = role(prov, context)
                role_instances.append(instance)
                instance.provision()
        finally:
            for role in role_instances:
                role.cleanup()

            for role in context['cleanup']:
                role.cleanup()

    print_header("%s provisioned!" % server.host_string)


def aggregate_node_options(server, context):
    for key, value in server.options.iteritems():
        context[key] = value


def build_prompt_options(servers, extra_options):
    for server in servers:
        for option_name, option in server.options.iteritems():
            if isinstance(option, AskFor):
                if option.key in extra_options:
                    value = extra_options[option.key]
                else:
                    value = option.get_value(server)
                server.options[option_name] = value

def get_all_servers(prov):
    if not hasattr(prov, 'servers'):
        raise ConfigurationError('The servers collection was not found in the provyfile file.')

    servers = getattr(prov, 'servers')

    result = {}

    for group_name, group in servers.items():
        group_dict = {}
        result[group_name] = group_dict
        for server_name, server_dict in group.items():
            group_dict[server_name] = ProvyServer.from_dict(server_name, group_name, server_dict)
    return result


def get_servers_for(prov, server_group_name):
    server_group_name = server_group_name.strip()
    all_servers = get_all_servers(prov)
    result = []
    if server_group_name == '':
         for group in all_servers.values():
             for server in group.values():
                 result.append(server)
    elif not '.' in server_group_name:
         group = all_servers[server_group_name]
         for server in group.values():
             result.append(server)
    else:
        group, server = server_group_name.split('.')
        result.append([all_servers[group][server]])
    return result
