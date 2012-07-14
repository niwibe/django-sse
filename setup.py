from setuptools import setup, find_packages

description="""
HTML5 Server-Side Events for Django 1.3, 1.4+

Documentation: http://www.niwi.be/post/django-sse-html5-server-sent-events-django/
"""

long_description = """"""


setup(
    name="django-sse",
    version=':versiontools:django_sse:',
    url='https://github.com/niwibe/django-sse',
    license='BSD',
    platforms=['OS Independent'],
    description = description.strip(),
    long_description = long_description.strip(),
    author = 'Andrei Antoukh',
    author_email = 'niwi@niwi.be',
    maintainer = 'Andrei Antoukh',
    maintainer_email = 'niwi@niwi.be',
    packages = [
        'django_sse',
    ],
    include_package_data = True,
    install_requires=[
        'distribute',
        'sse',
    ],
    setup_requires = [
        'versiontools >= 1.8',
    ],
    zip_safe = False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
