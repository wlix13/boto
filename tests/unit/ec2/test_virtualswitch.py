#!/usr/bin/env python

from tests.compat import unittest
from tests.unit import AWSMockServiceTestCase

from boto.ec2.connection import EC2Connection


DESCRIBE_VIRTUAL_SWITCH = br"""
<DescribeVirtualSwitchesResponse>
    <virtualSwitchInfo>
        <item>
            <switchId>sw-XXXXXXXX</switchId>
            <switchName>switch-name</switchName>
        </item>
    </virtualSwitchInfo>
    <requestId>7cd01b5e-b105-46ec-a9d5-6d2dee1910f3</requestId>
    <ResponseMetadata>
        <RequestId>7cd01b5e-b105-46ec-a9d5-6d2dee1910f3</RequestId>
    </ResponseMetadata>
</DescribeVirtualSwitchesResponse>"""


class TestDescribeVolumeSwitches(AWSMockServiceTestCase):
    connection_class = EC2Connection

    def test_get_all_virtual_switches(self):
        self.set_http_response(status_code=200, body=DESCRIBE_VIRTUAL_SWITCH)

        switches = self.service_connection.get_all_virtual_switches()
        self.assertEqual(1, len(switches))
        self.assertEqual('sw-XXXXXXXX', switches[0].id)
        self.assertEqual('switch-name', switches[0].name)


if __name__ == '__main__':
    unittest.main()
