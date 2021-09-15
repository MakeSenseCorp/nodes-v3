function Application() {
    var self = this;
    // Get makesense api instanse.
    this.API = MkSAPIBuilder.GetInstance();
    // Default handler
    this.API.OnUnexpectedDataArrived = function (packet) {
        console.log(packet);
    }
    this.API.ModulesLoadedCallback = function () {
        self.NodeLoaded();
    }
    this.EventMapper = {};
    this.Adaptor = new Pidaptor(this.API);
    this.Terminal = new Piterm(this.API);
    window.ApplicationModules.Modal = new MksBasicModal("GLOBAL");

    return this;
}
Application.prototype.RegisterEventHandler = function(name, callback, scope) {
    this.EventMapper[name] = { 
        callback: callback,
        scope: scope
    };
}
Application.prototype.UnregisterEventHandler = function(name) {
    delete this.EventMapper[name];
}
Application.prototype.Publish = function(name, data) {
    var handler  = this.EventMapper[name];
    if (handler !== undefined && handler !== null) {
        handler.callback(data, handler.scope);
    }
}
Application.prototype.Connect = function(ip, port, callback) {
    var self = this;
    console.log("Connect Application");
    // Python will emit messages
    self.API.OnNodeChangeCallback = self.OnChangeEvent.bind(self);
    this.API.ConnectLocalWS(ip, port, function() {
        console.log("Connected to local websocket");

        // Module area
        self.API.AppendModule("ModuleDashboardView");
        self.API.AppendModule("ModuleGatewayView");
        self.API.AppendModule("ModuleNodeView");
        self.API.AppendModule("ModuleSensorView");
        self.API.GetModules();

        callback();
    });
}
Application.prototype.NodeLoaded = function () {
    console.log("Modules Loaded");

    window.ApplicationModules.DashboardView = new ModuleDashboardView();
    window.ApplicationModules.DashboardView.SetHostingID("id_application_view_module");
    window.ApplicationModules.DashboardView.SetObjectDOMName("window.ApplicationModules.DashboardView");
    window.ApplicationModules.DashboardView.Build(null, function(module) {});	

}
Application.prototype.OnChangeEvent = function(packet) {
    var event = packet.payload.event;
    var data = packet.payload.data;
    this.Publish(event, data);
}
// ASYNC REGISTERED HANDLERS
Application.prototype.SystemInfoHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SerialListHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetNodeListHandler = function(data, scope) {
    if (data === undefined || data === null) {
        return;
    }

    window.ApplicationModules.DashboardView.GetDevicesEvent(data.list);
}
Application.prototype.GetRemoteNodeInfoHandler = function(data, scope) {
    window.ApplicationModules.DashboardView.NRFDataEvent(data);
}
Application.prototype.GetRemoteNodeDataHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SetRemoteNodeDataHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetDeviceTypeHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetDeviceAdditionalHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SetNodeAddressHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetNodeAddressHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetNodeInfoHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GetNodesMapHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.AddNodeIndexHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.DelNodeIndexHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SetRemoteNodeAddressHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.DelNodeIndexHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.USBDeviceConnectedHandler = function(data, scope) {
    window.ApplicationModules.DashboardView.USBDeviceConnectedEvent(data);
}
Application.prototype.USBDeviceDisconnectedHandler = function(data, scope) {
    window.ApplicationModules.DashboardView.USBDeviceDisconnectedEvent(data);
}
Application.prototype.SetWorkingPortHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.GatewayInfoHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.NRFPacket = function(data, scope) {
    window.ApplicationModules.DashboardView.NRFDataEvent(data);
}
Application.prototype.InsertDeviceHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SelectSensorsHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.DeleteDeviceHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SelectDevicesHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.UpdateSensorInfoHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.DeviceCommunicationLostHandler = function(data, scope) {
    window.ApplicationModules.DashboardView.DeviceConnectionLostEvent(data);
}
Application.prototype.SelectSensorsByDeviceHandler = function(data, scope) {
    console.log(data);
}
Application.prototype.SelectSensorHistoryHandler = function(data, scope) {
    console.log(data);
}

var app = new Application();
app.RegisterEventHandler("SelectSensorHistoryHandler",      app.SelectSensorHistoryHandler,     app);
app.RegisterEventHandler("SelectSensorsByDeviceHandler",    app.SelectSensorsByDeviceHandler,   app);
app.RegisterEventHandler("DeviceCommunicationLostHandler",  app.DeviceCommunicationLostHandler, app);
app.RegisterEventHandler("UpdateSensorInfoHandler",         app.UpdateSensorInfoHandler,        app);
app.RegisterEventHandler("SelectDevicesHandler",            app.SelectDevicesHandler,           app);
app.RegisterEventHandler("DeleteDeviceHandler",             app.DeleteDeviceHandler,            app);
app.RegisterEventHandler("SelectSensorsHandler",            app.SelectSensorsHandler,           app);
app.RegisterEventHandler("InsertDeviceHandler",             app.InsertDeviceHandler,            app);
app.RegisterEventHandler("NRFPacket",                       app.NRFPacket,                      app);
app.RegisterEventHandler("SystemInfoHandler",               app.SystemInfoHandler,              app);
app.RegisterEventHandler("GatewayInfoHandler",              app.GatewayInfoHandler,             app);
app.RegisterEventHandler("SerialListHandler",               app.SerialListHandler,              app);
app.RegisterEventHandler("SetWorkingPortHandler",           app.SetWorkingPortHandler,          app);
app.RegisterEventHandler("GetNodeListHandler",              app.GetNodeListHandler,             app);
app.RegisterEventHandler("GetRemoteNodeInfoHandler",        app.GetRemoteNodeInfoHandler,       app);
app.RegisterEventHandler("GetRemoteNodeDataHandler",        app.GetRemoteNodeDataHandler,       app);
app.RegisterEventHandler("SetRemoteNodeDataHandler",        app.SetRemoteNodeDataHandler,       app);
app.RegisterEventHandler("GetDeviceTypeHandler",            app.GetDeviceTypeHandler,           app);
app.RegisterEventHandler("GetDeviceAdditionalHandler",      app.GetDeviceAdditionalHandler,     app);
app.RegisterEventHandler("SetNodeAddressHandler",           app.SetNodeAddressHandler,          app);
app.RegisterEventHandler("GetNodeAddressHandler",           app.GetNodeAddressHandler,          app);
app.RegisterEventHandler("GetNodeInfoHandler",              app.GetNodeInfoHandler,             app);
app.RegisterEventHandler("GetNodesMapHandler",              app.GetNodesMapHandler,             app);
app.RegisterEventHandler("AddNodeIndexHandler",             app.AddNodeIndexHandler,            app);
app.RegisterEventHandler("DelNodeIndexHandler",             app.DelNodeIndexHandler,            app);
app.RegisterEventHandler("SetRemoteNodeAddressHandler",     app.SetRemoteNodeAddressHandler,    app);
app.RegisterEventHandler("GetRemoteNodeAddressHandler",     app.GetRemoteNodeAddressHandler,    app);
app.RegisterEventHandler("USBDeviceConnectedHandler",       app.USBDeviceConnectedHandler,      app);
app.RegisterEventHandler("USBDeviceDisconnectedHandler",    app.USBDeviceDisconnectedHandler,   app);

app.Connect(global_ip, global_port, function() {});

feather.replace();