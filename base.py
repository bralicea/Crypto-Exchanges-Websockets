from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
import sys
from twisted.python import log
from twisted.internet import reactor, ssl, task, asyncioreactor
from twisted.internet.protocol import ReconnectingClientFactory
import json
from urllib.parse import urlparse
import zlib
import psycopg2
import ast
import time
from datetime import datetime
from kafka import KafkaProducer


class Base(WebSocketClientProtocol):

    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))

        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed .. retrying ..")
        self.retry(connector)
        self.resetDelay()

    def clientConnectionLost(self, connector, reason):
        print("Client connection lost .. retrying ..")
        self.retry(connector)
        self.resetDelay()


class Connect(WebSocketClientFactory, ReconnectingClientFactory):

    pass


def createConnection(streamName, port, exchange): # Create a Twisted factory
    log.startLogging(sys.stdout)
    hostName = urlparse(streamName).hostname
    factory = Connect(streamName)
    factory.setProtocolOptions(autoPingInterval=60)
    factory.protocol = exchange
    reactor.connectSSL(hostName, port, factory, ssl.ClientContextFactory())
