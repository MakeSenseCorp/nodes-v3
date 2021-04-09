function NodeUI(api) {
    this.API = api;
    window.Modal = new MksBasicModal("GLOBAL");

    return this;
}

NodeUI.prototype.CleanActiveNavigation = function() {
    document.getElementById("id_m_main_dashboard").classList.remove("active");
    document.getElementById("id_m_main_stocks").classList.remove("active");
    document.getElementById("id_m_main_portfolio").classList.remove("active");
    document.getElementById("id_m_main_import").classList.remove("active");
    document.getElementById("id_m_main_export").classList.remove("active");
    document.getElementById("id_m_main_settings").classList.remove("active");
}

NodeUI.prototype.ViewDashboard = function() {
    window.DashboardView.Build(null, function(module) {
    });
    this.CleanActiveNavigation();
    document.getElementById("id_m_main_dashboard").classList.add("active");
}

NodeUI.prototype.OpenModalAppendNewStock = function() {
    window.StockAppend.Build(null, function(module) {
        window.StockAppend.GetDataBaseStocks();
        window.StockAppend.GetPortfolioList();
    });
    this.CleanActiveNavigation();
    document.getElementById("id_m_main_stocks").classList.add("active");
}

NodeUI.prototype.OpenModalPortfolio = function() {
    window.Portfolio.Build(null, function(module) {
        window.Portfolio.UpdatePortfolioList()
    });
    this.CleanActiveNavigation();
    document.getElementById("id_m_main_portfolio").classList.add("active");
}

NodeUI.prototype.OpenModalImportStocks = function() {
    window.ImportActions.Build(null, function(module) {
        module.BuildUploader();
    });
    this.CleanActiveNavigation();
    document.getElementById("id_m_main_import").classList.add("active");
}