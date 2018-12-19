$(function () {
    $.get('/graph/{{ search_sentence }}', function (result) {
        var style = [
            {
                selector: 'node[label = "Person"]',
                css: {
                    'background-color': '#6FB1FC',
                    'content': 'data(name)',

                    'text-valign': 'center',
                    'color': 'white',
                    "height": 60,
                    "width": 60,

                    'text-outline-width': 2,
                    'text-outline-color': '#316383',//颜色设置
                    "label": "data(name)"
                }
            },
            {
                selector: 'node[label = "Movie"]',
                css: {
                    'background-color': '#F5A45D',
                    'content': 'data(title)',

                    'text-valign': 'center',
                    'color': 'white',
                    "height": 60,
                    "width": 60,

                    'text-outline-width': 2,
                    'text-outline-color': '#316383',//颜色设置
                    "label": "data(title)"
                }
            },
            {
                selector: 'edge',
                css: {
                    'content': 'data(relationship)',
                    'target-arrow-shape': 'triangle',

                    'curve-style': 'bezier',
                    "label": "data(relationship)",
                    'target-arrow-color': 'black',
                    'line-color': '#ccc',
                    'width': 1
                }
            },
            {
                selector: ':selected',
                css: {
                    'content': 'data(value)',
                    'background-color': 'red',
                    'line-color': 'red',
                    'target-arrow-color': 'red',
                    'source-arrow-color': 'red'
                }
            },
            {
                selector: '.background',
                css: {
                    "text-background-opacity": 1,
                    "text-background-color": "#ccc",
                    "text-background-shape": "roundrectangle",
                    "text-border-color": "#000",
                    "text-border-width": 1,
                    "text-border-opacity": 1
                }
            },
            {
                selector: 'node[label="main"]',
                css: {
                    "background-color": '#d0413e',
                    'text-outline-width': 2,
                    'text-outline-color': '#d0413e',
                }
            },
            {
                selector: '.faded"]',
                css: {
                    'opacity': 0.25,
                    'text-opacity': 0
                }
            },
        ];

        var cy = cytoscape({
                    container: document.getElementById('cy'),
                    boxSelectionEnabled: false,
                    autounselectify: true,
                    style: style,
                    layout: {
                        name: 'cose',
                        fit: true,
                        padding: 30, // the padding on fit
                        startAngle: 4 / 2 * Math.PI, // where nodes start in radians
                        sweep: undefined, // how many radians should be between the first and last node (defaults to full circle)
                        clockwise: true, // whether the layout should go clockwise (true) or counterclockwise/anticlockwise (false)
                        equidistant: false, // whether levels have an equal radial distance betwen them, may cause bounding box overflow
                        minNodeSpacing: 100, // min spacing between outside of nodes (used for radius adjustment)
                    },// 整体布局
                    elements: result.elements //元素 边、点
                });
        cy.on('tap', 'node', {foo: 'bar'}, function (evt) {
            console.log(evt.data.foo); // 'bar'
            var node = evt.cyTarget;
            console.log('tapped ' + JSON.stringify(node.data()))
            alert(JSON.stringify(node.data()))
        });

        var layout = cy.layout({
            name: 'concentric',
            fit: true,
            padding: 30, // the padding on fit
            startAngle: 4 / 2 * Math.PI, // where nodes start in radians
            sweep: undefined, // how many radians should be between the first and last node (defaults to full circle)
            clockwise: true, // whether the layout should go clockwise (true) or counterclockwise/anticlockwise (false)
            equidistant: false, // whether levels have an equal radial distance betwen them, may cause bounding box overflow
            minNodeSpacing: 100 // min spacing between outside of nodes (used for radius adjustment)
        });

        layout.run();
    }, 'json');
});

