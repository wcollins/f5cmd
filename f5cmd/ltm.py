import json
import requests
from sys import argv
from sys import exit
from csv import reader
from os.path import isfile
from getpass import getpass

requests.packages.urllib3.disable_warnings()

class f5Conn(object):

    ''' Creates session to a given f5 Local Traffic Manager '''

    def __init__(self, hostname, partition):

        self.hostname = hostname
        self.partition = partition

    def authCheck(self):

        ''' Creates login file if it does not exist '''

        login = 'login.conf'
        login_exists = isfile(login)

        # If login file exists pass
        if login_exists == True:
            pass

        # Create login file if it doesn't exist
        elif login_exists == False:
            username = 'admin'
            password = getpass('Local Admin Password: ')
            login_data = '%s:%s' % (username, password)
            
            with open(login, 'w') as f:
                f.write(login_data)

    def f5Login(self):

        ''' Read credentials from login.conf and create connection '''

        hostname = self.hostname
        partition = self.partition

        self.authCheck()

        # Create session
        login = 'login.conf'

        with open(login, 'r') as f:
            for line in f.readlines():
                data = line.strip().split(':')
                username = data[0]
                password = data[1]

                conn = ltm_rest(hostname=hostname,
                                username=username,
                                password=password,
                                partition=partition)

                return conn

class ltm_rest(object):

    def __init__(self, hostname, username, password, partition):

        ''' Create resource for BIG-IP REST requests '''

        self.partition = partition
        self.bigip = requests.session()
        self.bigip.verify = False
        self.bigip.auth = (username, password)
        self.bigip_url = 'https://%s/mgmt/tm' % hostname
        self.bigip.headers.update({'Content-Type': 'application/json'})

    def post_virtual(self, name, address, port):

        '''  Create virtual server '''

        payload = {'name': name,
                   'partition': self.partition,
                   'kind': 'tm:ltm:virtual:virtualstate',
                   'destination': '%s:%s' % (address, port),
                   'ipProtocol': 'tcp',
                   'mask': '255.255.255.255'}

        resp = self.bigip.post('%s/ltm/virtual'
                               % self.bigip_url,
                               data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def post_pool(self, name):

        ''' Create pool '''

        payload = {'name': name,
                   'partition': self.partition,
                   'kind': 'tm:ltm:pool:poolstate'}

        resp = self.bigip.post('%s/ltm/pool'
                               % self.bigip_url,
                               data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def delete_virtual(self, server):

        ''' Delete virtual server '''

        resp = self.bigip.delete('%s/ltm/virtual/%s'
                                 % (self.bigip_url, server))

        return resp.status_code

    def delete_pool(self, pool):

        ''' Delete pool '''

        resp = self.bigip.delete('%s/ltm/pool/%s'
                                 % (self.bigip_url, pool))

        return resp.status_code

    def patch_description_virtual(self, server, description):

        ''' Add description to to a given virtual server '''

        payload = {'name': server,
                   'partition': self.partition,
                   'description': description,
                   'kind': 'tm:ltm:virtual:virtualstate'}

        resp = self.bigip.patch('%s/ltm/virtual/~%s~%s/'
                                % (self.bigip_url, self.partition, server),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def patch_description_pool(self, pool, description):

        ''' Add description to a given pool '''

        payload = {'name': pool,
                   'partition': self.partition,
                   'description': description,
                   'kind': 'tm:ltm:pool:poolstate'}

        resp = self.bigip.patch('%s/ltm/pool/~%s~%s/'
                                % (self.bigip_url, self.partition, pool),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def patch_pool(self, server, pool):

        ''' Add pool to a given virtual server '''

        payload = {'pool': pool,
                   'partition': self.partition,
                   'kind': 'tm:ltm:virtual:virtualstate'}

        resp = self.bigip.patch('%s/ltm/virtual/~%s~%s/'
                                % (self.bigip_url, self.partition, server),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def patch_profiles(self, server, profiles):

        ''' Add profiles to a given virtual server '''

        payload = {'name': server,
                   'partition': self.partition,
                   'kind': 'tm:ltm:virtual:virtualstate',
                   'profiles': profiles}

        resp = self.bigip.patch('%s/ltm/virtual/~%s~%s/'
                                % (self.bigip_url, self.partition, server),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def patch_persist(self, server, persistence):

        ''' Add persistence profile to a given virtual server '''

        payload = {'name': server,
                   'persist': persistence,
                   'partition': self.partition,
                   'kind': 'tm:ltm:virtual:virtualstate'}

        resp = self.bigip.patch('%s/ltm/virtual/~%s~%s/'
                                % (self.bigip_url, self.partition, server),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def patch_irule(self, server, irule):

        ''' Add irule to a given virtual server '''

        payload = {'name': server,
                   'partition': self.partition,
                   'rules': ['/Common/%s' % irule],
                   'kind': 'tm:ltm:virtual:virtualstate'}

        resp = self.bigip.patch('%s/ltm/virtual/~%s~%s/'
                                % (self.bigip_url, self.partition, server),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def patch_snat_profile(self, server, profile):

        ''' Add SNAT profile to a given virtual server '''

        payload = {'name': server,
                   'partition': self.partition,
                   'kind': 'tm:ltm:virtual:virtualstate',
                   'sourceAddressTranslation': {'type': profile}}

        resp = self.bigip.patch('%s/ltm/virtual/~%s~%s/'
                                % (self.bigip_url, self.partition, server),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def patch_members(self, pool, members):

        ''' Add members to a given pool '''

        payload = {'name': pool,
                   'members': members,
                   'partition': self.partition,
                   'kind': 'tm:ltm:pool:poolstate'}

        resp = self.bigip.patch('%s/ltm/pool/~%s~%s/'
                                % (self.bigip_url, self.partition, pool),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def patch_method(self, pool, method):

        ''' Add Load Balancing Method to a given pool '''

        payload = {'name': pool,
                   'loadBalancingMode': method,
                   'partition': self.partition,
                   'kind': 'tm:ltm:pool:poolstate'}

        resp = self.bigip.patch('%s/ltm/pool/~%s~%s/'
                                % (self.bigip_url, self.partition, pool),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def patch_monitor(self, pool, monitor):

        ''' Add Health Monitor to a given pool '''

        payload = {'name': pool,
                   'monitor': monitor,
                   'partition': self.partition,
                   'kind': 'tm:ltm:pool:poolstate'}

        resp = self.bigip.patch('%s/ltm/pool/~%s~%s/'
                                % (self.bigip_url, self.partition, pool),
                                data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

    def get_profiles(self, template):

        ''' List usable profiles on a given LTM '''

        resp = self.bigip.get('%s/ltm/profile/%s?$filter=partition eq %s'
                              % (self.bigip_url, template, self.partition))

        return json.loads(resp.text)

    def get_persist(self, template):

        ''' List usable persistence profiles on a given LTM '''

        resp = self.bigip.get('%s/ltm/persistence/%s?$filter=partition eq %s'
                              % (self.bigip_url, template, self.partition))

        return json.loads(resp.text)

    def get_irules(self):

        ''' List usable irules on a given LTM '''

        resp = self.bigip.get('%s/ltm/rule?$filter=partition eq %s'
                              % (self.bigip_url, self.partition))

        return json.loads(resp.text) 

    def get_monitors(self, template):

        ''' List usable health monitors on a given LTM '''

        resp = self.bigip.get('%s/ltm/monitor/%s?$filter=partition eq %s'
                              % (self.bigip_url, template, self.partition))

        return json.loads(resp.text)

    def get_device_group(self):

        ''' List device group a given LTM belongs to '''

        resp = self.bigip.get('%s/cm/device-group'
                              % self.bigip_url)

        return resp.status_code, json.loads(resp.text)

    def get_failover_status(self):

        ''' List failover status of a given LTM '''

        resp = self.bigip.get('%s/cm/failover-status'
                              % self.bigip_url)

        return resp.status_code, json.loads(resp.text)
		
    def sync_to_group(self, device_group):

        ''' Perform a ConfigSync from device to group '''

        payload = {'command': 'run',
                   'utilCmdArgs': 'config-sync to-group %s' % device_group}

        resp = self.bigip.post('%s/cm' % self.bigip_url, data=json.dumps(payload))

        return resp.status_code, json.loads(resp.text)

class ltm_create(object):

    ''' Create new objects on a given Local Traffic Manager '''

    def __init__(self, session):

        self.session = session

    def create_virtual(self, server, address, port):

        s = self.session

        status_code, json = s.post_virtual(server, address, port)

        if (status_code == 200):
            pass
        elif (status_code == 409):
            print 'DUPLICATE: Server %s already exists on the f5 - exiting' % server
        else:
            print status_code

    def create_pool(self, pool):

        s = self.session

        status_code, json = s.post_pool(pool)

        if (status_code == 200):
            pass
        elif (status_code == 409):
            print 'DUPLICATE: Pool %s already exists on the f5 - exiting' % pool
            exit()
        else:
            print status_code

class ltm_delete(object):

    ''' Delete objects from a given Local Traffic Manager '''

    def __init__(self, session):

        self.session = session

    def delete_virtual(self, server):

        s = self.session

        status_code = s.delete_virtual(server)

        if (status_code == 200):
            pass
        else:
            print status_code

    def delete_pool(self, pool):

        s = self.session

        status_code = s.delete_pool(pool)

        if (status_code == 200):
            pass
        else:
            print status_code

class ltm_modify(object):

    ''' Modify existing objects on a given Local Traffic Manager '''

    def __init__(self, session):

        self.session = session

    def add_pool(self, server, pool):

        s = self.session

        status_code, json = s.patch_pool(server, pool)

        if (status_code == 200):
            pass
        else:
            print status_code

    def add_description_virtual(self, server, desc):

        s = self.session

        status_code, json = s.patch_description_virtual(server, desc)

        if (status_code == 200):
            pass
        else:
            print status_code

    def add_description_pool(self, pool, desc):

        s = self.session

        status_code, json = s.patch_description_pool(pool, desc)

        if (status_code == 200):
            pass
        else:
            print status_code

    def add_profiles(self, server, profile_list):

        s = self.session

        status_code, json = s.patch_profiles(server, profile_list.split(','))

        if (status_code == 200):
            pass
        else:
            print status_code

    def add_persist(self, server, profile):

        s = self.session

        status_code, json = s.patch_persist(server, profile)

        if (status_code == 200):
            pass
        else:
            print status_code

    def add_irule(self, server, irule):

        s = self.session

        status_code, json = s.patch_irule(server, irule)

        if (status_code == 200):
            pass
        else:
            print status_code

    def add_snat_profile(self, server, profile):

        s = self.session

        status_code, json = s.patch_snat_profile(server, profile)

        if (status_code == 200):
            pass
        else:
            print status_code

    def add_members(self, pool, member_list):

        s = self.session

        status_code, json = s.patch_members(pool, member_list.split(','))

        if (status_code == 200):
            pass
        else:
            print status_code

    def add_method(self, pool, method):

        s = self.session

        status_code, json = s.patch_method(pool, method)

        if (status_code == 200):
            pass
        else:
            print status_code

    def add_monitor(self, pool, monitor):

        s = self.session

        status_code, json = s.patch_monitor(pool, monitor)

        if (status_code == 200):
            pass
        else:
            print status_code

class ltm_list(object):

    ''' List data from a given Local Traffic Manager '''

    def __init__(self, session):

        self.session = session

    def list_profiles(self):

        s = self.session

        templates = ['tcp', 'http', 'client-ssl', 'server-ssl', 'one-connect']

        for template in templates:
            profile_data = s.get_profiles(template)
            for profile in profile_data['items']:
                print profile['name']

    def list_persist(self):

        s = self.session

        templates = ['cookie', 'source-addr']

        for template in templates:
            persist_data = s.get_persist(template)
            for profile in persist_data['items']:
                print profile['name']

    def list_irules(self):

        s = self.session

        rule_data = s.get_irules()

        for rule in rule_data['items']:
            print rule['name']

    def list_monitors(self):

        s = self.session

        templates = ['http', 'https', 'external', 'tcp', 'tcp-half-open',
                     'tcp-echo']

        for template in templates:
            monitor_data = s.get_monitors(template)
            for monitor in monitor_data['items']:
                print monitor['name']

    def list_methods(self):

        s = self.session

        methods = ['round-robin', 'ratio-member', 'least-connections-member', 'observed-member',
                   'predictive-member', 'ratio-node', 'least-connections-node', 'fastest-node',
                   'observed-node', 'predictive-node', 'dynamic-ratio-node', 'fastest-app-response',
                   'least-sessions', 'dynamic-ratio-member', 'weighted-least-connections-member',
                   'weighted-least-connections-node', 'ratio-sessions', 'ratio-least-connections-member',
                   'ratio-least-connections-node']

        for method in methods:
            print method

    def list_device_group(self):

        s = self.session

        status_code, response = s.get_device_group()

        if (status_code == 200):
            device_group = response['items'][0]['name']

            return device_group

    def list_failover_status(self):

        s = self.session

        status_code, response = s.get_failover_status()
        keys = []

        if (status_code == 200):
            for device in response['entries'].values():
                failover_state = device['nestedStats']['entries']['status']['description']

                return failover_state

class ltm_run(object):

    ''' Run custom commands on a given Local Traffic Manager '''

    def __init__(self, session):

        self.session = session

    def run_config_sync(self):

        s = self.session
        l = ltm_list(s)

        # Get device group
        device_group = l.list_device_group()

        # Sync from device to group
        status_code, response = s.sync_to_group(device_group)
        if (status_code == 200):
            pass
        else:
            print 'Error: %s. %s' % (status_code, response['message'])

class ltm_interact(object):

    ''' Perform tasks on a Local Traffic Manager interactively '''

    def __init__(self, hostname):

        self.hostname = hostname

    def create_virtual_interact(self):

        hostname = self.hostname

        # Set hostname and partition
        session = f5Conn(hostname, 'Common')

        # Login to LTM
        s = session.f5Login()

        # Define session type
        _create = ltm_create(s)
        _delete = ltm_delete(s)
        _list = ltm_list(s)
        _modify = ltm_modify(s)
        _run = ltm_run(s)

        # Get failover status
        failover_status = _list.list_failover_status()

        # Validate LTM is 'ACTIVE' before continuing
        if failover_status == 'ACTIVE':
            pass
        elif failover_status == 'STANDBY':
            print 'You are logged into the STANDBY LTM - exiting'

        # Get name, address, port, desc
        server = raw_input('Name: ')
        address = raw_input('Destination Address: ')
        port = raw_input('Service Port: ')
        desc = raw_input('Description: ')

        # Create base virtual server
        try:
            _create.create_virtual(server, address, port)
        except Exception, e:
            print e

        # Add description
        try:
            if desc == '':
                pass
            else:
                _modify.add_description_virtual(server, desc)
        except Exception, e:
            print e

        # Add profiles
        try:
            _list.list_profiles()
            profiles = raw_input('Profiles - e.g. tcp,http,clientssl: ')

            if profiles == '':
                pass
            else:
                _modify.add_profiles(server, profiles)
        except Exception, e:
            print e

        # Add persistence
        try:
            _list.list_persist()
            persist = raw_input('Default Persistence Profile: ')

            if persist == '':
                pass
            else:
                _modify.add_persist(server, persist)
        except Exception, e:
            print e

        # Add iRule
        try:
            _list.list_irules()
            irule = raw_input('iRule: ')

            if irule == '':
                pass
            else:
                _modify.add_irule(server, irule)
        except Exception, e:
            print e

        # Add SNAT profile
        try:
            snat = raw_input('SNAT profile: ')

            if snat == '':
                pass
            else:
                _modify.add_snat_profile(server, snat)
        except Exception, e:
            print e

        # Option to create pool
        pool_option = raw_input('Add pool behind virtual server? - yes/no: ')

        if pool_option == 'yes':

            pool = raw_input('Name: ')

            # Create base pool, add description, & nest with virtual server
            try:
                _create.create_pool(pool)
                _modify.add_pool(server, pool)
                _modify.add_description_pool(pool, desc)
            except Exception, e:
                print e

            # Add pool members
            try:
                members = raw_input('Members - e.g. 10.0.1.1:80,10.0.1.2:80: ')

                if members == '':
                    pass
                else:
                    _modify.add_members(pool, members)
            except Exception, e:
                print e

            # Add Load Balancing Method
            try:
                _list.list_methods()
                method = raw_input('Load Balancing Method: ')

                if method == '':
                    pass
                else:
                    _modify.add_method(pool, method)
            except Exception, e:
                print e

            # Add Health Monitor
            try:
                _list.list_monitors()
                monitor = raw_input('Health Monitor: ')

                if monitor == '':
                    pass
                else:
                    _modify.add_monitor(pool, monitor)
            except Exception, e:
                print e

        # Option to sync config
        sync_option = raw_input('Sync Device to Group - yes/no: ')

        if sync_option == 'yes':

            # Sync device to group
            try:
                _run.run_config_sync()
            except Exception, e:
                print e

        elif sync_option == 'no':
            exit()
        else:
            print 'You did not select yes/no - exiting'
            exit()

class ltm_bulk(object):

    def __init__(self, csv_data):

        self.csv_data = csv_data

    def create_virtual_bulk(self):

        d = self.csv_data

        # Loop through data
        with open(d, 'r') as in_data:
            data = reader(in_data)
            next(data, None)
            for row in data:
                d = row
                hostname, server, address, port = d[0:4]
                profiles, persist, snat_profile, irule = d[4:8]
                pool, members, method, monitor = d[8:12]
                desc, sync = d[12:14]

                # Set hostname and partition
                session = f5Conn(hostname, 'Common')

                # Login to LTM
                s = session.f5Login()

                # Get failover status
                status_code, response = s.get_failover_status()

                if (status_code == 200):
                    for device in response['entries'].values():
                        failover_status = device['nestedStats']['entries']['status']['description']

                        # Validate LTM is 'ACTIVE' before continuing
                        if failover_status == 'ACTIVE':
                            pass
                        elif failover_status == 'STANDBY':
                            print 'You are logged into the STANDBY LTM - exiting'
                            exit()

                # Create base virtual server
                try:
                    if server != '':
                        status_code, json = s.post_virtual(server, address, port)

                        # Only continue if successful
                        if (status_code == 200):

                            # Add description
                            if desc != '':
                                status_code, json = s.patch_description_virtual(server, desc)

                                if (status_code == 200):
                                    pass
                                else:
                                    print status_code

                            # Add profiles
                            if profiles != '':
                                status_code, json = s.patch_profiles(server, profiles.split(','))

                                if (status_code == 200):
                                    pass
                                else:
                                    print status_code

                            # Add persistence
                            if persist != '':
                                status_code, json = s.patch_persist(server, persist)

                                if (status_code == 200):
                                    pass
                                else:
                                    print status_code

                            # Add irule
                            if irule != '':
                                status_code, json = s.patch_irule(server, irule)

                                if (status_code == 200):
                                    pass
                                else:
                                    print status_code

                        else:
                            print status_code
                except Exception, e:
                    print e

                # Create base pool
                try:
                    if pool != '':
                        status_code, json = s.post_pool(pool)

                        # Only continue if successful
                        if (status_code == 200):

                            # Nest pool with virtual server
                            s.patch_pool(server, pool)

                            # Add description
                            if desc != '':
                                status_code, json = s.patch_description_virtual(pool, desc)

                                if (status_code == 200):
                                    pass
                                else:
                                    print status_code

                            # Add members
                            if members != '':
                                status_code, json = s.patch_members(pool, members.split(','))

                                if (status_code == 200):
                                    pass
                                else:
                                    print status_code

                            # Add method
                            if method != '':
                                status_code, json = s.patch_method(pool, method)

                                if (status_code == 200):
                                    pass
                                else:
                                    print status_code

                            # Add monitor
                            if monitor != '':
                                status_code, json = s.patch_monitor(pool, monitor)

                                if (status_code == 200):
                                    pass
                                else:
                                    print status_code

                        else:
                            print status_code

                except Exception, e:
                    print e

    def delete_virtual_bulk(self):

        d = self.csv_data

        # Loop through data
        with open(d, 'r') as in_data:
            data = reader(in_data)
            next(data, None)
            for row in data:
                d = row
                hostname = d[0]
                server = d[1]
                pool = d[8]

                # Set hostname and partition
                session = f5Conn(hostname, 'Common')

                # Login to LTM
                s = session.f5Login()

                # Define session type
                _delete = ltm_delete(s)
                _run = ltm_run(s)

                # Delete virtual server
                if server != '':
                    _delete.delete_virtual(server)
                else:
                    pass

                # Delete pool
                if pool != '':
                    _delete.delete_pool(pool)
                else:
                    pass

                # Sync config
                if sync != '':
                    _run.run_config_sync()
                else:
                    pass
