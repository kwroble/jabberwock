import logging
import types
from jabberwocky.ccm.xtypes import XPhoneLine, XEnduserMember

log = logging.getLogger('pyaxl')


class MixingAbstractTemplate(object):
    """ Mixing class for all Types with template support.
    """

    @classmethod
    def template(cls, *args, typeclass=None, **kwargs):
        """ return with the given search criteria an complete object.
            On this object all attributes are pre-set with the
            values from template.
        """
        template = cls(*args, **kwargs)
        log.debug('%s created from template, criteria: %s, %s' % (cls.__name__, str(args), str(kwargs),))
        obj = template.clone()
        if typeclass is not None:
            obj['class'] = typeclass
        return obj


class MixingAbstractLines(object):

    def set_lines(self, lines):
        """Associate a list or a single ccm.Line object to device."""

        if not isinstance(lines, (list, types.GeneratorType)):
            lines = [lines]
        self.set_phone_lines(self._line_to_phone_line(lines))

    def set_line_user_association(self, user, phone_line):
        """Associate an end user with a line appearance."""
        if not phone_line.associatedEndusers:
            phone_line.associatedEndusers = {'enduser': []}
        if isinstance(user, str):
            enduser = XEnduserMember(userId=user)
        else:
            enduser = XEnduserMember(userId=user.userid)
        phone_line.associatedEndusers['enduser'].append(enduser)
        self.lines = self.lines

    def set_phone_lines(self, phone_lines):
        """Associate a list or a single ccm.XPhoneLine object to device."""
        if not isinstance(phone_lines, (list, types.GeneratorType)):
            phone_lines = [phone_lines]
        self.lines = {'line': phone_lines}

    def remove_phone_lines(self, phone_lines):
        """Disassociate a list or a single ccm.XPhoneLine object from device."""
        if not isinstance(phone_lines, (list, types.GeneratorType)):
            phone_lines = [phone_lines]
        self.removeLines = {'line': phone_lines}

    def _line_to_phone_line(self, lines):
        """Convert a list or single ccm.Line object to XPhoneLine object."""
        if not isinstance(lines, (list, types.GeneratorType)):
            lines = [lines]
        for index, line in enumerate(lines):
            yield XPhoneLine(index=index + 1, dirn={'pattern': line.pattern, 'uuid': line.uuid})
