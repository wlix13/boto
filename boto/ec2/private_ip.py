# Copyright (c) 2017 CROC Incorporated, http://cloud.croc.ru/en/
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.


from boto.ec2.address import Address
from boto.ec2.ec2object import EC2Object


class PrivateIP(EC2Object):
    """
    Represents an EC2 Private IP Address.
    """

    def __init__(self, connection=None):
        super(PrivateIP, self).__init__(connection)
        self.id = None
        self.subnet_id = None
        self.state = None
        self.availability_zone = None
        self.private_ip_address = None
        self.ip_address = None
        self.public_dns_name = None

    def __repr__(self):
        return 'Address:%s' % self.id

    def endElement(self, name, value, connection):
        if name == 'privateIpAddressId':
            self.id = value
        elif name == 'subnetId':
            self.subnet_id = value
        elif name == 'state':
            self.state = value
        elif name == 'availabilityZone':
            self.availability_zone = value
        elif name == 'privateIpAddress':
            self.private_ip_address = value
        elif name == 'ipAddress':
            self.ip_address = value
        elif name == 'dnsName':
            self.public_dns_name = value
        else:
            setattr(self, name, value)

    def use_ip(self, ip_address):
        if isinstance(ip_address, Address):
            ip_address = ip_address.public_ip
        return self.connection.associate_address(private_ip_address_id=self.id, public_ip=ip_address)

    def delete(self):
        return self.connection.delete_private_ip_address(self.id)
