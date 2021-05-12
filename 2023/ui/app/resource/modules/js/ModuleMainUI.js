function NodeUI(api) {
    this.API = api;
    window.Modal = new MksBasicModal("GLOBAL");

    return this;
}

NodeUI.prototype.CleanActiveNavigation = function() {
    document.getElementById("id_m_main_funder_dashboard").classList.remove("active");
    document.getElementById("id_m_main_funder_settings").classList.remove("active");
}

NodeUI.prototype.BindDashboardView = function() {
    window.DashboardView.Build(null, function(module) {
        module.GetAllFunds();
    });
    this.CleanActiveNavigation();
    document.getElementById("id_m_main_funder_dashboard").classList.add("active");
}

NodeUI.prototype.BindSettingsView = function() {
    window.SettingsView.Build(null, function(module) {
    });
    this.CleanActiveNavigation();
    document.getElementById("id_m_main_funder_settings").classList.add("active");
}
