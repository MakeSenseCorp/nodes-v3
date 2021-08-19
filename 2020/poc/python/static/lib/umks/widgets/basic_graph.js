function MksBasicGraph (name) {
	self 					= this;
	this.API 				= null;
    this.Name               = name
	
	this.BasicContainer = `
        <div id="id-basic-graph-container-`+name+`">
            <canvas id="id-basic-graph-`+name+`"></canvas>
        </div>
	`;

    this.Colors = {
        red: 'rgb(255, 99, 132)',
        orange: 'rgb(255, 159, 64)',
        yellow: 'rgb(255, 205, 86)',
        green: 'rgb(75, 192, 192)',
        blue: 'rgb(54, 162, 235)',
        purple: 'rgb(153, 102, 255)',
        grey: 'rgb(201, 203, 207)'
    };

    this.Config = {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            title: {
                display: false,
                text: ''
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: false,
                    scaleLabel: {
                        display: true,
                        labelString: ''
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: ''
                    }
                }]
            }
        }
    };
    this.Instance = null;
	
	return this;
}

MksBasicGraph.prototype.CleanConfigure = function () {
    this.Config.data.labels     = [];
    this.Config.data.datasets   = [];
}

MksBasicGraph.prototype.Configure = function (conf) {
    this.Config.type                                            = conf.type;
    this.Config.options.title.text                              = conf.title;
    this.Config.options.scales.xAxes[0].scaleLabel.labelString  = conf.x.title;
    this.Config.options.scales.yAxes[0].scaleLabel.labelString  = conf.y.title;
}

MksBasicGraph.prototype.AddDataSet = function(data) {
    if (data.x == undefined || data.y == undefined) {
        return;
    }

    if (data.x.length == 0 || data.y.length == 0) {
        return;
    }

    var dataSet = {
        label: data.title,
        fill: false,
        backgroundColor: data.bk_color,
        borderColor: data.color,
        data: data.y,
        pointRadius: 0
    }
    if (data.dashed) {
        dataSet.borderDash = [5, 5];
    }
    this.Config.data.labels = data.x;
    this.Config.data.datasets.push(dataSet);
}

MksBasicGraph.prototype.RemoveDataSet = function(name) {
    for (key in this.Config.data.datasets) {
        if (this.Config.data.datasets[key] == name) {
            // Remove item
        }
    }
}

MksBasicGraph.prototype.Build = function (obj) {
    if (this.Instance !== undefined && this.Instance !== null) {
        this.Instance.destroy();
    }

    obj.innerHTML = this.BasicContainer;
    
    var Ctx         = document.getElementById("id-basic-graph-"+this.Name).getContext('2d');
    this.Instance   = new Chart(Ctx, this.Config);
}

MksBasicGraph.prototype.Update = function (data) {
    if (this.Instance === null) {
        return;
    }

    var objContainer = document.getElementById("id-basic-graph-container-"+this.Name);
    var objGraph     = document.getElementById("id-basic-graph-"+this.Name);
}

MksBasicGraph.prototype.Rebuild = function () {
    if (this.Instance === null) {
        return;
    }

    if (this.Instance !== undefined) {
        this.Instance.destroy();
    }

    var objContainer = document.getElementById("id-basic-graph-container-"+this.Name);
    var objGraph     = document.getElementById("id-basic-graph-"+this.Name);
}

MksBasicGraph.prototype.Show = function () {
    document.getElementById("id-basic-graph-container-"+this.Name).classList.remove("d-none");
}

MksBasicGraph.prototype.Hide = function () {
    document.getElementById("id-basic-graph-container-"+this.Name).classList.add("d-none");
}