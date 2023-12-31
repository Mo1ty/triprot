import time

from pydnp3 import opendnp3, openpal, asiopal, asiodnp3

LOG_LEVELS = opendnp3.levels.NORMAL | opendnp3.levels.ALL_COMMS
LOCAL_IP = "0.0.0.0"
PORT = 20000


class OutstationApplication(opendnp3.IOutstationApplication):
    outstation = None

    def __init__(self):
        super(OutstationApplication, self).__init__()

        print('Configuring the DNP3 stack.')
        self.stack_config = self.configure_stack()

        print('Configuring the outstation database.')
        self.configure_database(self.stack_config.dbConfig, 96)

        print('Creating a DNP3Manager.')
        threads_to_allocate = 1
        # self.log_handler = MyLogger()
        self.log_handler = asiodnp3.ConsoleLogger().Create()              # (or use this during regression testing)
        self.manager = asiodnp3.DNP3Manager(threads_to_allocate, self.log_handler)

        print('Creating the DNP3 channel, a TCP server.')
        self.retry_parameters = asiopal.ChannelRetry().Default()
        self.listener = AppChannelListener()
        # self.listener = asiodnp3.PrintingChannelListener().Create()       # (or use this during regression testing)
        self.channel = self.manager.AddTCPServer("server",
                                                 LOG_LEVELS,
                                                 self.retry_parameters,
                                                 LOCAL_IP,
                                                 PORT,
                                                 self.listener)

        print('Adding the outstation to the channel.')
        self.command_handler = OutstationCommandHandler()
        # self.command_handler =  opendnp3.SuccessCommandHandler().Create() # (or use this during regression testing)
        self.outstation = self.channel.AddOutstation("outstation", self.command_handler, self, self.stack_config)

        # Put the Outstation singleton in OutstationApplication so that it can be used to send updates to the Master.
        OutstationApplication.set_outstation(self.outstation)

        print('Enabling the outstation. Traffic will now start to flow.')
        self.outstation.Enable()

    @staticmethod
    def configure_stack():
        """Set up the OpenDNP3 configuration."""
        stack_config = asiodnp3.OutstationStackConfig(opendnp3.DatabaseSizes.AllTypes(100))
        stack_config.outstation.eventBufferConfig = opendnp3.EventBufferConfig().AllTypes(100)
        stack_config.outstation.params.allowUnsolicited = True
        stack_config.link.LocalAddr = 10
        stack_config.link.RemoteAddr = 1
        stack_config.link.KeepAliveTimeout = openpal.TimeDuration().Max()
        return stack_config

    @staticmethod
    def configure_database(db_config, number_of_points):
        """
            Configure the Outstation's database of input point definitions.

            Configure two Analog points (group/variation 30.1) at indexes 1 and 2.
        """

        # Set points with 32-bit signed integers
        for point_number in range(0, number_of_points):
            db_config.analog[point_number].clazz = opendnp3.PointClass.Class2
            db_config.analog[point_number].svariation = opendnp3.StaticAnalogVariation.Group30Var1
            db_config.analog[point_number].evariation = opendnp3.EventAnalogVariation.Group32Var7

    def shutdown(self):
        """
            Execute an orderly shutdown of the Outstation.

            The debug messages may be helpful if errors occur during shutdown.
        """
        # _log.debug('Exiting application...')
        # _log.debug('Shutting down outstation...')
        # OutstationApplication.set_outstation(None)
        # _log.debug('Shutting down stack config...')
        # self.stack_config = None
        # _log.debug('Shutting down channel...')
        # self.channel = None
        # _log.debug('Shutting down DNP3Manager...')
        # self.manager = None

        self.manager.Shutdown()

    @classmethod
    def get_outstation(cls):
        """Get the singleton instance of IOutstation."""
        return cls.outstation

    @classmethod
    def set_outstation(cls, outstn):
        """
            Set the singleton instance of IOutstation, as returned from the channel's AddOutstation call.

            Making IOutstation available as a singleton allows other classes (e.g. the command-line UI)
            to send commands to it -- see apply_update().
        """
        cls.outstation = outstn

    # Overridden method
    def ColdRestartSupport(self):
        """Return a RestartMode enumerated value indicating whether cold restart is supported."""
        print('In OutstationApplication.ColdRestartSupport')
        return opendnp3.RestartMode.UNSUPPORTED

    # Overridden method
    def GetApplicationIIN(self):
        """Return the application-controlled IIN field."""
        application_iin = opendnp3.ApplicationIIN()
        application_iin.configCorrupt = False
        application_iin.deviceTrouble = False
        application_iin.localControl = False
        application_iin.needTime = False
        # Just for testing purposes, convert it to an IINField and display the contents of the two bytes.
        iin_field = application_iin.ToIIN()
        print('OutstationApplication.GetApplicationIIN: IINField LSB={}, MSB={}'.format(iin_field.LSB,
                                                                                             iin_field.MSB))
        return application_iin

    # Overridden method
    def SupportsAssignClass(self):
        print('In OutstationApplication.SupportsAssignClass')
        return False

    # Overridden method
    def SupportsWriteAbsoluteTime(self):
        print('In OutstationApplication.SupportsWriteAbsoluteTime')
        return False

    # Overridden method
    def SupportsWriteTimeAndInterval(self):
        print('In OutstationApplication.SupportsWriteTimeAndInterval')
        return False

    # Overridden method
    def WarmRestartSupport(self):
        """Return a RestartMode enumerated value indicating whether a warm restart is supported."""
        print('In OutstationApplication.WarmRestartSupport')
        return opendnp3.RestartMode.UNSUPPORTED

    @classmethod
    def process_point_value(cls, command_type, command, index, op_type):
        """
            A PointValue was received from the Master. Process its payload.

        :param command_type: (string) Either 'Select' or 'Operate'.
        :param command: A ControlRelayOutputBlock or else a wrapped data value (AnalogOutputInt16, etc.).
        :param index: (integer) DNP3 index of the payload's data definition.
        :param op_type: An OperateType, or None if command_type == 'Select'.
        """

        print('Processing received point value for index {}: {}'.format(index, command.value))

    def apply_update(self, value, index):
        """
            Record an opendnp3 data value (Analog, Binary, etc.) in the outstation's database.

            The data value gets sent to the Master as a side-effect.

        :param value: An instance of Analog, Binary, or another opendnp3 data value.
        :param index: (integer) Index of the data definition in the opendnp3 database.
        """
        print('Recording {} measurement, index={}, value={}'.format(type(value).__name__, index, value.value))
        builder = asiodnp3.UpdateBuilder()
        builder.Update(value, index)
        update = builder.Build()
        OutstationApplication.get_outstation().Apply(update)


class OutstationCommandHandler(opendnp3.ICommandHandler):
    """
        Override ICommandHandler in this manner to implement application-specific command handling.

        ICommandHandler implements the Outstation's handling of Select and Operate,
        which relay commands and data from the Master to the Outstation.
    """

    def Start(self):
        print('In OutstationCommandHandler.Start')

    def End(self):
        print('In OutstationCommandHandler.End')

    def Select(self, command, index):
        """
            The Master sent a Select command to the Outstation. Handle it.

        :param command: ControlRelayOutputBlock,
                        AnalogOutputInt16, AnalogOutputInt32, AnalogOutputFloat32, or AnalogOutputDouble64.
        :param index: int
        :return: CommandStatus
        """
        OutstationApplication.process_point_value('Select', command, index, None)
        return opendnp3.CommandStatus.SUCCESS

    def Operate(self, command, index, op_type):
        """
            The Master sent an Operate command to the Outstation. Handle it.

        :param command: ControlRelayOutputBlock,
                        AnalogOutputInt16, AnalogOutputInt32, AnalogOutputFloat32, or AnalogOutputDouble64.
        :param index: int
        :param op_type: OperateType
        :return: CommandStatus
        """
        OutstationApplication.process_point_value('Operate', command, index, op_type)
        return opendnp3.CommandStatus.SUCCESS


class AppChannelListener(asiodnp3.IChannelListener):
    """
        Override IChannelListener in this manner to implement application-specific channel behavior.
    """

    def __init__(self):
        super(AppChannelListener, self).__init__()

    def OnStateChange(self, state):
        print('In AppChannelListener.OnStateChange: state={}'.format(state))


def start_outstation():
    """The Outstation has been started from the command line. Execute ad-hoc tests if desired."""
    app = OutstationApplication()
    print('Initialization complete. In command loop.')

    while app:
        print("App started. Server up.")
        time.sleep(7)

    app.shutdown()
    print('Exiting.')
    exit()
