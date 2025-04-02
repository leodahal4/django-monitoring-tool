from setuptools import setup, find_packages

setup(
    name='django_health_metrics',
    version='1.0.0',
    description='A Django app providing /metrics and /health endpoints for monitoring and health checks.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Mou Sam Dahal',
    author_email='mousam.dahal4@gmail.com',
    url='https://github.com/leodahal4/django-health-metrics',
    packages=find_packages(exclude=['example', 'example.*']),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
        'prometheus-client',
        'psutil',
        'redis',
        'elasticsearch',
        'pika',
        'celery',
        'pymongo',
        'requests',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)