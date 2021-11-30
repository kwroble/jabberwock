What is jabberwock?
===================

jabberwock is a **Python 3** library that helps with accessing Cisco
CallManger over the AXL interface. This library is a refactoring of
[pyaxl](https://pypi.org/project/pyaxl/) to use
[zeep](https://pypi.org/project/zeep/) instead of
[suds-jurko](https://pypi.org/project/suds-jurko/) as the SOAP-based web
service client for calls to the AXL API. I recommend [SoupUI](http://www.soapui.org/) it if you want to work
with this library, as it helps in analyzing and understanding how the WSDL from Cisco CallManager is composed.

jabberwock is licensed under the ZPL 2.1, see LICENSE.txt for details.

Import WSDL
===========

The WSDL files are not included with this library for licensing reasons.
The AXL WSDL is included in the AXL SQL Toolkit download, which is available from your Cisco Unified CM server:

1.  Log into the Cisco Unified CM Administration application.
2.  Go to Application | Plugins
3.  Click on the Download link by the Cisco CallManager AXL SQL Toolkit
    Plugin.
4. Extract the contents of the downloaded .zip file to an accessible location.

The axlsqltoolkit.zip file contains the complete schema definition for different versions of Cisco Unified CM. 
The important files for each version are:
-   AXLAPI.wsdl
-   AXLEnums.xsd
-   axlSoap.xsd

Note: Do not modify the folder structure of the extracted files.
Proper use of jabberwock requires the following folder structure for the schema directory:

``` {.sourceCode .py}
schema/
    9.0/
        AXLAPI.wsdl
        AXLEnums.xsd
        AXLSoap.xsd
    9.1/
        AXLAPI.wsdl
        AXLEnums.xsd
        AXLSoap.xsd
    ...
    ...
    ...
    11.5/
        AXLAPI.wsdl
        AXLEnums.xsd
        AXLSoap.xsd
    12.5/
        AXLAPI.wsdl
        AXLEnums.xsd
        AXLSoap.xsd
    current/
        AXLAPI.wsdl
        AXLEnums.xsd
        AXLSoap.xsd
```

Configuration
=============
Import jabberwock 
-----------------
``` {.sourceCode .py}
>>> from jabberwock.configuration import registry
>>> from jabberwock.configuration import AXLClientSettings
>>> from jabberwock import ccm
>>> settings = AXLClientSettings(host='callmanager.fake.com',
                                 username='super-admin',
                                 password='wouldntyouliketoknow',
                                 schema_path='C:\\axlsqltoolkit\\schema',
                                 version='12.5')
>>> jabberwock.registry.register(settings)
```
jabberwock supports multiple settings configurations. To define a non-default configuration, pass the configuration
name as the second attribute in the register method.

``` {.sourceCode .py}
>>> settings = AXLClientSettings(host='callmanager-test.fake.com',
                                 username='super-admin',
                                 password='noneofyourbusiness',
                                 schema_path='C:\\axlsqltoolkit\\schema',
                                 version='10.0')
>>> jabberwock.registry.register(settings, 'test_config')
```

To use a non-default configuration, pass the config_name with each operation.
``` {.sourceCode .py}
>>> user = ccm.User(userid='kwroble', config_name='test_config')
```

Use cases for jabberwock
========================

Get all information for a specific object
----------------------------------------

``` {.sourceCode .py}
>>> user = ccm.User(userid='kwroble')
```

Get the same object with UUID
---------------------------
``` {.sourceCode .py}
>>> user = ccm.User(uuid='{12345678-1234-1234-1234-123123456789}')
```

Search and list information
---------------------------
``` {.sourceCode .py}
>>> users = ccm.User.list(criteria=dict(lastName='Kent'), returns=['firstName', 'lastName')])
>>> list(users)
[(Clark, Kent), (Jonathan, Kent), (Martha, Kent)]
```

Search and fetch information as objects
---------------------------------------
``` {.sourceCode .py}
>>> users = ccm.User.list_obj(criteria=dict(lastName='Kent'))
```

Reload an object
----------------
``` {.sourceCode .py}
>>> user = ccm.User(userid='kwroble')
>>> user.firstName = 'Clark'
>>> user.lastName = 'Kent'
>>> print(user.firstName, user.lastName)
Clark Kent
>>> user.reload()
>>> print(user.firstName, user.lastName)
Kyle Wroble
```
Update an object
----------------
``` {.sourceCode .py}
>>> user = ccm.User('kwroble')
>>> user.firstName = 'Clark'
>>> user.lastName = 'Kent'
>>> user.update()
```
Remove an object
----------------
``` {.sourceCode .py}
>>> user = ccm.User('kwroble')
>>> user.remove()
```

Create a new object
-------------------
``` {.sourceCode .py}
>>> user = ccm.User()
>>> user.lastName = 'Edison'
>>> user.firstName = 'Thomas'
>>> user.userid = 'tedison'
>>> user.update()
Traceback (most recent call last): ...
jabberwock.exceptions.UpdateException: you must create a object with "create" before update
>>> user.create()
{12345678-1234-1234-1234-123123456789}
```
If you try to create a user twice, an Exception of the type
CreationException is thrown:

``` {.sourceCode .py}
>>> user.create()
Traceback (most recent call last): ...
jabberwock.exceptions.CreationException: this object is already attached
```
Clone an object
---------------
``` {.sourceCode .py}
>>> user = ccm.User('kwroble')
>>> clone = user.clone()
>>> clone.userid = 'kwroble2'
>>> clone.update()
Traceback (most recent call last): ...
jabberwock.exceptions.UpdateException: you must create a object with "create" before update
>>> clone.create()
{12345678-1234-1234-1234-123123456789}
```