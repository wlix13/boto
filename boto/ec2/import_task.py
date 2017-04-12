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


from boto.ec2.ec2object import EC2Object


SNAPSHOT_DETAIL_ATTRS = ['description', 'deviceName', 'diskImageSize', 'format', 'progress', 'snapshotId',
                         'status', 'statusMessage', 'url']


class SnapshotDetail(EC2Object):
    def __init__(self, connection=None, description=None, device_name=None, disk_image_size=None, format=None,
                 progress=None, snapshot_id=None, status=None, status_message=None, url=None):
        super(SnapshotDetail, self).__init__(connection)
        self.connection = connection
        self.description = description
        self.device_name = device_name
        self.disk_image_size = disk_image_size
        self.format = format
        self.progress = progress
        self.snapshot_id = snapshot_id
        self.status = status
        self.status_message = status_message
        self.url = url
        self.user_bucket = None

    def startElement(self, name, attrs, connection):
        if name == 'userBucket':
            self.user_bucket = UserBucketDetails()
            return self.user_bucket
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'deviceName':
            self.device_name = value
        elif name == 'diskImageSize':
            self.disk_image_size = value
        elif name == 'snapshotId':
            self.snapshot_id = value
        elif name == 'statusMessage':
            self.status_message = value
        else:
            setattr(self, name, value)


class SnapshotDetails(list):
    def __init__(self, connection=None):
        super(SnapshotDetails, self).__init__()
        self.connection = connection
        self.attr_names = SNAPSHOT_DETAIL_ATTRS

    def startElement(self, name, attrs, connection):
        if name == 'item':
            snapshot = SnapshotDetail(self)
            self.append(snapshot)
            return snapshot

    def endElement(self, name, value, connection):
        pass


class ImportSnapshotTask(SnapshotDetail):
    """
    Represents an EC2 ImportSnapshotTask
    """

    def __init__(self, connection=None):
        super(ImportSnapshotTask, self).__init__(connection)
        self.request_id = None
        self.id = None

    def __repr__(self):
        return 'ImportSnapshotTask:%s' % self.id

    def endElement(self, name, value, connection):
        super(ImportSnapshotTask, self).endElement(name, value, connection)
        if name == 'importTaskId':
            self.id = value


class ImportImageTask(EC2Object):
    """
    Represents an EC2 ImportImageTask
    """

    def __init__(self, connection=None):
        super(ImportImageTask, self).__init__(connection)
        self.request_id = None
        self.architecture = None
        self.description = None
        self.hypervisor = None
        self.image_id = None
        self.id = None
        self.license_type = None
        self.platform = None
        self.progress = None
        self.snapshot_details = None
        self.status = None
        self.status_message = None
        self.snapshot_details = None

    def __repr__(self):
        return 'ImportImageTask:%s' % self.image_id

    def startElement(self, name, attrs, connection):
        retval = super(ImportImageTask, self).startElement(name, attrs, connection)
        if retval is not None:
            return retval
        if name == 'snapshotDetails':
            self.snapshot_details = SnapshotDetails()
            return self.snapshot_details
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'imageId':
            self.image_id = value
        elif name == 'importTaskId':
            self.id = value
        elif name == 'licenseType':
            self.license_type = value
        elif name == 'statusMessage':
            self.status_message = value
        else:
            setattr(self, name, value)


class UserBucketDetails(EC2Object):
    def __init__(self, connection=None):
        super(UserBucketDetails, self).__init__(connection)
        self.bucket_name = None
        self.bucket_path = None

    def startElement(self, name, attrs, connection):
        pass

    def endElement(self, name, value, connection):
        if name == 's3Bucket':
            self.bucket_name = value
        elif name == 's3Key':
            self.bucket_path = value
