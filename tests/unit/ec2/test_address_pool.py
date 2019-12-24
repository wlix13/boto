#!/usr/bin/env python


from tests.compat import unittest
from tests.unit import AWSMockServiceTestCase

from boto.ec2.address_pool import AddressPool, ByoipCidr
from boto.ec2.connection import EC2Connection


DESCRIBE_PUBLIC_IPV4_POOLS = br"""<DescribePublicIpv4PoolsResponse>
  <publicIpv4PoolSet>
    <item>
      <poolAddressRangeSet>
        <item>
          <addressCount>256</addressCount>
          <lastAddress>7.0.0.255</lastAddress>
          <availableAddressCount>247</availableAddressCount>
          <firstAddress>7.0.0.0</firstAddress>
        </item>
        <item>
          <addressCount>256</addressCount>
          <lastAddress>9.16.0.255</lastAddress>
          <availableAddressCount>256</availableAddressCount>
          <firstAddress>9.16.0.0</firstAddress>
        </item>
        <item>
          <addressCount>256</addressCount>
          <lastAddress>9.17.0.255</lastAddress>
          <availableAddressCount>256</availableAddressCount>
          <firstAddress>9.17.0.0</firstAddress>
        </item>
      </poolAddressRangeSet>
      <totalAvailableAddressCount>759</totalAvailableAddressCount>
      <totalAddressCount>768</totalAddressCount>
      <description/>
      <poolId>ipv4pool-ec2-4E58D35D</poolId>
    </item>
  </publicIpv4PoolSet>
  <requestId>b04344fb-e4c0-4b1b-b69c-4dbc1979f413</requestId>
  <ResponseMetadata>
    <RequestId>b04344fb-e4c0-4b1b-b69c-4dbc1979f413</RequestId>
  </ResponseMetadata>
</DescribePublicIpv4PoolsResponse>"""

DESCRIBE_BYOIP_CIDRS = br"""<DescribeByoipCidrsResponse>
  <byoipCidrSet>
    <item>
      <cidr>7.0.0.0/24</cidr>
      <description>7.0.0.0/24 PI block belonging to some user</description>
      <statusMessage/>
      <state>advertised</state>
    </item>
    <item>
      <cidr>9.16.0.0/24</cidr>
      <description>blabla</description>
      <statusMessage/>
      <state>advertised</state>
    </item>
    <item>
      <cidr>9.17.0.0/24</cidr>
      <description>blabla</description>
      <statusMessage/>
      <state>advertised</state>
    </item>
  </byoipCidrSet>
  <requestId>c9ab43f0-b6e9-4aed-97d2-42802109da9a</requestId>
  <ResponseMetadata>
    <RequestId>c9ab43f0-b6e9-4aed-97d2-42802109da9a</RequestId>
  </ResponseMetadata>Des
</DescribeByoipCidrsResponse>"""

PROVISION_BYOIP_CIDR = br"""<ProvisionByoipCidrResponse>
  <byoipCidr>
    <cidr>123.3.0.0/23</cidr>
    <description>123.3.0.0/23 PI block belonging to some user</description>
    <statusMessage/>
    <state>pending-provision</state>
  </byoipCidr>
  <requestId>4d39d116-5b2e-42f2-bf57-fbcf827c0853</requestId>
  <ResponseMetadata>
    <RequestId>4d39d116-5b2e-42f2-bf57-fbcf827c0853</RequestId>
  </ResponseMetadata>
</ProvisionByoipCidrResponse>"""

DEPROVISION_BYOIP_CIDR = br"""<DeprovisionByoipCidrResponse>
  <byoipCidr>
    <cidr>123.3.0.0/23</cidr>
    <description>123.3.0.0/23 PI block belonging to some user</description>
    <statusMessage/>
    <state>pending-deprovision</state>
  </byoipCidr>
  <requestId>824e8dc2-396e-4727-b8d9-3e8f608b6ade</requestId>
  <ResponseMetadata>
    <RequestId>824e8dc2-396e-4727-b8d9-3e8f608b6ade</RequestId>
  </ResponseMetadata>
</DeprovisionByoipCidrResponse>"""


class TestPublicIpv4Pools(AWSMockServiceTestCase):
    connection_class = EC2Connection

    def test_describe_public_ipv4_pools(self):
        self.set_http_response(status_code=200, body=DESCRIBE_PUBLIC_IPV4_POOLS)
        pools = self.service_connection.get_all_public_ipv4_pools()
        self.assertEqual(len(pools), 1)

        for field in ['id', 'description', 'total_address_count', 'pool_address_ranges',
                      'total_available_address_count', 'total_address_count']:
            self.assertTrue(field in pools[0].__dict__.keys())

        self.assertEqual(len(pools[0].pool_address_ranges), 3)
        self.assertEqual(pools[0].total_available_address_count, 759)
        self.assertEqual(pools[0].total_address_count, 768)
        self.assertEqual(pools[0].id, 'ipv4pool-ec2-4E58D35D')


class TestByoipCidrs(AWSMockServiceTestCase):
    connection_class = EC2Connection

    def test_describe_byoip_cidrs(self):
        self.set_http_response(status_code=200, body=DESCRIBE_BYOIP_CIDRS)
        cidrs = self.service_connection.get_all_byoip_cidrs()
        self.assertEqual(len(cidrs), 3)
        cidr_set = ('7.0.0.0/24', '9.16.0.0/24', '9.17.0.0/24')

        for cidr in cidrs:
            for field in ['id', 'description', 'state', 'cidr', 'status_message']:
                self.assertTrue(field in cidr.__dict__.keys())
            self.assertTrue(cidr.cidr in cidr_set)

    def test_provision_byoip_cidr(self):
        self.set_http_response(status_code=200, body=PROVISION_BYOIP_CIDR)
        cidr = self.service_connection.provision_byoip_cidr('123.3.0.0/23')

        for field in ['id', 'cidr', 'description', 'state', 'status_message']:
            self.assertTrue(field in cidr.__dict__.keys())

        self.assertEqual(cidr.id, '123.3.0.0/23')
        self.assertEqual(cidr.description, '123.3.0.0/23 PI block belonging to some user')
        self.assertEqual(cidr.state, 'pending-provision')

    def test_deprovision_byoip_cidr(self):
        self.set_http_response(status_code=200, body=DEPROVISION_BYOIP_CIDR)
        cidr = self.service_connection.deprovision_byoip_cidr('123.3.0.0/23')

        for field in ['id', 'cidr', 'description', 'state', 'status_message']:
            self.assertTrue(field in cidr.__dict__.keys())

        self.assertEqual(cidr.id, '123.3.0.0/23')
        self.assertEqual(cidr.description, '123.3.0.0/23 PI block belonging to some user')
        self.assertEqual(cidr.state, 'pending-deprovision')
