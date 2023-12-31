import time

from pydnp3 import opendnp3, openpal, asiopal, asiodnp3
from dnp3_python.dnp3station.visitors  import *
from pydnp3.opendnp3 import CommandSet, AnalogOutputInt32, IndexedAnalogOutputInt32

FILTERS = opendnp3.levels.NORMAL | opendnp3.levels.ALL_COMMS
LOCAL = "0.0.0.0"
PORT = 20000


class MyMaster:
    def __init__(self,
                 dnp3_host,
                 log_handler=asiodnp3.ConsoleLogger().Create(),
                 listener=asiodnp3.PrintingChannelListener().Create(),
                 soe_handler=asiodnp3.PrintingSOEHandler().Create(),
                 master_application=asiodnp3.DefaultMasterApplication().Create(),
                 stack_config=None):

        print('Creating a DNP3Manager.')
        self.log_handler = log_handler
        self.manager = asiodnp3.DNP3Manager(1, self.log_handler)

        print('Creating the DNP3 channel, a TCP client.')
        self.retry = asiopal.ChannelRetry().Default()
        self.listener = listener
        self.channel = self.manager.AddTCPClient("tcpclient",
                                        FILTERS,
                                        self.retry,
                                        dnp3_host,
                                        LOCAL,
                                        PORT,
                                        self.listener)

        print('Configuring the DNP3 stack.')
        self.stack_config = stack_config
        if not self.stack_config:
            self.stack_config = asiodnp3.MasterStackConfig()
            self.stack_config.master.responseTimeout = openpal.TimeDuration().Seconds(2)
            self.stack_config.link.RemoteAddr = 10

        print('Adding the master to the channel.')
        self.soe_handler = soe_handler
        self.master_application = master_application
        self.master = self.channel.AddMaster("master",
                                   asiodnp3.PrintingSOEHandler().Create(),
                                   self.master_application,
                                   self.stack_config)

        print('Configuring some scans (periodic reads).')
        # Set up a "slow scan", an infrequent integrity poll that requests events and static data for all classes.
        self.slow_scan = self.master.AddClassScan(opendnp3.ClassField().AllClasses(),
                                                  openpal.TimeDuration().Minutes(30),
                                                  opendnp3.TaskConfig().Default())
        # Set up a "fast scan", a relatively-frequent exception poll that requests events and class 1 static data.
        self.fast_scan = self.master.AddClassScan(opendnp3.ClassField(opendnp3.ClassField.CLASS_1),
                                                  openpal.TimeDuration().Minutes(1),
                                                  opendnp3.TaskConfig().Default())

        self.channel.SetLogFilters(openpal.LogFilters(opendnp3.levels.ALL_COMMS))
        self.master.SetLogFilters(openpal.LogFilters(opendnp3.levels.ALL_COMMS))

        print('Enabling the master. At this point, traffic will start to flow between the Master and Outstations.')
        self.master.Enable()
        time.sleep(5)

    def send_direct_operate_command(self, command, index, callback=asiodnp3.PrintingCommandCallback.Get(),
                                    config=opendnp3.TaskConfig().Default()):
        """
            Direct operate a single command

        :param command: command to operate
        :param index: index of the command
        :param callback: callback that will be invoked upon completion or failure
        :param config: optional configuration that controls normal callbacks and allows the user to be specified for SA
        """
        self.master.DirectOperate(command, index, callback, config)

    def send_direct_operate_command_set(self, command_set, callback=asiodnp3.PrintingCommandCallback.Get(),
                                        config=opendnp3.TaskConfig().Default()):
        """
            Direct operate a set of commands

        :param command_set: set of command headers
        :param callback: callback that will be invoked upon completion or failure
        :param config: optional configuration that controls normal callbacks and allows the user to be specified for SA
        """
        self.master.DirectOperate(command_set, callback, config)

    def send_select_and_operate_command(self, command, index, callback=asiodnp3.PrintingCommandCallback.Get(),
                                        config=opendnp3.TaskConfig().Default()):
        """
            Select and operate a single command

        :param command: command to operate
        :param index: index of the command
        :param callback: callback that will be invoked upon completion or failure
        :param config: optional configuration that controls normal callbacks and allows the user to be specified for SA
        """
        self.master.SelectAndOperate(command, index, callback, config)

    def send_select_and_operate_command_set(self, command_set, callback=asiodnp3.PrintingCommandCallback.Get(),
                                            config=opendnp3.TaskConfig().Default()):
        """
            Select and operate a set of commands

        :param command_set: set of command headers
        :param callback: callback that will be invoked upon completion or failure
        :param config: optional configuration that controls normal callbacks and allows the user to be specified for SA
        """
        self.master.SelectAndOperate(command_set, callback, config)

    def shutdown(self):
        del self.slow_scan
        del self.fast_scan
        del self.master
        del self.channel
        self.manager.Shutdown()


class MyLogger(openpal.ILogHandler):
    """
        Override ILogHandler in this manner to implement application-specific logging behavior.
    """

    def __init__(self):
        super(MyLogger, self).__init__()

    def Log(self, entry):
        flag = opendnp3.LogFlagToString(entry.filters.GetBitfield())
        filters = entry.filters.GetBitfield()
        location = entry.location.rsplit('/')[-1] if entry.location else ''
        message = entry.message
        print('LOG\t\t{:<10}\tfilters={:<5}\tlocation={:<25}\tentry={}'.format(flag, filters, location, message))


class AppChannelListener(asiodnp3.IChannelListener):
    """
        Override IChannelListener in this manner to implement application-specific channel behavior.
    """

    def __init__(self):
        super(AppChannelListener, self).__init__()

    def OnStateChange(self, state):
        print('In AppChannelListener.OnStateChange: state={}'.format(opendnp3.ChannelStateToString(state)))


class SOEHandler(opendnp3.ISOEHandler):
    """
        Override ISOEHandler in this manner to implement application-specific sequence-of-events behavior.

        This is an interface for SequenceOfEvents (SOE) callbacks from the Master stack to the application layer.
    """

    def __init__(self):
        super(SOEHandler, self).__init__()

    def Process(self, info, values):
        """
            Process measurement data.

        :param info: HeaderInfo
        :param values: A collection of values received from the Outstation (various data types are possible).
        """
        visitor_class_types = {
            opendnp3.ICollectionIndexedBinary: VisitorIndexedBinary,
            opendnp3.ICollectionIndexedDoubleBitBinary: VisitorIndexedDoubleBitBinary,
            opendnp3.ICollectionIndexedCounter: VisitorIndexedCounter,
            opendnp3.ICollectionIndexedFrozenCounter: VisitorIndexedFrozenCounter,
            opendnp3.ICollectionIndexedAnalog: VisitorIndexedAnalog,
            opendnp3.ICollectionIndexedBinaryOutputStatus: VisitorIndexedBinaryOutputStatus,
            opendnp3.ICollectionIndexedAnalogOutputStatus: VisitorIndexedAnalogOutputStatus,
            opendnp3.ICollectionIndexedTimeAndInterval: VisitorIndexedTimeAndInterval
        }
        visitor_class = visitor_class_types[type(values)]
        visitor = visitor_class()
        values.Foreach(visitor)
        for index, value in visitor.index_and_value:
            print_string = 'SOEHandler.Process {0}\theaderIndex={1}\tdata_type={2}\tindex={3}\tvalue={4}'
            print(print_string.format(info.gv, info.headerIndex, type(values).__name__, index, value))

    def Start(self):
        print('In SOEHandler.Start')

    def End(self):
        print('In SOEHandler.End')


class MasterApplication(opendnp3.IMasterApplication):
    def __init__(self):
        super(MasterApplication, self).__init__()

    # Overridden method
    def AssignClassDuringStartup(self):
        print('In MasterApplication.AssignClassDuringStartup')
        return False

    # Overridden method
    def OnClose(self):
        print('In MasterApplication.OnClose')

    # Overridden method
    def OnOpen(self):
        print('In MasterApplication.OnOpen')

    # Overridden method
    def OnReceiveIIN(self, iin):
        print('In MasterApplication.OnReceiveIIN')

    # Overridden method
    def OnTaskComplete(self, info):
        print('In MasterApplication.OnTaskComplete')

    # Overridden method
    def OnTaskStart(self, type, id):
        print('In MasterApplication.OnTaskStart')


def collection_callback(result=None):
    """
    :type result: opendnp3.CommandPointResult
    """
    print("Header: {0} | Index:  {1} | State:  {2} | Status: {3}".format(
        result.headerIndex,
        result.index,
        opendnp3.CommandPointStateToString(result.state),
        opendnp3.CommandStatusToString(result.status)
    ))


def command_callback(result=None):
    """
    :type result: opendnp3.ICommandTaskResult
    """
    print("Received command result with summary: {}".format(opendnp3.TaskCompletionToString(result.summary)))
    result.ForeachItem(collection_callback)


def restart_callback(result=opendnp3.RestartOperationResult()):
    if result.summary == opendnp3.TaskCompletion.SUCCESS:
        print("Restart success | Restart Time: {}".format(result.restartTime.GetMilliseconds()))
    else:
        print("Restart fail | Failure: {}".format(opendnp3.TaskCompletionToString(result.summary)))


def write_data_to_points(register_info, app):
    command_headers = []
    for info in range(0, len(register_info)):
        command_headers.append(IndexedAnalogOutputInt32(AnalogOutputInt32(value=register_info[info]), info))

    command_set = CommandSet(command_headers)
    app.send_select_and_operate_command_set(command_set)


def start_master(dnp3_host="127.0.0.1", register_info=None):

    if register_info is None:
        return

    """Main method used by app to start application"""
    app = MyMaster(dnp3_host,
                   log_handler=MyLogger(),
                   listener=AppChannelListener(),
                   soe_handler=SOEHandler(),
                   master_application=MasterApplication())
    print('Initialization complete. In command loop.')

    # Transmit info to VM 3
    write_data_to_points(register_info, app)

    while app:
        time.sleep(3)
    # Ad-hoc tests can be performed at this point. See master_cmd.py for examples.
    app.shutdown()
    print('Exiting.')
    exit()


