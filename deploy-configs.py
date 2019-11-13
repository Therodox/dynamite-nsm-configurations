import os
import boto3
import tarfile
import argparse
from configparser import ConfigParser
config = ConfigParser()

config.read('config.cfg')


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir)


def upload_file(fh, bucket, directory, filename):

    s3 = boto3.client('s3', aws_access_key_id=config['AWS']['aws_access_key_id'],
                      aws_secret_access_key=config['AWS']['aws_secret_access_key'])
    if filename is None:
        filename = fh.name.split("/")[-1]
    else:
        filename = filename
    file_key = os.path.join(directory, filename)

    s3.upload_fileobj(fh, bucket, file_key, ExtraArgs={'ACL': 'public-read'})


def copy_to_latest(filename, bucket, directory):
    s3 = boto3.resource('s3', aws_access_key_id=config['AWS']['aws_access_key_id'],
                      aws_secret_access_key=config['AWS']['aws_secret_access_key'])
    basepath = directory.split('/')[-2]
    s3.meta.client.copy(
        {
            'Bucket': bucket,
            'Key': os.path.join(directory, filename)
        },
        bucket,
        os.path.join(basepath, 'latest', filename),
        ExtraArgs={'ACL': 'public-read'}
    )


def get_public_versions():
    versions = set()
    s3 = boto3.client('s3', aws_access_key_id=config['AWS']['aws_access_key_id'],
                      aws_secret_access_key=config['AWS']['aws_secret_access_key'])
    for key in s3.list_objects(Bucket='dynamite-config-staging', Prefix='dynamite-public')['Contents']:
        key = key['Key'].split('/')
        if len(key) != 3:
            continue
        try:
            versions.add(float(key[1]))
        except ValueError:
            continue

    return list(versions)


def get_pro_versions():
    versions = set()
    s3 = boto3.client('s3', aws_access_key_id=config['AWS']['aws_access_key_id'],
                      aws_secret_access_key=config['AWS']['aws_secret_access_key'])
    for key in s3.list_objects(Bucket='dynamite-config-staging', Prefix='dynamite-pro')['Contents']:
        key = key['Key'].split('/')
        if len(key) != 3:
            continue
        try:
            versions.add(float(key[1]))
        except ValueError:
            continue

    return list(versions)


def upload_to_public(default_configs_directory, mirrors_directory, version, overwrite=False):
    existing_versions = get_public_versions()
    if not overwrite:
        if float(version) in existing_versions:
            print('A version of this number already exists.')
            return
        if existing_versions:
            if float(version) < max(existing_versions):
                print('The version given must be greater than {}'.format(max(existing_versions)))
                return

    print('Building compressed TAR files...')
    make_tarfile('default_configs-{}.tar.gz'.format(version), default_configs_directory)
    def_config_tar_fh = open('default_configs-{}.tar.gz'.format(version), 'rb')
    make_tarfile('mirrors-{}.tar.gz'.format(version), mirrors_directory)
    mirrors_tar_fh = open('mirrors-{}.tar.gz'.format(version), 'rb')
    print('Uploading Default Configs...')
    upload_file(
        def_config_tar_fh,
        'dynamite-config-staging',
        'dynamite-public/{}'.format(version),
        'default_configs.tar.gz'
    )
    copy_to_latest(
        'default_configs.tar.gz',
        'dynamite-config-staging',
        'dynamite-public/{}'.format(version)
    )
    print('Uploading Mirror Configs...')
    upload_file(
        mirrors_tar_fh,
        'dynamite-config-staging',
        'dynamite-public/{}'.format(version),
        'mirrors.tar.gz'
    )
    copy_to_latest(
        'mirrors.tar.gz',
        'dynamite-config-staging',
        'dynamite-public/{}'.format(version)
    )

    print('''

    COMPLETE!

    Configurations can now be downloaded from:
     - https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-public/latest/default_configs.tar.gz
     - https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-public/latest/mirrors.tar.gz

     AND

     - https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-public/{}/default_configs.tar.gz
     - https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-public/{}/mirrors.tar.gz
    '''.format(version, version))


def upload_to_pro(default_configs_directory, mirrors_directory, version, overwrite=False):
    existing_versions = get_pro_versions()
    if not overwrite:
        if float(version) in existing_versions:
            print('A version of this number already exists.')
            return
        if existing_versions:
            if float(version) < max(existing_versions):
                print('The version given must be greater than {}'.format(max(existing_versions)))
                return
    print('Building compressed TAR files...')
    make_tarfile('default_configs-{}.tar.gz'.format(version), default_configs_directory)
    def_config_tar_fh = open('default_configs-{}.tar.gz'.format(version), 'rb')
    make_tarfile('mirrors-{}.tar.gz'.format(version), mirrors_directory)
    mirrors_tar_fh = open('mirrors-{}.tar.gz'.format(version), 'rb')
    print('Uploading Default Configs...')
    upload_file(
        def_config_tar_fh,
        'dynamite-config-staging',
        'dynamite-pro/{}'.format(version),
        'default_configs.tar.gz'
    )
    copy_to_latest(
        'default_configs.tar.gz',
        'dynamite-config-staging',
        'dynamite-pro/{}'.format(version)
    )
    print('Uploading Mirror Configs...')
    upload_file(
        mirrors_tar_fh,
        'dynamite-config-staging',
        'dynamite-pro/{}'.format(version),
        'mirrors.tar.gz'
    )
    copy_to_latest(
        'mirrors.tar.gz',
        'dynamite-config-staging',
        'dynamite-pro/{}'.format(version)
    )

    print('''
    
    COMPLETE!
    
    Configurations can now be downloaded from:
     - https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-pro/latest/default_configs.tar.gz
     - https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-pro/latest/mirrors.tar.gz
     
     AND
     
     - https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-pro/{}/default_configs.tar.gz
     - https://dynamite-config-staging.s3-us-west-2.amazonaws.com/dynamite-pro/{}/mirrors.tar.gz
    '''.format(version, version))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Upload DynamiteNSM public/pro configurations to S3 staging environment.'
        )

    parser.add_argument('default_configs_directory', metavar='default_configs_directory', type=str,
                        help='The path to the default_configs directory')

    parser.add_argument('mirrors_directory', metavar='mirrors_directory', type=str,
                        help='The path to the mirrors directory')
    parser.add_argument('version', metavar='version', type=float,
                        help='The corresponding dynamite-nsm version')
    parser.add_argument('--dynamite-pro', default=False, dest='dynamite_pro', action='store_true',
                        help='Upload to Dynamite Pro staging environment instead of public.')
    parser.add_argument('--overwrite', default=False, dest='overwrite', action='store_true',
                        help='If true overwrites an old version if one is specified.')

    args = parser.parse_args()

    if args.dynamite_pro:
        print('Uploaded Pro Versions: {}'.format(', '.join([str(v) for v in get_pro_versions()])))
        upload_to_pro(args.default_configs_directory, args.mirrors_directory, args.version, args.overwrite)
    else:
        print('Uploaded Public Versions: {}'.format(', '.join([str(v) for v in get_public_versions()])))
        upload_to_public(args.default_configs_directory, args.mirrors_directory, args.version, args.overwrite)



