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


class ExportTask(EC2Object):
    """
    Represents an EC2 ExportTask.
    """

    def __init__(self, connection=None):
        super(ExportTask, self).__init__(connection)
        self.request_id = None
        self.description = None
        self.id = None
        self.container_format = None
        self.disk_image_format = None
        self.bucket_name = self.s3_bucket = None
        self.bucket_path = self.s3_key = None
        self.instance_id = None
        self.target_environment = None
        self.state = None
        self.status_message = None
        self.volume_export_details = None

    def startElement(self, name, attrs, connection):
        retval = super(ExportTask, self).startElement(name, attrs, connection)
        if retval is not None:
            return retval

        if name == 'volumeExportDetails':
            self.volume_export_details = VolumeExportDetails()
            return self.volume_export_details
        return None

    def endElement(self, name, value, connection):
        if name == 'exportTaskId':
            self.id = value
        elif name == 'containerFormat':
            self.container_format= value
        elif name == 'diskImageFormat':
            self.disk_image_format = value
        elif name == 's3Bucket':
            self.bucket_name = self.s3_bucket = value
        elif name == 's3Key':
            self.bucket_path = self.s3_key = value
        elif name == 'instanceId':
            self.instance_id = value
        elif name == 'targetEnvironment':
            self.target_environment = value
        elif name == 'statusMessage':
            self.status_message= value
        else:
            setattr(self, name, value)


class ExportVolumeTask(ExportTask):
    """
    Represents custom EC2 ExportVolumeTask
    """

    def __init__(self, connection=None):
        super(ExportVolumeTask, self).__init__(connection)
        self.volume_id = None

    def endElement(self, name, value, connection):
        super(ExportVolumeTask, self).endElement(name, value, connection)
        if name == "volumeId":
            self.volume_id = value


class VolumeExportDetails(list):
    def __init__(self, connection=None):
        super(VolumeExportDetails, self).__init__()
        self.connection = connection

    def startElement(self, name, attrs, connection):
        if name == 'item':
            item = ExportVolumeTask(self)
            self.append(item)
            return item

    def endElement(self, name, value, connection):
        pass
