import time
from typing import List, Dict
import multiprocessing as mp
import subprocess
from pathlib import Path

import zmq
from loguru import logger

from utilities import Timer
from utilities_log import log_start

class ZMQMessage:
    def __init__(self, server:str=None, client:str=None, function:str=None, args:List[any]=None, kwargs:Dict[str, any]=None, return_:List[any]=None, status:str=None, times:List[any]=[], id_:int=None, dont_log_args:bool=False, dont_log_return:bool=False):
        self.server: str = server
        self.client: str = client
        self.function: str = function
        self.args: List[any] = [] if args is None else args
        self.kwargs: Dict[str, any] = {} if kwargs is None else kwargs
        self.return_: List[any] = [] if return_ is None else return_
        self.status: str = status
        self.times: List[int] = times
        self.id_: int = id_
        self.dont_log_args: bool = dont_log_args
        self.dont_log_return: bool = dont_log_return

    def __str__(self):
        dict = self.__dict__
        #*Remove hidden 
        if self.dont_log_args or self.dont_log_return:
            dict = dict.copy()

            if self.dont_log_args:
                dict['args'] = ['***']
                dict['kwargs'] = {'***': '***'}

            if self.dont_log_return:
                dict['return_'] = ['***']

        return str(dict)

class ZMQServer:
    def __init__(self, server_name='main', send_address='127.0.0.1', send_port=5555, recv_address='127.0.0.1', recv_port=5556) -> None:
        self.server_name = server_name
        self.client_dictionary = {}

        self.send_address = send_address
        self.send_port = send_port
        self.recv_address = recv_address
        self.recv_port = recv_port

        self._context = zmq.Context()

        self._pub_socket = self._context.socket(zmq.PUB)
        self._pub_socket.bind(f'tcp://{send_address}:{send_port}')

        self._sub_socket = self._context.socket(zmq.SUB)
        self._sub_socket.setsockopt(zmq.SUBSCRIBE, b"")
        self._sub_socket.bind(f'tcp://{recv_address}:{recv_port}')

        self.next_message_id = 0

    def send(self, client:str, function:str, args:List[any]=[], kwargs:Dict[str, any]={}, dont_log_args:bool=False):
        message = ZMQMessage(client=client, function=function, args=args, kwargs=kwargs, dont_log_args=dont_log_args)

        message.server = self.server_name
        message.times = [time.time()]
        message.id_ = self.next_message_id
        self.next_message_id = (self.next_message_id+1)%10000000

        self._pub_socket.send_json(message.__dict__)

        logger.trace('sent ' + str(message))

    def recv(self, timeout=10):
        if self._sub_socket.poll(timeout=timeout):
            message = ZMQMessage(**self._sub_socket.recv_json())

            message.times.append(time.time())

            logger.trace('recv ' + str(message))

            return message
        else:
            return ZMQMessage()#null message

    def recv_blocking(self, timeout=10):
        timeout_timer = Timer(timeout)
        while timeout_timer.running:
            message = self.recv()
            return message
        else:
            logger.error(f'Timed out waiting for response')

    def wait_for_function(self, client_wanted, function_wanted, timeout=10):
        timeout_timer = Timer(timeout)
        while timeout_timer.running:
            message = self.recv()
            if message.client == client_wanted and message.function == function_wanted:
                return message
        else:
            logger.error(f'Timed out waiting for response')

    def start_subprocess(self, executable, folder, process_name):
        path = Path(folder)
        executable_path = path / executable
        subprocess.Popen([executable_path], cwd=path)

        self.client_dictionary[process_name] = 'not_started'

    def start_multiprocess(self, multiprocess, process_name):
        process = mp.Process(target=multiprocess, args=(self.send_port, self.recv_port, process_name), daemon=True)
        process.start()

        self.client_dictionary[process_name] = 'not_started'

    def wait_for_all_clients_ready(self, timeout=10):
        ping_timer = Timer(1)
        timeout_timer = Timer(timeout)

        while timeout_timer.running:
            message = self.recv()

            if ping_timer.finished:
                ping_timer.reset()
                self.send('all', 'ping')

            if message.function == 'ping':
                if message.return_ == 'pong':
                    if message.status == 'loading':
                        self.client_dictionary[message.client] = 'loading'
                    elif message.status == 'success':
                        self.client_dictionary[message.client] = 'ready'

            if all([value == 'ready' for value in self.client_dictionary.values()]):
                break
        else:
            raise Exception(f'Timed out waiting for clients. {self.client_dictionary}')

    def close(self, timeout=10):
        timeout_timer = Timer(timeout)

        self.send('all', 'close')

        while timeout_timer.running:
            message = self.recv()

            if message.function == 'close':
                if message.status == 'success':
                    self.client_dictionary[message.client] = 'closed'#True means connected

            if all([value == 'closed' for value in self.client_dictionary.values()]):
                break
        else:
            raise Exception(f'Timed out waiting for clients. {self.client_dictionary}')
        
class StateMachine(ZMQServer):
    def __init__(self, server_name='main', send_address='127.0.0.1', send_port=5555, recv_address='127.0.0.1', recv_port=5556) -> None:
        log_start(server_name)
        self.state_name = 'init'
        try:
            super().__init__(server_name=server_name, send_address=send_address, send_port=send_port, recv_address=recv_address, recv_port=recv_port)
        except Exception:
            logger.exception('Initialization error.')

    def run(self):
        #*Set the first state to main state
        state = self.main_state
        args = ()
        kwargs = {}

        #*Continuously run the function (state) returned by each state as it finishes
        while True:
            try:
                logger.debug(f'Entering {state.__name__}')
                self.state_name = ' '.join(state.__name__.split('_')[:-1])

                #*Call the state
                return_ = state(*args, **kwargs)

                #*Get the next state if only one thing is returned
                if not isinstance(return_, tuple):
                    if return_ is None:
                        break
                    elif callable(return_):
                        state = return_

                #*Get the next state and args if return is a tuple
                else:
                    assert callable(return_[0])
                    state = return_[0]

                    #*Get the next args
                    if len(return_) < 2:
                        args = ()
                    else:
                        args = return_[1]
                        assert isinstance(args, tuple)

                    #*Get the next kwargs
                    if len(return_) < 3:
                        kwargs = {}
                    else:
                        kwargs = return_[2]
                        assert isinstance(args, dict)
                
            except Exception:
                if self.state_name == 'main state':
                    logger.exception('Critical state machine error.')
                    return None
                else:
                    logger.exception(f'Error in "{state.__name__}".')
                    state = self.main_state
                    args = ()
                    kwargs = {}

        logger.debug('Leaving run loop.')

    def main_state(self):
        raise NotImplementedError

    def close(self):
        super().close()

class ZMQClient:
    def __init__(self, recv_port=5555, send_port=5556, client_name='test', autorun=True) -> None:
        log_start(client_name)

        self._context = zmq.Context()

        self._pub_socket = self._context.socket(zmq.PUB)
        self._pub_socket.connect(f'tcp://localhost:{send_port}')

        self._sub_socket = self._context.socket(zmq.SUB)
        self._sub_socket.connect(f'tcp://localhost:{recv_port}')
        self._sub_socket.setsockopt(zmq.SUBSCRIBE, b"")

        self.client_name = client_name

        self.closed = False

        if autorun:
            self.run()

    def send(self, function:str=None, args:List[any]=[], kwargs:Dict[str, any]={}, status:str=None, dont_log_args:bool=False):
        message = ZMQMessage(function=function, args=args, kwargs=kwargs, status=status, dont_log_args=dont_log_args)

        message.client = self.client_name
        message.times = [time.time()]
        message.id_ = -1#this indicates a message originating from the client

        self._pub_socket.send_json(message.__dict__)

        logger.trace('sent ' + str(message))

    def recv(self, timeout=10):
        if self._sub_socket.poll(timeout=timeout):
            message = ZMQMessage(**self._sub_socket.recv_json())
            if message.client == self.client_name or message.client == 'all':
                if message.client == 'all':
                    message.client = self.client_name
                    
                message.times.append(time.time())

                logger.trace('recv ' + str(message))

                return message
            else:
                return ZMQMessage()
        else:
            return ZMQMessage()#null message

    def return_(self, message: ZMQMessage):
        message.times.append(time.time())

        self._pub_socket.send_json(message.__dict__)

        logger.trace('sent ' + str(message))

    def call(self, message: ZMQMessage):
        message.times.append(time.time())
        #*Get the function to call. This should send and log an attribute error if it fails
        try:
            function = getattr(self, message.function)
        except Exception:
            message.status = 'invalid_function'
        else:
            #*Call the function with or without arguments
            try:
                message.return_ = function(*message.args, **message.kwargs)
            except Exception:
                logger.exception(message.function)
                message.status = 'function_error'
            else:
                message.status = 'success'

        return message
    
    def run(self):
        try:
            while not self.closed:
                message = self.recv()
                if message.function:
                    message = self.call(message)
                    self.return_(message)
        except Exception as e:
            self.send(status='error', args=[str(e)])
            logger.exception('error')

    def ping(self):
        return 'pong'
    
    def close(self):
        self.closed = True
