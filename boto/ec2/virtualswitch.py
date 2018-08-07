"""Croc Cloud EC2 Virtual Switch."""

from boto.ec2.ec2object import TaggedEC2Object


class VirtualSwitch(TaggedEC2Object):

    def __init__(self, connection=None, id=None, name=None):
        super(VirtualSwitch, self).__init__(connection)
        self.id = id
        self.name = name

    def __repr__(self):
        return 'VirtualSwitch:%s' % self.name

    def startElement(self, name, attrs, connection):
        retval = super(VirtualSwitch, self).startElement(name, attrs,
                                                         connection)
        if retval is not None:
            return retval
        else:
            return

    def endElement(self, name, value, connection):
        if name == 'switchId':
            self.id = value
        elif name == 'switchName':
            self.name = value
        elif name == 'return':
            if value == 'false':
                self.status = False
            elif value == 'true':
                self.status = True
            else:
                raise Exception(
                    'Unexpected value of status '
                    '%s for group %s' % (value, self.name))

        else:
            setattr(self, name, value)

    def delete(self, dry_run=False):
        """
        Delete virtual switch.

        :type dry_run: bool
        :param dry_run: dry run
        """
        kwargs = {'switch_id': self.id} if self.id else {'name': self.name}
        kwargs['dry_run'] = dry_run

        return self.connection.delete_virtual_switch(**kwargs)

    def create(self, dry_run=False):
        """
        Create virtual switch.

        :type dry_run: bool
        :param dry_run: dry run

        :rtype: :class:`boto.ec2.virtualswitch.VirtualSwitch`
        :return: created virtual switch
        """
        kwargs = {
            'name': self.name,
            'dry_run': dry_run,
        }

        return self.connection.create_virtual_switch(**kwargs)
