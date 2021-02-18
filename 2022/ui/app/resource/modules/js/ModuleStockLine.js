function StockLine() {
    self = this;

    this.Middle = `
        <div class="progress-bar bg-transparent" role="progressbar" style="width: [LEFT]%"></div>
        <div class="progress-bar bg-info" data-toggle="tooltip" title="[TOOLTIP_PRICE]" role="progressbar" style="width: [PRICE_HIST_LEFT]%" aria-valuemin="0" aria-valuemax="100"></div>
        <div class="progress-bar bg-warning" role="progressbar" style="width: [PRICE]%" aria-valuemin="0" aria-valuemax="100"></div>
        <div class="progress-bar bg-info" data-toggle="tooltip" title="[TOOLTIP_PRICE]" role="progressbar" style="width: [PRICE_HIST_RIGHT]%" aria-valuemin="0" aria-valuemax="100"></div>
        <div class="progress-bar bg-transparent" role="progressbar" style="width: [RIGHT]%"></div>
    `;

    this.Right = `
        <div class="progress-bar bg-transparent" role="progressbar" style="width: [LEFT]%"></div>
        <div class="progress-bar bg-info" data-toggle="tooltip" title="[TOOLTIP_PRICE]" role="progressbar" style="width: [PRICE_HIST]%" aria-valuemin="0" aria-valuemax="100"></div>
        <div class="progress-bar bg-transparent" role="progressbar" style="width: [DELIMITER]%"></div>
        <div class="progress-bar bg-success" role="progressbar" style="width: [PRICE]%" aria-valuemin="0" aria-valuemax="100"></div>
        <div class="progress-bar bg-transparent" role="progressbar" style="width: [RIGHT]%"></div>
    `;

    this.Left = `
        <div class="progress-bar bg-transparent" role="progressbar" style="width: [LEFT]%"></div>
        <div class="progress-bar bg-danger" role="progressbar" style="width: [PRICE]%" aria-valuemin="0" aria-valuemax="100"></div>
        <div class="progress-bar bg-transparent" role="progressbar" style="width: [DELIMITER]%"></div>
        <div class="progress-bar bg-info" data-toggle="tooltip" title="[TOOLTIP_PRICE]" role="progressbar" style="width: [PRICE_HIST]%" aria-valuemin="0" aria-valuemax="100"></div>
        <div class="progress-bar bg-transparent" role="progressbar" style="width: [RIGHT]%"></div>
    `;

    return this;
}

StockLine.prototype.Build = function(data, callback=null) {
    var html = "";

    if (data.min < data.price && data.max > data.price) {
        // MIDDLE
        html = this.Middle;
        html = html.split("[LEFT]").join(10);
        html = html.split("[RIGHT]").join(10);
        html = html.split("[PRICE]").join(5);
        html = html.split("[PRICE_HIST_LEFT]").join(37.5);
        html = html.split("[PRICE_HIST_RIGHT]").join(37.5);
        html = html.split("[TOOLTIP_PRICE]").join(data.min + " - " + data.max);
    } else if (data.min > data.price) {
        // LEFT
        html = this.Left;
        html = html.split("[LEFT]").join(10);
        html = html.split("[RIGHT]").join(10);
        html = html.split("[DELIMITER]").join(10);
        html = html.split("[PRICE]").join(5);
        html = html.split("[PRICE_HIST]").join(65);
        html = html.split("[TOOLTIP_PRICE]").join(data.min + " - " + data.max);
    } else if (data.max < data.price) {
        // RIGHT
        html = this.Right;
        html = html.split("[LEFT]").join(10);
        html = html.split("[RIGHT]").join(10);
        html = html.split("[DELIMITER]").join(10);
        html = html.split("[PRICE]").join(5);
        html = html.split("[PRICE_HIST]").join(65);
        html = html.split("[TOOLTIP_PRICE]").join(data.min + " - " + data.max);
    } else  {

    }
    return html;
}

StockLine.prototype.Hide = function() {
    var self = this;
}

StockLine.prototype.Show = function() {
    var self = this;
}