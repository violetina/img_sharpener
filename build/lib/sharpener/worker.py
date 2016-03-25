import datetime
import pika
import logging
import os
from pika.credentials import PlainCredentials
from pip import logger

from .rabbit_publisher import send_message
from json import loads, dumps
from .convertor import convert
import subprocess
# from subprocess import check_output, STDOUT


from os.path import join
import logging

def validate_message(params):
    mandatory_keys = [
        'correlation_id',
        'source_server',
        'source_path',
        'destination_server',
        'destination_path',
        'destination_file',
        'level',
        'source_user',
        'destination_user'

    ]

    message_valid = True

    for key in mandatory_keys:
        #try:
          if key not in params:
            message_valid = False
            logging.error('{} is missing from received message'.format(key))
        #except BaseException as e:
        #    logger.exception('ERROR: source_user is missing from received message' + str(e))

    return message_valid



class Consumer:
    def __init__(self, arguments):
        self.host = arguments.broker_ip
        self.port = arguments.broker_port
        self.username = arguments.username
        self.password = arguments.password
        self.queue = arguments.incoming_queue
        self.result_exchange = arguments.result_exchange
        self.result_routing = arguments.result_routing
        self.result_queue = arguments.result_queue
        self.topic_type = arguments.topic_type
        self.file_permission = 0o770
        self.user = ''
        self.group = ''


    def consume(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=PlainCredentials(self.username, self.password)
        ))

        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)
        channel.basic_consume(self.callback, self.queue)
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        try:
            status = 'OK'
            details = 'file successfully converted'
            convert_params = loads(body.decode("utf-8"))
            if validate_message(convert_params):
                try:
                    destination_user = convert_params['destination_user']
                    if not destination_user:
                        destination_user = 'tcochet'
                    source_user = convert_params['source_user']
                    if not source_user:
                        source_user = 'tcochet'

                    source_file_path = join(convert_params['source_path'], convert_params['source_file'])
                    dest_file_path = join(convert_params['destination_path'], convert_params['destination_file'])
                    level = convert_params['level']
                    temp_dir_dest = '/mnt/dest'
                    temp_dir = '/mnt/source'
                    self.supermakedirs(temp_dir_dest)
                    self.supermakedirs(temp_dir)
                    if convert_params['destination_server']:
                        fs_dest = convert_params['destination_path']
                        host_dest = convert_params['destination_server']

                        path_dest = os.path.dirname(temp_dir_dest)
                        self.supermakedirs(path_dest)
                        if not os.path.ismount(path_dest):
                            logging.info("starting mount of destination server %s" % host_dest)
                            subprocess.call(["sshfs -o default_permissions -o nonempty -o allow_other  %s@%s:%s %s" % (
                                destination_user, host_dest, fs_dest, temp_dir_dest)], shell=True)
                            dest_file_path_dest = join(temp_dir_dest, convert_params['destination_file'])
                            dest_file_path = dest_file_path_dest
                            mounted_filepath = join(temp_dir_dest, convert_params['destination_file'])
                            mounted_path_dest = os.path.dirname(mounted_filepath)
                            logging.info("destfilepath %s" % dest_file_path_dest)
                            logging.info("destination dir wil be made if not exists: %s" % mounted_path_dest)
                            self.supermakedirs(mounted_path_dest)

                        else:
                            logging.info('already mounted')

                    if convert_params['source_server']:
                        fs = convert_params['source_path']
                        host = convert_params['source_server']
                        path = os.path.dirname(temp_dir)
                        self.supermakedirs(path)
                        if not os.path.ismount(path):
                            logging.info("starting mount of source server %s" % host)
                            subprocess.call(["sshfs -o default_permissions -o nonempty -o allow_other  %s@%s:%s %s" % (
                                source_user, host, fs, temp_dir)], shell=True)
                            source_file_path = join(temp_dir, convert_params['source_file'])
                            mounted_file_path_source = join(temp_dir, convert_params['source_file'])
                            mounted_path_source = os.path.dirname(mounted_file_path_source)
                            logging.info("sourcefilepath %s" % source_file_path)
                            logging.info("source dir wil be made if not exists: %s" % mounted_path_source)
                            self.supermakedirs(mounted_path_source)
                        else:
                            logging.info('already mounted')

                    else:
                        logging.info('no source_server defiend ignoring')
                        path = os.path.dirname(convert_params['destination_path'])
                        self.supermakedirs(path)
                        if os.path.exists(convert_params['destination_path']) and os.path.isfile(
                            convert_params['destination_path']):
                            os.remove(convert_params['destination_path'])

                    convert(source_file_path, level, dest_file_path)
                    if os.path.ismount(temp_dir):
                        logging.info("unmounting %s" % temp_dir)
                        subprocess.call(["fusermount -u %s" % (temp_dir)], shell=True)
                    if os.path.ismount(temp_dir_dest):
                        logging.info("unmounting %s" % temp_dir_dest)
                        subprocess.call(["fusermount -u %s" % (temp_dir_dest)], shell=True)

                except Exception as e:
                    status = 'NOK'
                    details = str(e)

                except Exception as e:
                    status = 'NOK'
                    if type(e).__name__ == 'CalledProcessError':
                        details = str(e.output.decode("utf-8"))
                    else:
                        details = str(type(e)) + ":" + str(e)

                message = {
                    "correlation_id": convert_params["correlation_id"],
                    "status": status,
                    "details": details,
                    "destination_server": convert_params["destination_server"],
                    "destination_path": convert_params["destination_path"],
                    "destination_file": convert_params["destination_file"],
                    "level": convert_params["level"],
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                json_message = dumps(message)
                logging.info(json_message)

                send_message(
                    self.host,
                    self.port,
                    self.username,
                    self.password,
                    self.result_exchange,
                    self.result_routing,
                    self.result_queue,
                    self.topic_type,
                    json_message
                )
            else:
                logging.error('Message invalid: {}'.format(convert_params))

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logging.error(str(e))

    def supermakedirs(self, path):
        try:
            if not path or os.path.exists(path):
                stat_info = os.stat(path)
                uid = stat_info.st_uid
                gid = stat_info.st_gid
                self.user = uid
                self.group = gid
                logging.debug('Found: {} - {} - {}'.format(self.user, self.group, path))
                # Break recursion
                return []
            (head, tail) = os.path.split(path)
            res = self.supermakedirs(head)
            os.mkdir(path)
            os.chmod(path, self.file_permission)
            os.chown(path, self.user, self.group)
            logging.debug('Created: {} - {} - {}'.format(self.user, self.group, path))
            res += [path]
            return res
        except OSError as e:
            if e.errno == 17:
                logging.debug('Directory existed when creating. Ignoring')
                res += [path]
                return res
            raise
