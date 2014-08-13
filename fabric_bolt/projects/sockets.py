import logging
import sys
import subprocess
from threading import Thread
import time
import fcntl
import os

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace

from .util import build_command
from fabric_bolt.projects.models import Deployment


@namespace('/deployment')
class DeployNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):

    def initialize(self):
        self.logger = logging.getLogger("socketio.deployment")
        self.log("Socketio session started")
        self.threads = {}

    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))

    def on_join(self, deployment_id):
        self.deployment = Deployment.objects.get(pk=deployment_id)
        if self.deployment.status == self.deployment.PENDING:
            update_thread = Thread(target=self.output_stream_generator, args=(self,))
            update_thread.daemon = True
            update_thread.start()
            self.threads[deployment_id] = update_thread

        return True

    def on_input(self, text):
        try:
            self.process.stdin.write(text + '\n')
            return True
        except:
            return False

    def recv_disconnect(self):
        self.log('Disconnected')
        self.disconnect(silent=True)
        return True

    def output_stream_generator(self, *args, **kwargs):
        cmd = build_command(self.deployment, self.request.session, False),

        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=True
        )

        fd = self.process.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        all_output = ''
        while True:
            try:
                nextline = self.process.stdout.read()
            except IOError:
                nextline = ''

            if nextline == '' and self.process.poll() != None:
                break

            all_output += nextline

            if nextline:
                self.broadcast_event('output', {'status': 'pending', 'lines': str(nextline)})
            time.sleep(0.00001)

            sys.stdout.flush()

        self.deployment.status = self.deployment.SUCCESS if self.process.returncode == 0 else self.deployment.FAILED


        self.deployment.output = all_output
        self.deployment.save()

        print "Broadcasting status {}".format(self.deployment.status)
        self.broadcast_event('output', {'status': self.deployment.status})

        # self.disconnect()

        # all_output = ''
        # while self.process.poll() is None:
        #     try:
        #         nextline = self.process.stdout.readline()
        #         if nextline == '':
        #             break

        #         self.broadcast_event('output', {'status': 'pending', 'lines': str(nextline)})
        #         all_output += str(nextline)
        #         sys.stdout.flush()

        #     except IOError:
        #         print "Got an IO error?"
        #         break

        # print "Exited with: {}".format(self.process.returncode)
        # self.deployment.status = self.deployment.SUCCESS if self.process.returncode == 0 else self.deployment.FAILED

        # self.deployment.output = all_output
        # self.deployment.save()

        # print "Broadcasting status {}".format(self.deployment.status)
        # self.broadcast_event('output', {'status': self.deployment.status})

        # self.disconnect()
