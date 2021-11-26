What is jabberwock
=============

jabberwock is a **Python 3** library that helps with accessing Cisco
Callmanger over the AXL interface. This library is a refactoring of
[pyaxl](https://pypi.org/project/pyaxl/) to use
[zeep](https://pypi.org/project/zeep/) instead of
[suds-jurko](https://pypi.org/project/suds-jurko/) as the SOAP-based web
service client for calls to the AXL API. We use
[SoupUI](http://www.soapui.org/) and recommend it if you want to work
with this library, as it helps in analyzing and understanding how the
WSDL from Cisco Callmanager is composed.

jabberwock is licensed under the ZPL 2.1, see LICENSE.txt for details.

Import WSDL
===========

The WSDL files are not included with this library due to licenses terms.
jabberwock provides a script to import it and then build a cache
directly into the library.

First of all, you need to download the WSDL files. The AXL WSDL is
included in the AXL SQL Toolkit download, which is available in Cisco
Unified CM. Follow these steps to download the AXL SQL Toolkit from your
Cisco Unified CM server:

1.  Log into the Cisco Unified CM Administration application.
2.  Go to Application | Plugins
3.  Click on the Download link by the Cisco CallManager AXL SQL Toolkit
    Plugin.

The axlsqltoolkit.zip file contains the complete schema definition for
different versions of Cisco Unified CM.

The important files for each version are:
:   -   AXLAPI.wsdl
    -   AXLEnums.xsd
    -   axlmessage.xsd
    -   axlsoap.xsd
    -   axl.xsd

Note: all files must be in the same directory and have the same name as
the version you want use.

``` {.sourceCode .bash}
$ ./pyaxl_import_wsdl -p path_to_wsdl/10.5/AXLAPI.wsdl
```

Hint: We put all these file in the buildout directory. While buildout is
running, the WSDL files are imported automatically.

``` {.sourceCode .ini}
[buildout]
parts =
    pyaxl_import
    pyaxl_import_exec

[pyaxl_import]
recipe = zc.recipe.egg:scripts
eggs = pyaxl
scripts=pyaxl_import_wsdl=import_wsdl

[pyaxl_import_exec]
recipe = collective.recipe.cmd
on_install=true
on_update=true
cmds = ${buildout:directory}/bin/import_wsdl -p ${buildout:directory}/wsdl/10.5/AXLAPI.wsdl
```

Configuration
=============

\>\>\> import pyaxl \>\>\> from pyaxl import ccm \>\>\> from
pyaxl.testing import validate \>\>\> from pyaxl.testing.transport import
TestingTransport

For these tests we use a fake transport layer. For this we must tell
which xml the transporter should use for the response.

\>\>\> transport = TestingTransport() \>\>\>
transport.define('10.5\_user\_riols') \>\>\> transport\_testing =
TestingTransport() \>\>\> transport\_testing.define('8.0\_user\_riols')

\>\>\> settings =
pyaxl.AXLClientSettings(host='<https://callmanger.fake:8443>', ...
user='super-admin', ... passwd='nobody knows', ... path='/axl/', ...
version='10.5', ... suds\_config=dict(transport=transport)) \>\>\>
pyaxl.registry.register(settings)

pyaxl supports multiple settings. To use that, pass the configuration
name as second attribute in the register method.

\>\>\> settings\_testing =
pyaxl.AXLClientSettings(host='<https://callmanger-testing.fake:8443>',
... user='super-admin', ... passwd='nobody knows', ... path='/axl/', ...
version='8.0', ... suds\_config=dict(transport=transport\_testing))
\>\>\> pyaxl.registry.register(settings\_testing, 'testing')

if you want to use a custom configuration, you also need to pass it when
you are getting the object:

\>\>\> user = ccm.User('riols', configname='testing')

if you don't need multiple settings, you can just use the default.

\>\>\> user = ccm.User('riols')

Don't forget to build the cache for the defined configuration name:

``` {.sourceCode .bash}
$ ./pyaxl_import_wsdl -p -c testing path_to_wsdl/10.5/AXLAPI.wsdl
```

Working with pyaxl
==================

Get all information for a specific user.
----------------------------------------

\>\>\> transport.define('10.5\_user\_riols') \>\>\> user1 =
ccm.User('riols')

\>\>\> validate.printSOAPRequest(transport.lastrequest()) getUser:
userid=riols

\>\>\> user1.firstName Samuel \>\>\> user1.lastName Riolo

Get the same user with his UUID.
--------------------------------

\>\>\> transport.define('10.5\_user\_riols') \>\>\> user2 =
ccm.User(uuid='{5B5C014F-63A8-412F-B793-782BDA987371}') \>\>\>
user1.\_uuid == user2.\_uuid True

Search and list information
---------------------------

\>\>\> transport.define('10.5\_user\_armstrong') \>\>\> users =
ccm.User.list(dict(lastName='Armstrong'), ('firstName', 'lastName'))
\>\>\> validate.printSOAPRequest(transport.lastrequest()) listUser:
searchCriteria: lastName=Armstrong returnedTags: firstName=True
lastName=True

\>\>\> list(users) [(Lance, Armstrong), (Neil, Armstrong)]

Search and fetch information as objects
---------------------------------------

\>\>\> transport.define('10.5\_user\_riols') \>\>\> users =
ccm.User.list\_obj(dict(lastName='Riolo', firstName='Samuel')) \>\>\>
for user in users: ... print(user.firstName, user.lastName) Samuel Riolo

Reload an object
----------------

\>\>\> transport.define('10.5\_user\_riols') \>\>\> user =
ccm.User('riols') \>\>\> user.firstName = 'Yuri' \>\>\> user.lastName =
'Gagarin' \>\>\> print(user.firstName, user.lastName) Yuri Gagarin
\>\>\> user.reload() Traceback (most recent call last): ...
pyaxl.exceptions.ReloadException: Error because some field are already
changed by the client. Use force or update it first. \>\>\>
user.reload(force=True) \>\>\> print(user.firstName, user.lastName)
Samuel Riolo

Update an object
----------------

\>\>\> transport.define('10.5\_user\_riols') \>\>\> user =
ccm.User('riols') \>\>\> user.firstName = 'Claude' \>\>\> user.lastName
= 'Nicollier' \>\>\> user.update() \>\>\>
validate.printSOAPRequest(transport.lastrequest()) updateUser:
uuid={5B5C014F-63A8-412F-B793-782BDA987371} firstName=Claude
lastName=Nicollier

Remove an object
----------------

\>\>\> transport.define('10.5\_user\_riols') \>\>\> user =
ccm.User('riols') \>\>\> user.remove() \>\>\>
validate.printSOAPRequest(transport.lastrequest()) removeUser:
uuid={5B5C014F-63A8-412F-B793-782BDA987371}

Create a new object
-------------------

\>\>\> transport.define('10.5\_user\_riols') \>\>\> user = ccm.User()
\>\>\> user.lastName = 'Edison' \>\>\> user.firstName = 'Thomas' \>\>\>
user.userid = 'tedison' \>\>\> user.presenceGroupName = 'SC Presence
Group' \>\>\> user.ipccExtension = None \>\>\> user.ldapDirectoryName =
None \>\>\> user.userProfile = None \>\>\> user.serviceProfile = None
\>\>\> user.primaryDevice = None \>\>\> user.pinCredentials = None
\>\>\> user.passwordCredentials = None \>\>\>
user.subscribeCallingSearchSpaceName = None \>\>\> user.defaultProfile =
None \>\>\> user.convertUserAccount = None

\>\>\> user.update() Traceback (most recent call last): ...
pyaxl.exceptions.UpdateException: you must create a object with "create"
before update

\>\>\> user.create() {12345678-1234-1234-1234-123123456789} \>\>\>
validate.printSOAPRequest(transport.lastrequest()) addUser: user:
firstName=Thomas lastName=Edison userid=tedison presenceGroupName=SC
Presence Group

If you try to create a user twice, an Exception of the type
CreationException is thrown:

\>\>\> user.create() Traceback (most recent call last): ...
pyaxl.exceptions.CreationException: this object are already attached

Clone an object
---------------

\>\>\> transport.define('10.5\_user\_riols') \>\>\> user =
ccm.User('riols') \>\>\> clone = user.clone() \>\>\> clone.userid =
'riols2' \>\>\> clone.update() Traceback (most recent call last): ...
pyaxl.exceptions.UpdateException: you must create a object with "create"
before update \>\>\> clone.create()
{12345678-1234-1234-1234-123123456789}

Running the doc tests
=====================

``` {.sourceCode .bash}
$ tox --  <path to axlsqltoolkit directory>
```