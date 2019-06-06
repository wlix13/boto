#!/usr/bin/env python
# Copyright (c) 2012 Amazon.com, Inc. or its affiliates.  All Rights Reserved
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
#

from tests.compat import mock, unittest
from tests.unit import AWSMockServiceTestCase

from boto.exception import BotoClientError
from boto.ec2 import EC2Connection
from boto.ec2.networkinterface import NetworkInterfaceCollection
from boto.ec2.networkinterface import NetworkInterfaceSpecification
from boto.ec2.networkinterface import PrivateIPAddress
from boto.ec2.networkinterface import Association, Attachment, NetworkInterface


class NetworkInterfaceTests(unittest.TestCase):
    def setUp(self):

        self.attachment = Attachment()
        self.attachment.id = 'eni-attach-1'
        self.attachment.instance_id = 10
        self.attachment.status = "some status"
        self.attachment.device_index = 100

        self.eni_one = NetworkInterface()
        self.eni_one.id = 'eni-1'
        self.eni_one.status = "one_status"
        self.eni_one.attachment = self.attachment

        self.eni_two = NetworkInterface()
        self.eni_two.connection = mock.Mock()
        self.eni_two.id = 'eni-2'
        self.eni_two.status = "two_status"
        self.eni_two.attachment = None

    def test_update_with_validate_true_raises_value_error(self):
        self.eni_one.connection = mock.Mock()
        self.eni_one.connection.get_all_network_interfaces.return_value = []
        with self.assertRaisesRegexp(ValueError, "^eni-1 is not a valid ENI ID$"):
            self.eni_one.update(True)

    def test_update_with_result_set_greater_than_0_updates_dict(self):
        self.eni_two.connection.get_all_network_interfaces.return_value = [self.eni_one]
        self.eni_two.update()

        assert all([self.eni_two.status == "one_status",
                    self.eni_two.id == 'eni-1',
                    self.eni_two.attachment == self.attachment])

    def test_update_returns_status(self):
        self.eni_one.connection = mock.Mock()
        self.eni_one.connection.get_all_network_interfaces.return_value = [self.eni_two]
        retval = self.eni_one.update()
        self.assertEqual(retval, "two_status")

    def test_attach_calls_attach_eni(self):
        self.eni_one.connection = mock.Mock()
        self.eni_one.attach("instance_id", 11)
        self.eni_one.connection.attach_network_interface.assert_called_with(
            'eni-1',
            "instance_id",
            11,
            dry_run=False
        )

    def test_detach_calls_detach_network_interface(self):
        self.eni_one.connection = mock.Mock()
        self.eni_one.detach()
        self.eni_one.connection.detach_network_interface.assert_called_with(
            'eni-attach-1',
            False,
            dry_run=False
        )

    def test_detach_with_no_attach_data(self):
        self.eni_two.connection = mock.Mock()
        self.eni_two.detach()
        self.eni_two.connection.detach_network_interface.assert_called_with(
            None, False, dry_run=False)

    def test_detach_with_force_calls_detach_network_interface_with_force(self):
        self.eni_one.connection = mock.Mock()
        self.eni_one.detach(True)
        self.eni_one.connection.detach_network_interface.assert_called_with(
            'eni-attach-1', True, dry_run=False)


class TestNetworkInterfaceCollection(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.private_ip_address1 = PrivateIPAddress(
            private_ip_address='10.0.0.10', primary=False)
        self.private_ip_address2 = PrivateIPAddress(
            private_ip_address='10.0.0.11', primary=False)
        self.network_interfaces_spec1 = NetworkInterfaceSpecification(
            device_index=1, subnet_id='subnet_id',
            description='description1',
            private_ip_address='10.0.0.54', delete_on_termination=False,
            private_ip_addresses=[self.private_ip_address1,
                                  self.private_ip_address2]
        )

        self.private_ip_address3 = PrivateIPAddress(
            private_ip_address='10.0.1.10', primary=False)
        self.private_ip_address4 = PrivateIPAddress(
            private_ip_address='10.0.1.11', primary=False)
        self.network_interfaces_spec2 = NetworkInterfaceSpecification(
            device_index=2, subnet_id='subnet_id2',
            description='description2',
            groups=['group_id1', 'group_id2'],
            private_ip_address='10.0.1.54', delete_on_termination=False,
            private_ip_addresses=[self.private_ip_address3,
                                  self.private_ip_address4]
        )

        self.network_interfaces_spec3 = NetworkInterfaceSpecification(
            device_index=0, subnet_id='subnet_id2',
            description='description2',
            groups=['group_id1', 'group_id2'],
            private_ip_address='10.0.1.54', delete_on_termination=False,
            private_ip_addresses=[self.private_ip_address3,
                                  self.private_ip_address4],
            associate_public_ip_address=True
        )

        self.network_interfaces_spec4 = NetworkInterfaceSpecification(
            device_index=4, switch_id='switch_id4', description='description4',
            delete_on_termination=True,
        )

    def test_param_serialization(self):
        collection = NetworkInterfaceCollection(self.network_interfaces_spec1,
                                                self.network_interfaces_spec2,
                                                self.network_interfaces_spec4)
        params = {}
        collection.build_list_params(params)
        self.assertDictEqual(params, {
            'NetworkInterface.0.DeviceIndex': '1',
            'NetworkInterface.0.DeleteOnTermination': 'false',
            'NetworkInterface.0.Description': 'description1',
            'NetworkInterface.0.PrivateIpAddress': '10.0.0.54',
            'NetworkInterface.0.SubnetId': 'subnet_id',
            'NetworkInterface.0.PrivateIpAddresses.0.Primary': 'false',
            'NetworkInterface.0.PrivateIpAddresses.0.PrivateIpAddress':
                '10.0.0.10',
            'NetworkInterface.0.PrivateIpAddresses.1.Primary': 'false',
            'NetworkInterface.0.PrivateIpAddresses.1.PrivateIpAddress':
                '10.0.0.11',
            'NetworkInterface.1.DeviceIndex': '2',
            'NetworkInterface.1.Description': 'description2',
            'NetworkInterface.1.DeleteOnTermination': 'false',
            'NetworkInterface.1.PrivateIpAddress': '10.0.1.54',
            'NetworkInterface.1.SubnetId': 'subnet_id2',
            'NetworkInterface.1.SecurityGroupId.0': 'group_id1',
            'NetworkInterface.1.SecurityGroupId.1': 'group_id2',
            'NetworkInterface.1.PrivateIpAddresses.0.Primary': 'false',
            'NetworkInterface.1.PrivateIpAddresses.0.PrivateIpAddress':
                '10.0.1.10',
            'NetworkInterface.1.PrivateIpAddresses.1.Primary': 'false',
            'NetworkInterface.1.PrivateIpAddresses.1.PrivateIpAddress':
                '10.0.1.11',
            'NetworkInterface.2.DeviceIndex': '4',
            'NetworkInterface.2.SwitchId': 'switch_id4',
            'NetworkInterface.2.Description': 'description4',
            'NetworkInterface.2.DeleteOnTermination': 'true',
        })

    def test_add_prefix_to_serialization(self):
        collection = NetworkInterfaceCollection(self.network_interfaces_spec1,
                                                self.network_interfaces_spec2)
        params = {}
        collection.build_list_params(params, prefix='LaunchSpecification.')
        # We already tested the actual serialization previously, so
        # we're just checking a few keys to make sure we get the proper
        # prefix.
        self.assertDictEqual(params, {
            'LaunchSpecification.NetworkInterface.0.DeviceIndex': '1',
            'LaunchSpecification.NetworkInterface.0.DeleteOnTermination':
                'false',
            'LaunchSpecification.NetworkInterface.0.Description':
                'description1',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddress':
                '10.0.0.54',
            'LaunchSpecification.NetworkInterface.0.SubnetId': 'subnet_id',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddresses.0.Primary':
                'false',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddresses.0.PrivateIpAddress':
                '10.0.0.10',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddresses.1.Primary': 'false',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddresses.1.PrivateIpAddress':
                '10.0.0.11',
            'LaunchSpecification.NetworkInterface.1.DeviceIndex': '2',
            'LaunchSpecification.NetworkInterface.1.Description':
                'description2',
            'LaunchSpecification.NetworkInterface.1.DeleteOnTermination':
                'false',
            'LaunchSpecification.NetworkInterface.1.PrivateIpAddress':
                '10.0.1.54',
            'LaunchSpecification.NetworkInterface.1.SubnetId': 'subnet_id2',
            'LaunchSpecification.NetworkInterface.1.SecurityGroupId.0':
                'group_id1',
            'LaunchSpecification.NetworkInterface.1.SecurityGroupId.1':
                'group_id2',
            'LaunchSpecification.NetworkInterface.1.PrivateIpAddresses.0.Primary':
                'false',
            'LaunchSpecification.NetworkInterface.1.PrivateIpAddresses.0.PrivateIpAddress':
                '10.0.1.10',
            'LaunchSpecification.NetworkInterface.1.PrivateIpAddresses.1.Primary':
                'false',
            'LaunchSpecification.NetworkInterface.1.PrivateIpAddresses.1.PrivateIpAddress':
                '10.0.1.11',
        })

    def test_cant_use_public_ip(self):
        collection = NetworkInterfaceCollection(self.network_interfaces_spec3,
                                                self.network_interfaces_spec1)
        params = {}

        # First, verify we can't incorrectly create multiple interfaces with
        # on having a public IP.
        with self.assertRaises(BotoClientError):
            collection.build_list_params(params, prefix='LaunchSpecification.')

        # Next, ensure it can't be on device index 1.
        self.network_interfaces_spec3.device_index = 1
        collection = NetworkInterfaceCollection(self.network_interfaces_spec3)
        params = {}

        with self.assertRaises(BotoClientError):
            collection.build_list_params(params, prefix='LaunchSpecification.')

    def test_public_ip(self):
        # With public IP.
        collection = NetworkInterfaceCollection(self.network_interfaces_spec3)
        params = {}
        collection.build_list_params(params, prefix='LaunchSpecification.')

        self.assertDictEqual(params, {
            'LaunchSpecification.NetworkInterface.0.AssociatePublicIpAddress':
                'true',
            'LaunchSpecification.NetworkInterface.0.DeviceIndex': '0',
            'LaunchSpecification.NetworkInterface.0.DeleteOnTermination':
                'false',
            'LaunchSpecification.NetworkInterface.0.Description':
                'description2',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddress':
                '10.0.1.54',
            'LaunchSpecification.NetworkInterface.0.SubnetId': 'subnet_id2',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddresses.0.Primary':
                'false',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddresses.0.PrivateIpAddress':
                '10.0.1.10',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddresses.1.Primary':
                'false',
            'LaunchSpecification.NetworkInterface.0.PrivateIpAddresses.1.PrivateIpAddress':
                '10.0.1.11',
            'LaunchSpecification.NetworkInterface.0.SecurityGroupId.0':
                'group_id1',
            'LaunchSpecification.NetworkInterface.0.SecurityGroupId.1':
                'group_id2',
        })


class TestDescribeNetworkInterfaces(AWSMockServiceTestCase):
    connection_class = EC2Connection

    def default_body(self):
        return b"""
            <DescribeNetworkInterfacesResponse xmlns="http://ec2.amazonaws.com/doc/2014-10-01/">
              <requestId>47c6a494-08a9-47d9-89e3-884bb87a2130</requestId>
              <networkInterfaceSet>
                <item>
                  <networkInterfaceId>eni-5d22cec4</networkInterfaceId>
                  <subnetId>subnet-e8a8b6b5</subnetId>
                  <vpcId>vpc-a894d1d3</vpcId>
                  <availabilityZone>us-east-1a</availabilityZone>
                  <description>Primary network interface</description>
                  <status>in-use</status>
                  <macAddress>0e:bc:c1:69:7d:7a</macAddress>
                  <privateIpAddress>172.10.10.217</privateIpAddress>
                  <sourceDestCheck>true</sourceDestCheck>
                  <attachment>
                    <attachmentId>eni-attach-e878d8f0</attachmentId>
                    <instanceId>i-00f2f9ed1bbd6b2a2</instanceId>
                    <deviceIndex>0</deviceIndex>
                    <status>attached</status>
                    <deleteOnTermination>true</deleteOnTermination>
                  </attachment>
                  <association>
                    <publicIp>18.208.84.240</publicIp>
                    <publicDnsName/>
                    <allocationId>eipalloc-9e2ad396</allocationId>
                    <associationId>eipassoc-970f913c</associationId>
                  </association>
                  <tagSet/>
                  <privateIpAddressesSet>
                    <item>
                      <privateIpAddress>172.10.10.217</privateIpAddress>
                      <primary>true</primary>
                      <association>
                        <publicIp>18.208.84.240</publicIp>
                        <publicDnsName/>
                        <allocationId>eipalloc-9e2ad396</allocationId>
                        <associationId>eipassoc-970f913c</associationId>
                      </association>
                    </item>
                    <item>
                      <privateIpAddress>172.10.10.218</privateIpAddress>
                      <privateDnsName/>
                      <primary>false</primary>
                      <association>
                        <publicIp>18.210.215.25</publicIp>
                        <publicDnsName/>
                        <allocationId>eipalloc-e0ded8e8</allocationId>
                        <associationId>eipassoc-a4005b0f</associationId>
                      </association>
                    </item>
                  </privateIpAddressesSet>
                </item>
              </networkInterfaceSet>
            </DescribeNetworkInterfacesResponse>
        """

    def test_get_all_route_tables(self):
        self.set_http_response(status_code=200)
        api_response = self.service_connection.get_all_network_interfaces()
        self.assertEquals(len(api_response), 1)
        self.assertIsInstance(api_response[0], NetworkInterface)
        self.assertIsInstance(api_response[0].association, Association)
        self.assertEquals(
            api_response[0].association.allocation_id, "eipalloc-9e2ad396")
        self.assertEquals(
            api_response[0].association.id, "eipassoc-970f913c")
        self.assertEquals(
            api_response[0].association.public_ip, "18.208.84.240")
        self.assertEquals(
            api_response[0].association.allocation_id,
            api_response[0].private_ip_addresses[0].association.allocation_id)
        self.assertEquals(
            api_response[0].association.id,
            api_response[0].private_ip_addresses[0].association.id)
        self.assertEquals(
            api_response[0].association.public_ip,
            api_response[0].private_ip_addresses[0].association.public_ip)
        self.assertEquals(
            api_response[0].private_ip_addresses[1].association.allocation_id,
            "eipalloc-e0ded8e8")
        self.assertEquals(
            api_response[0].private_ip_addresses[1].association.id,
            "eipassoc-a4005b0f")
        self.assertEquals(
            api_response[0].private_ip_addresses[1].association.public_ip,
            "18.210.215.25")


if __name__ == '__main__':
    unittest.main()
