'''Croc Cloud EC2 Address Pool.'''


from boto.ec2.ec2object import EC2Object


class AddressPool(EC2Object):

    def __init__(self, connection=None, id=None):
        super(AddressPool, self).__init__(connection)
        self.connection = connection
        self.id = id
        self.description = None
        self.total_address_count = None
        self.total_available_address_count = None
        self.pool_address_ranges = AddressRangeList()

    def __repr__(self):
        return 'AddressPool:{0}'.format(self.id)

    def startElement(self, name, attrs, connection):
        retval = super(AddressPool, self).startElement(name, attrs, connection)
        if retval is not None:
            return retval
        if name == 'poolAddressRangeSet':
            return self.pool_address_ranges
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'poolId':
            self.id = value
        elif name == 'description':
            self.description = value
        elif name == 'totalAvailableAddressCount':
            self.total_available_address_count = int(value)
        elif name == 'totalAddressCount':
            self.total_address_count = int(value)
        elif name == 'item':
            pass
        else:
            setattr(self, name, value)


class AddressRangeList(list):

    def startElement(self, name, attrs, connection):
        if name == 'item':
            self.append(AddressRange(self))
            return self[-1]
        return None

    def endElement(self, name, value, connection):
        pass


class AddressRange(object):

    def __init__(self, parent=None):
        self.parent = parent
        self.address_count = None
        self.last_address = None
        self.available_address_count = None
        self.first_address = None

    def __repr__(self):
        return 'AddressRange:{0}-{1}'.format(self.first_address, self.last_address)

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'addressCount':
            self.address_count = int(value)
        elif name == 'lastAddress':
            self.last_address = value
        elif name == 'availableAddressCount':
            self.available_address_count = int(value)
        elif name == 'firstAddress':
            self.first_address = value
        elif name == 'item':
            pass
        else:
            setattr(self, name, value)


class ByoipCidr(EC2Object):

    def __init__(self, connection=None, id=None):
        super(ByoipCidr, self).__init__(connection)
        self.connection = connection
        self.id = id
        self.cidr = None
        self.description = None
        self.status_message = None
        self.state = None

    def __repr__(self):
        return 'ByoipCidr:{0}'.format(self.cidr)

    def startElement(self, name, attrs, connection):
        return super(ByoipCidr, self).startElement(name, attrs, connection)

    def endElement(self, name, value, connection):
        if name == 'cidr':
            self.id = value
            self.cidr = value
        elif name == 'description':
            self.description = value
        elif name == 'statusMessage':
            self.status_message = value
        elif name == 'state':
            self.state = value
        elif name == 'item':
            pass
        else:
            setattr(self, name, value)
